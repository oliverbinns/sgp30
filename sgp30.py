import smbus
import struct
import statistics
from time import sleep

channel = 1
address = 0x58

bus = smbus.SMBus(channel)

def getSerial():
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
    def __init__(self, data):

        byteData = bytearray(data)

        CO2, csum1 = struct.unpack_from(">HB", byteData, offset=0)
        VOC, csum2 = struct.unpack_from(">HB", byteData, offset=3)

        self.CO2 = CO2
        self.VOC = VOC

        if crc(data[0:2]) != csum1:
            self.CO2 = False

        if crc(data[3:5]) != csum2:
            self.VOC = False

        self.warmup = False

        if CO2 == 400 and VOC == 0:
            self.warmup = True


def getMeasurement():
    cmd = [0x20, 0x08]

    cmd_byte = cmd[0]
    arg_bytes = list(cmd[1:])

    bus.write_i2c_block_data(address, cmd_byte, arg_bytes)
    sleep(0.12)
    resp = bus.read_i2c_block_data(address, 0, 6)

    return Measurement(resp)


def loopMeasurement():
    initSensor()

    vals = []
    while(True):
        sleep(1)
        meas = getMeasurement()
        if meas.CO2 is False:
            print("CRC error")
        else:
            vals.append(meas.CO2)
            if(len(vals) == 10):
                mean = statistics.mean(vals)
                print("eCO2 = " + str(mean))
                vals = []


def getRawMeasurement():
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
    init = 0xFF
    polynomial = 0x31
    crc = init
    # calculates 8-Bit checksum with given polynomial
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
    return crc & 0xFF

