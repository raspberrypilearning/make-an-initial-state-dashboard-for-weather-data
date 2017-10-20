## Using live data

For testing and development, you used some fictitious data values that you stored as variables in your code. Once you've tested your upload, you should delete these and amend the code to process real data from your weather station.

As you're going to be building some dashboards, it will be easier to see a text-based representation of the wind direction. At the moment you send a numerical value for the angle detected by our wind vane. So in the next step you're going onvert that into [cardinal (N, S, E or W) or intercardinal directions (ESE, NW etc)](http://snowfence.umn.edu/Components/winddirectionanddegreeswithouttable3.htm){:target="_blank"}.

- You could just use a 'look-up table' made out of a series of `if... elif... else` conditionals, but it is neater to simply write a function to perform a numerical calculation.


```python
def degrees_to_cardinal(angle):

    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((angle + 11.25)/22.5)
    return directions[ix % 16]
```

---collapse---
---
title: Code Explanation
---
- Line 1: Define a function named degrees_to_cardinal, that takes an angle as an input value.

- Line 2: There are 16 possible values as shown in the `directions` list in the code snippet above.

- Line 3: So the first step in the conversion is to divide the angle by 22.5 (because 360 degrees / 16 directions = 22.5 degrees).

- However, to avoid values falling on the change threshold between adjacent directions (think about what happens at 0 and 360 degrees), you need to add half a step value/direction change (22.5 / 2 = 11.25).

- Then truncate the value using integer division.

- Line 4: This gives the index into the list from which we select the cardinal value (modulo 16).
---/collapse---

- Now you can use this function to convert the wind_direction (in degrees) from your Weather Station into cardinal value. Add these two lines to your code.

```python
wind_direction_text = degrees_to_cardinal(int(wind_average))
streamer.log(":cloud_tornado: " + SENSOR_LOCATION_NAME + " Wind Direction Text", wind_direction_text)
```
- Run your code and check your Initial State dashboard. You should see that a new tile with the converted wind direction has appeared.

![](images/image30.png)

Once your code is working, you need to integrate it with the Oracle Weather Station software. This can be found it the ``/home/pi/weather-station` directory.

- The Oracle Weather Station software uses the Crontab method to run a Python script called [log_all_sensors.py](https://github.com/raspberrypi/weather-station/blob/master/log_all_sensors.py) every 5 minutes. A simple way to modify your Weather Station so that it regularly uploads data to Initial State is to add the upload code you have written to this file.

---hints---
---hint---
Make sure you add the library imports to the top of your modified file.
---/hint---
---hint---
The rest of your code can be inserted after lines in the original `log_all_sensors.py` that handle inserting readings into the local MariaDB database.  
---/hint---
---hint---
A modified log_all_sensors.py could look like this:
```python
#!/usr/bin/python
import time
import sys
from ISStreamer.Streamer import Streamer
from gpiozero import MCP3008
import interrupt_client, MCP342X, wind_direction, HTU21D, bmp085, tgs2600, ds18b20_therm
import database # requires MySQLdb python 2 library which is not ported to python 3 yet

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

def degrees_to_cardinal(angle):

    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((angle + 11.25)/22.5)
    return directions[ix % 16]

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
]
```
---/hint---
---/hints---

If you've followed the [standard installation instructions](https://www.raspberrypi.org/learning/weather-station-guide/){:target="_blank"}, this script should be run every five minutes via Cron, which is a sensible frequency.

Once you have data uploading regularly, you can use your Initial State dashboard to analyse how your local climate is changing over time.
