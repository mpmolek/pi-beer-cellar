import board
import busio
import time

from adafruit_htu21d import HTU21D
from datetime import datetime

sensor = HTU21D(busio.I2C(board.SCL, board.SDA))

def read_temperature():
    return (sensor.temperature * 1.8) + 32


print(read_temperature())
