---
title: low power wireless devices
---
Or how do you make that Arduino run on a tiny battery for a year.
Aka, gosh, that solar cell is much weaker than I thought ...

## Don't use wifi
Yeah sure, the `ESP32` and its brothers are a lot of fun and so super convenient to put a project on the net ...

![such esp]({{ site.baseurl }}/uploads/sens/2p7ihv.jpg)

But truth is, wifi has never been designed for low power operation.
These chips take a long time to wake up from sleep, boot an operating system, initialize and calibrate the wifi hardware, authenticate and connect to the network, get an IP address before they're finally ready to get the payload sent.
There's some special sleep options to stay half-way connected and skip some of these steps, but then you cannot fully power down the micro-controller.

## Back to the basics: nRF24
I've been playing with a bunch of [nRF24L01+](https://www.sparkfun.com/datasheets/Components/SMD/nRF24L01Pluss_Preliminary_Product_Specification_v1_0.pdf) modules scattered around my home. These are very cheap (like < 2 $), mass produced RF modems.
Combined with the trusty old atmega328 (= Arduino nano) they make a very nice low power sensor platform.

Here's an example module running from a tiny solar cell and storing enough charge in it's 2.5 F, 4.6 V `ultra cap` to run through the night.

![sens_1]({{ site.baseurl }}/uploads/sens/sens_1.jpg)

Communication happens through the `base station`, which is just a raspberry pi with another nRF module strapped on top of it.

```mermaid
graph TD
subgraph base station
   A[raspberry pi] -- SPI --- B
   A -- mqtt --- C
   B(fa:fa-broadcast-tower nRF24)
   C(fa:fa-wifi wifi)
end
subgraph humidity sensor
  D[arduino]
  E[solar cell]
  F[battery]
  G("fa:fa-broadcast-tower nRF24")
  D --- E
  D --- F
  D -- SPI --- G
end
```

## How low can you go
How much is low power ... well let's have a look ...

The solar cell, in full sun light provides ~ 5 mA at 4 V. That's only ... mW.

The 2 `ultra` caps are wires in series to form a 2.5 F 4.3 V max. capacitor. The stored energy is ... mJ.
That's the equivalent of a 5 maH battery. So really not very much.

## In practice
Here's a diagram of operation for a cloudy day. To charge up it needs a few minutes in bright sunlight. Dim sunlight doesn't do much. It's an all or nothing deal. But once it gets these few minutes once a day, it is enough to last 24 h. Doing a measurement of humidity and temperature every minute.

## Hardware mods
The power LED and voltage regulator need to go to reduce the standby current. The Schottky diode needs to be put in a different place.

## Software tricks
  * Shut everything down as often as possible
  * Use the watchdog timer to wake up again
  * Going to sleep / waking up is fast, so do it often! Sometimes it's even worth to sleep a few miliseconds between pwm cycles
  * To make wakeup faster, don't use the external crystal as a clock source. Use the internal RC oscillator! It wakes up much faster (citation needed)



<script src="{{ site.baseurl }}/uploads/mermaid.min.js"></script>
<script>
    mermaid.initialize({
        startOnLoad: true,
        theme: 'dark',
        flowchart: {
            curve: 'basis',
            useMaxWidth: true,
            htmlLabels: true
        }
    });
    window.mermaid.init(
        undefined, 
        document.querySelectorAll('.language-mermaid')
    );
</script>
