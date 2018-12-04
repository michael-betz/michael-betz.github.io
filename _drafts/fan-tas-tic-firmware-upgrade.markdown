---
title: A Fan-Tas-Tic firmware upgrade
---
The idea for the pinball controller was to use [PCF8574](http://www.ti.com/lit/ds/symlink/pcf8574.pdf) I2C port extenders for a majority of the in and outputs.

This makes the system very flexible as multiple in- and output boards can be placed in the machine wherever they are needed. Also boards of different function can coexist on the same bus, e.g., switch inputs, solenoid outputs, servo outputs, led outputs ...

For solenoid outputs a coarse control of power level is needed. For example the solenoid opening a gate for the ball to pass through needs to be powered with the full 24 V for a couple of ms to actuate but can then fall back to a fraction of its full power to prevent it from overheating. This is done for all channels by binary code modulation (bcm).

For example, having a `I = 4 bit` word `[b3, b2, b1, b0]` encoding the solenoid intensity and a 1 ms cycle time. Each bit is applied to the output for `2^i` cycles, where `i` is the index of the bit.

![bcd]({{ site.baseurl }}/uploads/fan/bcd.png)

The advantage of using this method as compared to pulse width modulation (PWM) is that it can be implemented much more efficiently for a large number of channels.

We count the cycles and when we reach `2^i` we just need to fire a write to set the output ports to value `port_val[i]`. The values to be written at the 4 particular instances are precomputed. We'll need `I * N` bits of memory for `N` outputs.
If we would do classical PWM we would need to store the `I` bit wide pulse width for each output. But only theoretically, as memory on a microcontroller comes at least in 8 bit increments.

![read_all]({{ site.baseurl }}/uploads/fan/read_all.png)

![read_ack]({{ site.baseurl }}/uploads/fan/read_ack.png)

I canput sometexthere and here and bla and then there shouldbeanimage.

![read_ack_2]({{ site.baseurl }}/uploads/fan/read_ack_2.png)
{: .full}

Andther ecanbesomem or etextbelowa nditshould lo oknotott oobad.
