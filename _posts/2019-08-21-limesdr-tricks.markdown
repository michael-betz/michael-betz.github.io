---
title: LimeSDR
---
I bought the [LimeSDR mini](https://www.crowdsupply.com/lime-micro/limesdr-mini) some time ago and this is is my experience with it so far ...

## Things I have done

  * 3D printed a [case](https://www.thingiverse.com/thing:2872421). Protects the PCB and sensitive components. However the board gets uncomfortably hot! If I would do it again I would look for something which integrates a small heatsink / fan.
  * Had a bit of a struggle building and installing [Gnuradio 3.8](https://github.com/gnuradio/gnuradio/releases/tag/v3.8.0.0) from source (the latest of the latest) only to realize [it does not support LimeSDR](https://github.com/myriadrf/gr-limesdr/issues/44)
  * Installed `Lime Suite`, `SoapySDR` and [GQRX](http://gqrx.dk/), which is the perfect combination to get started. Here's the order of things to try:
    * `$ LimeQuickTest` should find the device and test it
    * `$ SoapySDRUtil --probe` should also find the LimeSDR and print its capabilities
    * `$ gqrx` should work once the device string is set to `driver=lime,soapy=2`

### Using gqrx
I like its simplicity and usefulness for exploring the radio spectrum.

![fm_radio]({{ site.baseurl }}/uploads/lime/fm_radio.png)
Here's some strong FM radio stations. Listening-in from gqrx is as as simple as clicking on them.

![915MHz]({{ site.baseurl }}/uploads/lime/915MHz.png)
Here's many very short data transmissions around 915 MHz. Most look very similar in the spectrogram. I haven't found out yet what their purpose is or even which radio standard they follow. My goal for now is to discover and decode some LORA transmissions in my area.

I would like to use gqrx as a tuner software, where I can select a center frequency and bandwidth and it exports a live data stream, either as UDP packets or through stdout, for further processing in gnuradio or baudline for example. I figured the demodulated audio stream can be sent over a UDP socket. Selecting `Raw I/Q` as demodulating mode, I can store the I and Q signals as 2 channel .wav file to disk. However the UDP stream only contains the `I` channel and hence discards the negative half of the spectrum. I [forked and patched](https://github.com/yetifrisstlama/gqrx) gqrx to get `Raw I/Q` mode working over UDP.

To get the samples into baudline, I use
```bash
$ nc -6ulp 12345 | baudline -reset -stdin -format le32f -channels 2 -scaleby 32768 -quadrature -flipcomplex
```
where the UDP port is 12345.

### Using [baudline](http://baudline.com/)
it's like a swiss pocket knife for signal processing and analysis. It stores raw samples in a large ring-buffer and operates on them. Analysis-settings like FFT-size or color aperture can be changed after recording without loss of signal. Everything visible in the spectrogram can be manually extracted and demodulated. Also it is blazing fast and has no trouble recording 20 MHz wide IQ data, while visualizing it in a gap-less spectrogram in real-time!

I use the below bash script together with [rx_tools](https://github.com/rxseger/rx_tools) to send complex samples from the LimeSDR through std-input directly to baudline for analysis and capture.

```bash
#!/bin/bash
echo "usage: 5 MHz bandwidth around 500 MHz: $0 500e6 5e6"
F0=$1
BW=$2
rx_sdr -d driver=lime -f $F0 -s $BW -F CS16 \
-a LNAW -g TIA=7,LNA=7,PGA=0 \
-b 32768 - | baudline -tsession lime -record -stdin -format le16 -channels 2 \
-quadrature -flipcomplex -samplerate $BW -basefrequency $F0 -memory 2048
```

save it as `lime_to_baudline.sh`, make it executable and use it as such:

```bash
$ lime_to_baudline.sh 915e6 15e6
```

which will tune to 915 MHz and sample with 15 MHz bandwidth. Tune the 3 gain stages of the SDR by modifying TIA, LNA and PGA in the script.


### Building an Antenna
An [antenna](https://m0ukd.com/calculators/quarter-wave-ground-plane-antenna-calculator/) for 915 MHz to search for LORA signals. It's built from a SMA male connector and some brass wires / tubing. The improved signal level compared to sticking a random wire in the SMA port is remarkable :)

![diploe_915MHz]({{ site.baseurl }}/uploads/lime/diploe_915MHz.jpg)


## Workflow for demodulating signals
  1 Identify which modulation it is. Sometimes obvious due to spectrogram signature (FM-radio) or frequency band (LTE), sometimes not
  2 Get a clean recording with good signal to noise. A specialized antenna, filter, LNA might be required
  3 Down-convert to baseband (IQ signal), filter and decimate. GQRX in Raw I/Q mode seems the most convenient to do this. However its bandwidth is limited to 48 kHz
  4 Start working on de-modulation in gnuradio, blocks might exist already

I wanted to go through these steps for [LORA signals](https://static1.squarespace.com/static/54cecce7e4b054df1848b5f9/t/57489e6e07eaa0105215dc6c/1464376943218/Reversing-Lora-Knight.pdf) as an example. Unfortunately, looking for the characteristic frequency sweeps in the spectrogram, I have not discovered any in my area so far. I'll keep looking and updating this page as I make progress.
