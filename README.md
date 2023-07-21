<h1>Audio Processing Lab</h1>
<h2>Description</h2>
In this lab, I have <br />

<h2>Languages and Environments Used</h2>

- <b>Python</b> 
- <b>VS code</b>

<h2>Program walk-through</h2>

<p align="left">
Create BACKWARDS function:<br/>

This functions computes the reversed version of the original mono sound. The output is a new mono sound dictionary. 
<img src= "https://imgur.com/J6JxCwa.png" height="50%" width="50%"/>

<br />
<p align="left">
Create MIX function:<br/>

This function mixes 2 sounds with same 'rate', and returns a new sound = p*'samples' in sound1 + (1-p)*'samples' in sound2 where p i the mixing parameter, else None if the rates are different. <br/>

<img src= "https://imgur.com/Q02iEr7.png" height="50%" width="50%"/>

<br />
<p align="left">
Create MIX SAMPLES function:<br/>

This function computes the mixing of sample for the mix function and returns a mix_sample list. <br/>

<img src= "https://imgur.com/dhzht8g.png" height="40%" width="40%"/>


<br />
<p align="left">
Create FILTER functions:<br/>

It is important to note that none of these functions should modify the input sound <br/>
1. Convolve - applies a filter to a sound, resulting in a new sound that is longer than the original mono sound by the (kernel length - 1). <br />

<img src= "https://imgur.com/1SkIeak.png" height="50%" width="50%"/>
<br />
2. Echo - outputs a new mono sound after applying the echo effect by computing a new signal consisting of several scaled-down and delayed versions of the input.<br />

<img src= "https://imgur.com/vgN4Hfs.png" height="40%" width="40%"/>
<br />
3. Pan - creates a neat spatial effect. <br />

<img src= "https://imgur.com/dQupaSx.png" height="50%" width="50%"/>
<br />
4. Vocal elimination - removes vocals from sound. <br />

<img src= "https://imgur.com/4eyvVE9.png" height="50%" width="50%"/>
<br />
