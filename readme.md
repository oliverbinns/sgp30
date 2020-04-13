# SPG30

Oliver Binns, 2020

This is a python module for reading SPG30 gas sensor values on Raspberry Pi. 

The SGP30 is a multi-gas sensor produced by Sensiron, which communicates by the i2c protocol. This module has been tested on the board produced by [Adafruit][2]. The code is base don the details in the specsheet, [here][1].

## Installation

Enable i2c communcation on the Raspberry Pi using the `raspi-config` utility. Ensure that you have installed python 3 and the `smbus` utility:

    sudo apt install ipython3 python3-pip python3-smbus

Then, install the sgp30 module with pip.

## Usage

To ininitialise the sensor, use:

    import sgp30
    sgp30.initSensor()

This will call the initialisation of the sensore and trigger an approx. 15 second run of warm-up measurements. These measurements will not be recorded. After the warm-up, to take a measurement, use:

    measurement = sgp30.getMeasurement()

This will return a `sgp.Measurement` object. The measurement object will have the attributes `measurement.CO2` and `measurement.VOC`. If the CRC checksum returned by the chip for either of the measurements failed, the respective attribute will be returned as `False` 

The SGP [specsheet][1] recommends taking a reading every 1s. Use the `time.sleep(1)` to delay the time between measurements.


[1]: https://www.sensirion.com/en/environmental-sensors/gas-sensors/multi-pixel-gas-sensors/

[2]: https://www.adafruit.com/product/3709