import board
import busio
import time

from adafruit_htu21d import HTU21D
from datetime import datetime
from py_irsend import irsend

'''
TODO: If you haven't run in at least 90 minutes then:
- threshold = 0
- min run time doesn't apply
'''

SET_TEMP = 70

# current temp must deviate by this much before AC will engage
THRESHOLD = 0.75 

OVERCOOL = 3.25

# wait at least this long between AC triggers
COMPRESSOR_DELAY_SECONDS = 35 * 60 # 30 minutes

MIN_RUN_TIME_SECONDS = 7 * 60 #10 minutes

sensor = HTU21D(busio.I2C(board.SCL, board.SDA))

def get_run_time():
    current_hour = datetime.now().hour
    #run longer in the afternoon
    if current_hour >= 11 and current_hour <= 18:
        print("Long run time")
        return MIN_RUN_TIME_SECONDS * 2.25
    else:
        print("Short run time")
        return MIN_RUN_TIME_SECONDS

def get_overcool():
    current_hour = datetime.now().hour
    #run longer in the afternoon
    if current_hour >= 11 and current_hour <= 18:
        return OVERCOOL + 0.5
    else:
        return OVERCOOL

def get_threshold():
    current_hour = datetime.now().hour
    #run longer in the afternoon
    if current_hour >= 11 and current_hour <= 18:
        return THRESHOLD
    else:
        return THRESHOLD + 0.75

def get_compressor_delay_seconds():
    #intentionally different than the others
    if current_hour >= 9 and current_hour <= 21:
        return COMPRESSOR_DELAY_SECONDS
    else:
        return COMPRESSOR_DELAY_SECONDS + 15*60 # extra 15 minutes at night



def read_temperature():
    # Convert C to F
    try:
        temp = (sensor.temperature * 1.8) + 32
        if temp < 60 or temp > 80:
             print(now_str() + ": bad sensor data. read temp as " + str(temp))
             raise ValueError(temp) 
        return temp
    except Exception as e:
        print("temp exception: " + repr(e))
        time.sleep(1)
        return read_temperature()

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
    #print("dry run only")
    irsend.send_once('ac', ['KEY_POWER'])

def turn_off(retry_count):
    start_temp = read_temperature()
    print(now_str() + " retry " + str(retry_count) + ". sending power off command. current temp is: " + str(start_temp), flush=True)
    print(now_str() + " waiting for temp to be at least " + str(start_temp + 1.5), flush=True)
    last_cool_time_secs = now() # wait at least half an hour from now before running again
    send_power_command()
    wait_time = 15 * 60
    print(now_str() + " sleeping for 15 minutes to see if the room warms up", flush=True)
    time.sleep(wait_time)
    new_temp = read_temperature()
    if new_temp < start_temp + 1.5:
        print(now_str() + " still too cold, trying to turn off again", flush=True)
        return turn_off(retry_count + 1)
    else:
        print(now_str() + " I think it's really off now, temp is " + str(new_temp), flush=True)
        return last_cool_time_secs
    

def main():
    # assume current state is off
    currently_cooling = False

    # set last cool time far enough in the past that we can start immediately
    last_cool_time_secs = now() #- COMPRESSOR_DELAY_SECONDS
    while True:
        current_temp = read_temperature()
        print(now_str() + ": current temp is " + str(current_temp), flush=True)
        print(now_str() + ": currently cooling " + str(currently_cooling), flush=True)
        if not currently_cooling and current_temp > SET_TEMP + get_threshold():
            if now() >= last_cool_time_secs + COMPRESSOR_DELAY_SECONDS:
                #and we haven't run for at least COMPRESSOR_DELAY_SECONDS
                #start cooling
                print(now_str() + ": turning on ac", flush=True)
                idle_time = (now() - last_cool_time_secs) / 60
                print("it was off for " + str(idle_time) + " minutes", flush=True)
                start_temp = read_temperature()
                #try to turn on the AC every MIN_RUN_TIME_SECONDS until the temperature goes down
                while read_temperature() >= start_temp:
                    send_power_command()
                    print("Sending power command", flush=True)
                    last_cool_time_secs = now()
                    currently_cooling = True
                    start_temp = read_temperature() # read again in case the first value was bad
                    time.sleep(get_run_time()/2)
                time.sleep(get_run_time()/2)
            else:
                sleep_until = last_cool_time_secs + COMPRESSOR_DELAY_SECONDS
                sleep_duration = int(round(sleep_until - now()))
                print(now_str() + ": temp is too warm but waiting " + str(sleep_duration) + " seconds for compressor delay", flush=True)
                time.sleep(sleep_duration)
                continue
        else:
            if currently_cooling and current_temp < SET_TEMP - get_overcool():
                print(now_str() + ": too cold. turning off ac.", flush=True)
                '''
                start_temp = read_temperature()
                retry_count = 0
                while read_temperature() < start_temp + 0.2:
                    start_temp = read_temperature()
                    print(now_str() + " retry " + str(retry_count) + ". sending power off command. current temp is: " + str(read_temperature()), flush=True)
                    print(now_str() + " waiting for temp to be at least " + str(start_temp + 0.2), flush=True) 
                    last_cool_time_secs = now() # wait at least half an hour from now before running again
                    send_power_command()
                    time.sleep(MIN_RUN_TIME_SECONDS)
                    retry_count = retry_count + 1
                print(now_str() + " I think the ac is really off now. Temp is " + str(read_temperature()), flush=True)
                '''
                last_cool_time_secs = turn_off(0)
                run_time = (now() - last_cool_time_secs) / 60
                print("ac ran for " + str(run_time) + " minutes", flush=True)
                currently_cooling = False
        print(now_str() + ": sleeping a minute before next loop", flush=True)
        print(flush=True)
        time.sleep(60)

if __name__ == "__main__":
    # execute only if run as a script
    main()
