"""
6.1010 Spring '23 Lab 0: Audio Processing
"""

import wave
import struct

# No additional imports allowed!


def backwards(sound):
    """
    Compute a new mono sound which is the reversed version of the original mono sound
     Args:
        sound: A mono sound dictionary with two key/value pairs:
            * "rate": an int representing the sampling rate, samples per second
            * "samples": a list of floats containing the sampled values

    Returns:
        A new mono sound dictionary.
    """
    new_samples = sound["samples"][::-1]  # list of samples in reverse
    new_sound = {}  # new dict
    new_sound["rate"] = sound["rate"]
    new_sound["samples"] = new_samples
    return new_sound


def mix(sound1, sound2, p):
    """
    Mixes 2 sounds
    Args:
        sound1: dict with same 'rate' as sound2
        sound2: dict with same 'rate' as sound1
        p: mixing parameter
    Returns:
        A new sound which is p*'samples' in sound1 + (1-p)*'samples' in sound2.
        Return None if diff rate
    """
    # mix 2 good sounds
    if not (
        "rate" in sound1.keys()
        and "rate" in sound2.keys()
        and sound1["rate"] == sound2["rate"]
    ):
        return

    r = sound1["rate"]  # get rate
    if len(sound1) == 2 and len(sound2) == 2:
        sound1 = sound1["samples"]
        sound2 = sound2["samples"]
        sound_len=min(len(sound1),len(sound2))
        
        mix_sample_mono = mixsample(sound1,sound2,p)
       
        return {"rate": r, "samples": mix_sample_mono}  # return new sound

    if len(sound1) == 3 and len(sound2) == 3:
        sound1_lft = sound1["left"]
        sound2_lft = sound2["left"]
        mix_sample_lft = mixsample(sound1_lft,sound2_lft,p)

        sound1_rt = sound1["right"]
        sound2_rt = sound2["right"]
        mix_sample_rt = mixsample(sound1_rt,sound2_rt,p)
        
        return {"rate": r, "left": mix_sample_lft, "right": mix_sample_rt}

def mixsample(sound1,sound2,p):
    """
    Computes mixing of sample for mix fn
    Args:
        sound1: dict
        sound2: dict
    Return:
        mix_sample: list
    """
    sound_len=min(len(sound1),len(sound2))
    mix_sample = []
    x = 0
    while x <= sound_len:
        s2, s1 = p * sound1[x], sound2[x] * (1 - p)
        mix_sample.append(s1 + s2)  # add sounds
        x += 1
        if x == sound_len:  # end
            break
    return mix_sample

def convolve(sound, kernel):
    """
    Applies a filter to a sound, resulting in a new sound that is longer than
    the original mono sound by the length of the kernel - 1.
    Does not modify inputs.

    Args:
        sound: A mono sound dictionary with two key/value pairs:
            * "rate": an int representing the sampling rate, samples per second
            * "samples": a list of floats containing the sampled values
        kernel: A list of numbers

    Returns:
        A new mono sound dictionary.
    """
    samples = [0]  # a list of scaled sample lists

    result_len = len(sound["samples"]) + len(kernel) - 1
    samples *= result_len  # list of 0's

    for shift, scale in enumerate(kernel):  # gives index and num
        if scale != 0:
            for i, num in enumerate(sound["samples"]):
                scale_sample = num * scale
                samples[i + shift] += scale_sample  # add as you go, no list in btwn

    convolve_sound = {}  # new dict
    convolve_sound["rate"] = sound["rate"]
    convolve_sound["samples"] = samples

    return convolve_sound

    

def echo(sound, num_echoes, delay, scale):
    """
    Compute a new signal consisting of several scaled-down and delayed versions
    of the input sound. Does not modify input sound.

    Args:
        sound: a dictionary representing the original mono sound
        num_echoes: int, the number of additional copies of the sound to add
        delay: float, the amount of seconds each echo should be delayed
        scale: float, the amount by which each echo's samples should be scaled

    Returns:
        A new mono sound dictionary resulting from applying the echo effect.
    """
    # echo_filter = [0] * (sample_delay * num_echoes) #list of 0's of new len
    sample_delay = round(delay * sound["rate"])  # num of samples

    # make kernel
    zero_lst = [0] * (sample_delay - 1)
    scale_lst = []

    for i in range(num_echoes + 1):
        scale_lst.extend([scale**i])  # match scale to indx
        if i != num_echoes:  # no 0's at end
            scale_lst.extend(zero_lst)

    return convolve(sound, scale_lst)

    

