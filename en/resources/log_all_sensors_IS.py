#!/usr/bin/python
import time
import sys
from ISStreamer.Streamer import Streamer
from gpiozero import MCP3008
import interrupt_client, MCP342X, wind_direction, HTU21D, bmp085, tgs2600, ds18b20_therm
import database # requires MySQLdb python 2 library which is not ported to python 3 yet

def degrees_to_cardinal(d):
    '''
    note: this is highly approximate...
    '''
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    #ix = int((d + 11.25)/22.5)
    ix = int((d + 11.25)/22.5)
    return dirs[ix % 16]

pressure = bmp085.BMP085()
temp_probe = ds18b20_therm.DS18B20()
air_qual = tgs2600.TGS2600(adc_channel = 0)
humidity = HTU21D.HTU21D()
wind_dir = wind_direction.wind_direction(adc_channel = 0, config_file="wind_direction.json")
interrupts = interrupt_client.interrupt_client(port = 49501)

db = database.weather_database() #Local MySQL db

wind_average = wind_dir.get_value(10) #ten seconds
ambient_temp = humidity.read_temperature()
ground_temp =  temp_probe.read_temp()
air_quality = air_qual.get_value()
pressure = pressure.get_pressure()
humidity = humidity.read_humidity()
wind_speed = interrupts.get_wind()
wind_gust =  interrupts.get_wind_gust()
rainfall = interrupts.get_rain()

print("Inserting...")
db.insert(ambient_temp, ground_temp, air_quality, pressure, humidity, wind_average, wind_speed, wind_gust, rainfall)
print("done")

credentials_file = os.path.join(os.path.dirname(__file__), "credentials.initialstate")

if os.path.isfile(credentials_file):
    f = open(credentials_file, "r")
    credentials = json.load(f)
    f.close()
else:
     print("Credentials file not found")

interrupts.reset()
# --------- Initial State Settings ---------

BUCKET_NAME = ":partly_sunny:  Weather Station"
BUCKET_KEY = credentials['X-IS-BucketKey']
ACCESS_KEY = credentials['X-IS-AccessKey']
SENSOR_LOCATION_NAME = ""
# ---------------------------------

ambient_temp = float("{0:.2f}".format(ambient_temp))
ground_temp = float("{0:.2f}".format(ground_temp))
humidity = float("{0:.2f}".format(humidity))
pressure = float("{0:.2f}".format(pressure))
wind_speed = float("{0:.2f}".format(wind_speed))
wind_direction_text = degrees_to_cardinal(int(wind_average))
wind_gust = float("{0:.2f}".format(wind_gust))
wind_average = float("{0:.2f}".format(wind_average))
air_quality = float("{0:.2f}".format(air_quality))

print("uploading to IS")
streamer = Streamer(bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)
streamer.log(":sunny: " + SENSOR_LOCATION_NAME + " Ambient Temp (C)", ambient_temp)
streamer.log(":earth_americas: " + SENSOR_LOCATION_NAME + " Ground Temp (C)", ground_temp)
streamer.log(":cloud: " + SENSOR_LOCATION_NAME + " Air Quality", air_quality)
streamer.log(":droplet: " + SENSOR_LOCATION_NAME + " Pressure(mb)", pressure)
streamer.log(":sweat_drops: " + SENSOR_LOCATION_NAME + " Humidity(%)", humidity)
streamer.log(":cloud_tornado: " + SENSOR_LOCATION_NAME + " Wind Direction", wind_average)
streamer.log(":cloud_tornado: " + SENSOR_LOCATION_NAME + " Wind Direction Text", wind_direction_text)
streamer.log(":wind_blowing_face: " + SENSOR_LOCATION_NAME + " Wind Speed", wind_speed)
streamer.log(":wind_blowing_face: " + SENSOR_LOCATION_NAME + " Wind Gust", wind_gust)
streamer.log(":cloud_rain: " + SENSOR_LOCATION_NAME + " Rainfall", rainfall)

streamer.flush()
