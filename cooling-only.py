import board
import busio
import time

from adafruit_htu21d import HTU21D
from datetime import datetime
from py_irsend import irsend

#SET_TEMP = 20 # 68 *F
SET_TEMP = 19

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

def now_str():
    date_time = datetime.fromtimestamp(now())
    return date_time.strftime("%c")

def print_state():
    print(now_str() + ": current temp is " + str(current_temp))
    print(now_str() + ": currently cooling " + str(currently_cooling))

def send_power_command():
    irsend.send_once('ac', ['KEY_POWER'])

def main():
    # assume current state is off
    currently_cooling = False

    # set last cool time far enough in the past that we can start immediately
    last_cool_time_secs = now() - COMPRESSOR_DELAY_SECONDS
    while True:
        current_temp = read_temperature()
        print(now_str() + ": current temp is " + str(current_temp))
        print(now_str() + ": currently cooling " + str(currently_cooling))
        if not currently_cooling:
            if now() >= last_cool_time_secs + COMPRESSOR_DELAY_SECONDS:
                #and we haven't run for at least COMPRESSOR_DELAY_SECONDS
                #start cooling
                print(now_str() + ": turning on ac")
                send_power_command()
                last_cool_time_secs = now()
                currently_cooling = True
            else:
                sleep_until = last_cool_time_secs + COMPRESSOR_DELAY_SECONDS
                sleep_duration = int(round(sleep_until - now()))
                print(now_str() + ": temp is too warm but waiting " + str(sleep_duration) + " seconds for compressor delay")
                time.sleep(sleep_duration)
                continue
        else:
            if current_temp < SET_TEMP - THRESHOLD:
                print(now_str() + ": too cold. turning off ac.")
                send_power_commend()
                last_cool_time_secs = now() # wait at least half an hour from now before running again
                currently_cooling = False
        print(now_str() + ": sleeping a minute before next loop")
        time.sleep(60)

if __name__ == "__main__":
    # execute only if run as a script
    main()
