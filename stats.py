import board
import busio
import time
import statsd

from adafruit_htu21d import HTU21D
from datetime import datetime

sensor = HTU21D(busio.I2C(board.SCL, board.SDA))

def read_temperature():
    return (sensor.temperature * 1.8) + 32

statsd.Connection.set_defaults(host='svalbard', port=8125)

temp_gauge = statsd.Gauge('beercloset')
humidity_gauge = statsd.Gauge('beercloset')

while True:
    try:
        temp = read_temperature()
        humid = sensor.relative_humidity
        print("temperature: " + str(temp))
        print("rh: " + str(humid))
        temp_gauge.send('temperature', temp)
        humidity_gauge.send('humidity', humid)
        time.sleep(60*5)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        time.sleep(10)
        
