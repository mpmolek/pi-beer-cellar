import board
import busio
import time

from adafruit_htu21d import HTU21D
from py_irsend import irsend

SET_TEMP = 20 # 68 *F

# current temp must deviate by this much before AC will engage
THRESHOLD = 1.25 #2.25 *F

# wait at least this long between AC triggers
COMPRESSOR_DELAY_SECONDS = 30 * 60 # 30 minutes

sensor = HTU21D(busio.I2C(board.SCL, board.SDA))

def read_temperature():
    return sensor.temperature

def read_humidity():
    return sensor.humidity

def now():
    return time.time()

def send_power_command():
    irsend.send_once('ac', ['KEY_POWER'])

def main():
    # assume current state is off
    currently_cooling = False
    
    # set last cool time to now 
    # so we wait COMPRESSOR_DELAY_SECONDS before doing anythin
    last_cool_time_secs = now()

    while True:
        current_temp = read_tempearture()
        if current_temp > SET_TEMP + THRESHOLD and not currently_cooling:
            #if it's too hot
            if now() >= last_cool_time_secs + COMPRESSOR_DELAY_SECONDS:
                #and we haven't run for at least COMPRESSOR_DELAY_SECONDS
                #start cooling
                send_power_command()
                last_cool_time_secs = now()
                currently_cooling = True
            else:
                sleep_until = last_cool_time_secs + COMPRESSOR_DELAY_SECONDS
                sleep_duration = int(round(sleep_until - now())
                sleep(sleep_duration)
        elif current_temp < SET_TEMP - THRESHOLD:




            

