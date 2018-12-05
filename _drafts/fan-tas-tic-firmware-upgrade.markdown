---
title: A Fan-Tas-Tic firmware upgrade
---

The idea for the pinball controller was to use [PCF8574](http://www.ti.com/lit/ds/symlink/pcf8574.pdf) I2C port extenders for a majority of the in and outputs.

This makes the system very flexible as multiple in- and output boards can be placed in the machine wherever they are needed. Also boards of different function can coexist on the same bus, e.g., switch inputs, solenoid outputs, servo outputs, led outputs ...

For solenoid outputs a coarse control of power level is needed. For example a solenoid needs to be powered with the full 24 V for a couple of ms to actuate but can then fall back to a fraction of its full power and stay actuated. This is done for all channels by [binary code modulation (bcm)](http://www.batsocks.co.uk/readme/art_bcm_3.htm).

For example, having a `I = 4 bit` word `[b3, b2, b1, b0]` encoding the solenoid intensity and a 1 ms cycle time. Each bit is applied to the output for `2^i` cycles, where `i` is the index of the bit.

![bcd]({{ site.baseurl }}/uploads/fan/bcd.png)

The advantage of using this method as compared to pulse width modulation (PWM) is that it can be implemented much more efficiently for a large number of channels. Let's have a closer look how the firmware achieves that in detail.

## main
The main function starts 3 FreeRTOS tasks, all of which loop forever.
<div class="mermaid">
graph TD;
    A["main()"]
    A-->B["taskDemoLED()"]
    A-->C["task_pcf_io()"]
    A-->D["taskUsbCommandParser()"]
</div>

## taskDemoLED
Right now this justs prints a welcome message to the UART and then blinks the user LED. Also it clears `globalDebugEnabled` after 1 second, which will make all UARTprintf calls return immediately without printing to UART.

<div class="mermaid">
graph LR;
    A[init UART]
    A-->B[print welcome message]
    B-->C[wait 1 s]
    C-->D[globalDebugEnabled = 0]
</div>

## task_pcf_io
This task coordinates everything in- and output related. It uses `vTaskDelayUntil()` to achieve a more or less accurate 1 ms cycle time.

It triggers the I2C state machine, which will carry out all pending I2C transactions in the background, using interrupts. At the same time, the switch matrix is scanned using simple `NOP` delay loops.

When both processes are finished, `process_IO()` is called, which takes care of debouncing all inputs and keeping track of timed outputs and quick-fire rules.

Finally a few pending one-shot I2C transactions are carried out (from the `I2C` command) and the cycle continues.

<div class="mermaid">
graph TD;
    X[Initialize]-->A
    E-->A(wait for I2C to complete all transactions)
    A-->B["process_IO()"]
    B-->Y[do one shot I2C transactions]
    Y-->C(wait to fill up 1 ms cycle)
    C-->D["trigger I2C state machine (interrupts)"]
    D-->E["read switch matrix (bit bang)"]
</div>

## The I2C state machine

<div class="mermaid">
graph TD;
    D[I2C_IDLE]--"trigger by task_pcf_io()"-->A
    A["I2C_START<br> init variables, start first I2C job"]-->B
    B["I2C_PCF<br> get I2C result, increment error counters, start next job"]-->B
    B--"notify task_pcf_io()"-->D
    D--"trigger by task_pcf_io()"-->C["I2C_CUSTOM<br> get result of a one-shot I2C job"]
    C--"notify task_pcf_io()"-->D
</div>

Here's a logic analyzer capture showing 3 of the 4 I2C channels. The lowest trace shows when the I2C interrupt service routine (isr) is active.

![read_all]({{ site.baseurl }}/uploads/fan/read_all.png)

All 4 I2C channels have their own state machine. Once triggered by `task_pcf_io()`, each one iterates through addresses 0x20 - 0x27, which is the range where PCF8574 chips can be configured for. They read or write one byte from each address, depending on each channels flags. If there is no I2C ACK (no PCF chip connected at this address) or another error, an error counter is incremented. The whole process takes a bit less than half a millisecond, after which `task_pcf_io()` is notified.

Entering the command `IL` in the UART console would show this overview:

```
0 1 2
3 4 5 ...
```

meaning.

About 10 seconds after power up all error counters are evaluated. More than 9900 errors means the respective channel will be deactivated an not scanned in the future to save some time. In this case there were only 3 PCF chips connected and the state machine finishes already after 0.15 ms.

![read_ack]({{ site.baseurl }}/uploads/fan/read_ack.png)

The `IL` command in this case would show

```
0 1 2
3 4 5 ...
```

## Dealing with outputs


<script src="https://unpkg.com/mermaid@8.0.0-rc.8/dist/mermaid.min.js"></script>
<script>
    mermaid.initialize({theme: 'dark', flowchart: {curve: 'basis'}});
</script>