def pan(sound):
    """
    Create a really neat spatial effect
    Args:
        sound: dict with keys 'rate','lft','rght'
    Returns:
        new list with scaled values
    """

    sound_lft = sound["left"][:]
    sound_rt = sound["right"][:]
    len_dp_sound = len(sound_lft)  # same len
    # print(len_dp_sound)
    adj_samples = {}
    adj_samples["rate"] = sound["rate"]
    adj_lft = []
    adj_rt = []

    for i in range(len_dp_sound):
        if i == 0:  # index = 0
            adj_lft.append(sound_lft[0])
            adj_rt.append(0)
        elif i == len_dp_sound - 1:  # last indx
            adj_rt.append(sound_rt[len_dp_sound - 1])
            adj_lft.append(0)
        else:  # scale
            adj_rt.append(sound_rt[i] * (i / (len_dp_sound - 1)))  # added ()
            adj_lft.append(sound_lft[i] * ((1 - (i / (len_dp_sound - 1)))))

    adj_samples["left"] = adj_lft
    adj_samples["right"] = adj_rt

    return adj_samples


def remove_vocals(sound):
    """
    Remove vocals from sound
    Args:
        sound: stero
    Returns:
        new sound: mono
    """
    sound_lft = sound["left"][:]  # list copy
    sound_rt = sound["right"][:]
    rem_sound = {}  # new dict
    rem_sound["rate"] = sound["rate"]
    rem_lst = []

    for i,j in enumerate(sound_lft):  # calc diff
        rem_lst.extend([j - sound_rt[i]])  # must be list to extend

    rem_sound["samples"] = rem_lst

    return rem_sound


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def bass_boost_kernel(boost, scale=0):
    """
    Constructs a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ N

    Then we scale that piece up and add a copy of the original signal back in.

    Args:
        boost: an int that controls the frequencies that are boosted (0 will
            boost all frequencies roughly equally, and larger values allow more
            focus on the lowest frequencies in the input sound).
        scale: a float, default value of 0 means no boosting at all, and larger
            values boost the low-frequency content more);

    Returns:
        A list of floats representing a bass boost kernel.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    kernel = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    for i in range(boost):
        kernel = convolve(kernel, base["samples"])
    kernel = kernel["samples"]

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel) // 2] += 1

    return kernel


def load_wav(filename, stereo=False):
    """
    Load a file and return a sound dictionary.

    Args:
        filename: string ending in '.wav' representing the sound file
        stereo: bool, by default sound is loaded as mono, if True sound will
            have left and right stereo channels.

    Returns:
        A dictionary representing that sound.
    """
    sound_file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = sound_file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    left = []
    right = []
    for i in range(count):
        frame = sound_file.readframes(1)
        if chan == 2:
            left.append(struct.unpack("<h", frame[:2])[0])
            right.append(struct.unpack("<h", frame[2:])[0])
        else:
            datum = struct.unpack("<h", frame)[0]
            left.append(datum)
            right.append(datum)

    if stereo:
        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = [(ls + rs) / 2 for ls, rs in zip(left, right)]
        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Save sound to filename location in a WAV format.

    Args:
        sound: a mono or stereo sound dictionary
        filename: a string ending in .WAV representing the file location to
            save the sound in
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l_val, r_val in zip(sound["left"], sound["right"]):
            l_val = int(max(-1, min(1, l_val)) * (2**15 - 1))
            r_val = int(max(-1, min(1, r_val)) * (2**15 - 1))
            out.append(l_val)
            out.append(r_val)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    # hello = load_wav("sounds/synth.wav")
    # bye = load_wav("sounds/water.wav")
    # write_wav(mix(hello, bye, 0.2), "synth_water.wav")

    # hello = load_wav("sounds/ice_and_chilli.wav")
    # write_wav(convolve(hello,bass_boost_kernel(1000,1.5)), "bb_ice_and_chilli.wav")

    # hello = load_wav("sounds/chord.wav")
    # write_wav(echo(hello, 5, 0.3, 0.6), "echoe_chord.wav")

    # hello = load_wav("sounds/car.wav",stereo=True)
    # write_wav(pan(hello), "pan_car.wav")

    # hello = load_wav("sounds/lookout_mountain.wav", stereo=True)
    # write_wav(remove_vocals(hello), "remove_lookout_mountain.wav")

    hello = load_wav("sounds/synth.wav", stereo=True)
    bye = load_wav("sounds/water.wav", stereo=True)
    write_wav(mix(hello,bye,0.3), "stereo_synth_water.wav")
