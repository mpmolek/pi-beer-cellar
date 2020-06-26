import board
import busio
import time
import sys
import statsd

from adafruit_htu21d import HTU21D
from datetime import datetime

sensor = HTU21D(busio.I2C(board.SCL, board.SDA))

statsd.Connection.set_defaults(host='svalbard', port=8125)

temp_gauge = statsd.Gauge('beercloset')
humidity_gauge = statsd.Gauge('beercloset')

def read_temperature(attempt):
    # Convert C to F
    try:
        temp = (sensor.temperature * 1.8) + 32
        if temp < 50 or temp > 85:
             print(now_str() + ": bad sensor data. read temp as " + str(temp))
             raise ValueError(temp) 
        return temp
    except Exception as e:
        print("temp exception: " + repr(e))
        if attempt > 5:
            raise
        time.sleep(1)
        return read_temperature(attempt + 1)

def tick():
    temp = read_temperature(0)
    temp_gauge.send('temperature', temp)
    print("temperature: " + str(temp))
    humid = sensor.relative_humidity
    humidity_gauge.send('humidity', humid)
    print("rh: " + str(humid))


print()
my_date = datetime.now()
print(my_date.isoformat())
try:
    tick()
except:
        print("Unexpected error:", sys.exc_info()[0])
        time.sleep(5)
        #try again, errors here are usually transient
        tick()
        
