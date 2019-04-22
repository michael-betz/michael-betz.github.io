---
title: Si570 phase noise
---
The Si570 is a single-chip I2C programmable frequency synthesizer. It is often used to generate sampling clocks for ADCs, DACs or to drive FPGA logic. It is possible to get the chip on an evaluation board, powered and programmable over USB (`Si5xx-PROG_EVB`). This board has been super handy to have around the lab and I've used it on many occasions to generate clocks or test signals for prototypes.

I've [re-written the firmware](https://github.com/yetifrisstlama/Si5xx-5x7-EVV_autoloader) such that it enumerates as UART and wrote a python app to set the frequency, avoiding the need for the kludgy windows-only silicon labs driver. Also I've added a persistence feature, such that it restores the last set frequency on power up.

Here's a phase noise measurement at $f_/mathrm{out}$ = 500 MHz, in comparison to 2 high-end RF signal generators:

  * [HP8644b](https://www.keysight.com/en/pd-1000002189%3Aepsg%3Apro-pn-8644B/high-performance-signal-generator-1-ghz-or-2-ghz?cc=US&lc=eng)
  * [HS9001A](http://www.holzworth.com/Spec_sheets/HS9000_Web_Datasheet.pdf)
  * [Si570](https://www.silabs.com/documents/public/data-sheets/si570.pdf)

Integrated jitter (from 1 Hz to 10 MHz) is shown in the legend on the top right.

![Si570 phase noise at 500 MHz]({{ site.baseurl }}/uploads/si570_pn.png)

The measurements were done on a R&S FSWP signal source analyzer.

## In conclusion
the `Si570` is 58 times as noisy as the `HS9001A` RF synthesizer from Holzworth. However it is also 1233 times cheaper!
