'''Module for interfacing with SGP30 chip over i2c on Raspberry Pi'''

import smbus
import struct
import statistics
from time import sleep

channel = 1
address = 0x58

bus = smbus.SMBus(channel)

def getSerial():
    '''Get the serial number of the attached SGP sensor

    Returns:
        serial (:obj:`list`): Three member list with the serial number of
            the attached SGP30
    '''
    cmd = [0x36, 0x82]

    cmd_byte = cmd[0]
    arg_bytes = list(cmd[1:])

    bus.write_i2c_block_data(address, cmd_byte, arg_bytes)
    sleep(0.1)
    resp = bus.read_i2c_block_data(address, 0, 3*3)

    data = bytearray(resp)

    serial = []
    for i in range(0, 9, 3):
        b, crs = struct.unpack_from(">HB", data, offset=i)
        if crc(resp[i:i+2]) != crs:
            print("Checksum error")
            return False

        serial.append(b)

    return serial


def initSensor():
    '''Initialises the SGP30 sensor

    Will start an approx. 15s run of measurements while the sensor initialises.
    When the warm-up process completes, "Ready" will be printed to the terminal
    '''
    cmd = [0x20, 0x03]

    cmd_byte = cmd[0]
    arg_bytes = list(cmd[1:])
    bus.write_i2c_block_data(address, cmd_byte, arg_bytes)
    sleep(0.01)

    msg = "Warming up [" + (" "*19) + "]"
    print(msg, end="\r" , flush=True)
    for i in range(20):
        getMeasurement()
        msg = "Warming up [" + ("#"*i)
        print(msg, end="\r", flush=True)
        sleep(1)

    print("\nReady")


class Measurement():
    '''SGP30 measurement object

    Attributes:
        CO2 (:obj:`int`): Measured eCO2 concentration in ppm. In the event of
            CRC checksum error, will be False
        VOC (:obj:`int`): Measured TVOC concentration in ppb. In the event of
            CRC checksum error, will be False
        warmup (:obj:`bool`): True if CO2 == 400 and VOC == 0, which are the 
            default values during warm-up. Used by the sensor initialisation
            routine to ignore warm-up values.
    '''
    def __init__(self, data):
        '''Initialisation of Measurement object 

        Parameters:
            data (:obj:`list`): 6-item list of hexadecimal values representing 
                the bytes returned by the sensor. The first two bytes form the
                eCO2 value, and the third is the CRC checksum of those bytes,
                The fourth and fifth bytes form the TVOC value and the sixth
                is the CRC checksum of those bytes.
        '''

        # Convert the values to a byte array
        byteData = bytearray(data)

        # Unpack the byte array into an unsigned short and unsigned char 
        # (big endian bytes)
        CO2, csum1 = struct.unpack_from(">HB", byteData, offset=0)
        VOC, csum2 = struct.unpack_from(">HB", byteData, offset=3)

        self.CO2 = CO2
        self.VOC = VOC

        # Check the CRC on the data
        if crc(data[0:2]) != csum1:
            self.CO2 = False

        if crc(data[3:5]) != csum2:
            self.VOC = False

        # Check the value to see if it might be from the warm-up of the sensor
        self.warmup = False

        if CO2 == 400 and VOC == 0:
            self.warmup = True


def getMeasurement():
    ''' Gets a single measurement from the sensor

    Returns:
        measurement (:obj:`sgp30.Measurement`): An SGP30 measurement object
    '''
    cmd = [0x20, 0x08]

    cmd_byte = cmd[0]
    arg_bytes = list(cmd[1:])

    bus.write_i2c_block_data(address, cmd_byte, arg_bytes)
    sleep(0.12)
    resp = bus.read_i2c_block_data(address, 0, 6)

    return Measurement(resp)


def getRawMeasurement():
    ''' Gets the raw measurement data from the sensor

    For details on how these values work, see the SGP30 chip specification
    sheet

    Returns:
        H2 (:obj:`int`): Raw sensor hydrogen value (see SGP specs)
        EtOH (:obj:`int`): Raw sensor ethanol value (see SGP specs)
    '''
    cmd = [0x20, 0x50]

    cmd_byte = cmd[0]
    arg_bytes = list(cmd[1:])

    bus.write_i2c_block_data(address, cmd_byte, arg_bytes)
    sleep(0.25)
    resp = bus.read_i2c_block_data(address, 0, 6)

    data = bytearray(resp)

    H2, csum1 = struct.unpack_from(">HB", data, offset=0)
    EtOH, csum2 = struct.unpack_from(">HB", data, offset=3)

    return H2, EtOH


def crc(data):
    '''CRC8 algorithm

    Implements a CRC8 algorithm like that used by the SGP30 chip 
    (initialisation = 0xFF, polynomial = 0x31)

    Parameters:
        data (:obj:`list`): List of byte values the be checked

    '''
    init = 0xFF
    polynomial = 0x31
    crc = init

    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
    return crc & 0xFF

