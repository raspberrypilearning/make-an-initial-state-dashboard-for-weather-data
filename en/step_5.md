## Using live data

For testing and development of your code, you used made-up data values which you stored as variables in your code. Once you've tested your upload, you should delete these and amend the code to process real data from your Weather Station.

You real data values typically are produced are floating-point numbers with several decimal places, even though the Weather Station sensors are not really capable of this level of precision. Therefore, it makes sense to round the values to two or three decimal places.

[[[generic-python-rounding-numbers]]]

- To round your humidity measurement to three decimal places, do this:

    ```python
    humidity = "{0:.3f}".format(humidity)
    ```

- Write similar commands to round the other Weather Station measurements.


--- hints ---
--- hint ---
Use `.format` to perform the rounding.
```python
rounded_number = "{0:.3f}".format(number_with_dec_places)
```
--- /hint---
--- hint ---
- Your code should look like this:
```python
ambient_temp = "{0:.3f}".format(ambient_temp)
ground_temp = "{0:.3f}".format(ground_temp)
pressure = "{0:.3f}".format(pressure)
wind_speed_mph = "{0:.3f}".format(wind_speed)
wind_gust_mph = "{0:.3f}".format(wind_gust)
rainfall = "{0:.3f}".format(rainfall)
```
---/hint---
---/hints---

### Wind direction

As you're going to be building some dashboards, it will be easier to see a text-based representation of the wind direction. At the moment, you are sending a numerical value for the angle your wind vane detects. In the next step, you're going convert that angle into [cardinal (N, S, E, W) or intercardinal directions (ESE, NW, etc.)](http://snowfence.umn.edu/Components/winddirectionanddegreeswithouttable3.htm){:target="_blank"}.

- You could just use a look-up table made out of a series of `if/elif/else` conditionals, but it is neater to write a function to perform a numerical calculation.

```python
def degrees_to_cardinal(angle):

    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((angle + 11.25)/22.5)
    return directions[ix % 16]
```

---collapse---
---
title: Code explanation
---
- Line 1: define a function named `degrees_to_cardinal` that takes an angle as an input value.

- Line 2: there are 16 possible output values in the `directions` list.

- Line 3: the first step in the conversion is to divide the angle by `22.5`, because `360 degrees / 16 directions = 22.5 degrees`. However, to avoid values falling on the threshold between adjacent directions (e.g. think about what happens at 0 and 360 degrees), you need to add half a step value/direction change (`22.5 / 2 = 11.25`). Then truncate the value using integer division.

- Line 4: this uses the `ix` value calculated in line 3 as a list index to select right the cardinal direction value and return it. By using modulo 16 division, you make sure that the maximum possible value of `ix` used as a list index is 15 - the largest index value in the `directions` list.

---/collapse---

- Now you can use this function to convert the `wind_direction` (in degrees) from your Weather Station into a cardinal direction. Add these two lines to your code.

```python
wind_direction_text = degrees_to_cardinal(int(wind_direction))
streamer.log(":cloud_tornado: " + SENSOR_LOCATION_NAME + " Wind direction text", wind_direction_text)
```
- Run your code and check your Initial State dashboard. You should see that a new tile with the converted wind direction has appeared.

![](images/image30.png)

### Integration with Weather Station software

Once your code is working, you need to integrate it with the Oracle Weather Station software, which can be found in the `/home/pi/weather-station` directory.

- The Oracle Weather Station software uses the crontab method to run a Python script called [`log_all_sensors.py`](https://github.com/raspberrypi/weather-station/blob/master/log_all_sensors.py) every five minutes. A simple way to modify your Weather Station so that it regularly uploads data to Initial State is to add the upload code you have written to this file.

---hints---
---hint---
Make sure you add the library imports to the top of `log_all_sensors.py` when you modify this file.
---/hint---
---hint---
The rest of your code can be inserted after lines in `log_all_sensors.py` which handle inserting readings into the local MariaDB database.  
---/hint---
---hint---
A modified  **Python3** `log_all_sensors.py` could look like this:

```python
#!/usr/bin/python3
import time
import sys
import json
import interrupt_client, MCP342X, wind_direction, HTU21D, bmp085, tgs2600, ds18b20_therm
import database
import os
from ISStreamer.Streamer import Streamer

pressure = bmp085.BMP085()
temp_probe = ds18b20_therm.DS18B20()
air_qual = tgs2600.TGS2600(adc_channel = 0)
humidity = HTU21D.HTU21D()
wind_dir = wind_direction.wind_direction(adc_channel = 0, config_file="wind_direction.json")
interrupts = interrupt_client.interrupt_client(port = 49501)

db = database.weather_database() #Local MariaDB db

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

interrupts.reset()

def degrees_to_cardinal(angle):

    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((angle + 11.25)/22.5)
    return directions[ix % 16]

credentials_file = os.path.join(os.path.dirname(__file__), "credentials.initialstate")
f_is = open(credentials_file, "r")
credentials_is = json.load(f_is)
f.close()


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
print("Upload code finished")
```
**Note**: this is Python 3 code. If you're using a version of the Weather Station software from before **September 2017**, you'll be programming in Python 2.7. In this case, your code will be almost identical, except that the first line needs to be `#!/usr/bin/python` instead.
---/hint---
---/hints---

If you've followed the [standard installation instructions](https://www.raspberrypi.org/learning/weather-station-guide/){:target="_blank"}, this script should be run every five minutes via Cron, which is a sensible frequency.

Once you have data uploading regularly, you can use your Initial State dashboard to analyse how your local climate is changing over time.
