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

- When you installed the Weather Station software, you will have noticed that there are already a couple of credentials used by Oracle Weather Station scripts: for the local MariaDB and the online Oracle databases. Rather than store these directly in the Python code itself, these are stored as supplementary JSON files. This is good practice so now that testing is complete, do the same for the Initial State keys.   

---hints---
---hint---
Create a file called `credentials.initialstate` and populate it with the bucket and access keys:

```json
{
"BUCKET_KEY": "XXXX",
"ACCESS_KEY": "YYYY"
}
```
---/hint---
---hint---
Add the following lines to your `log_all_sensors` code:
```python
credentials_file = os.path.join(os.path.dirname(__file__), "credentials.initialstate")
f_is = open(credentials_file, "r")
credentials_is = json.load(f_is)
```
---/hint---
---hint---
Finally, change the Initial State key variables to contain the credentials loaded from the file:
```python
BUCKET_KEY = credentials_is['BUCKET_KEY'] # Replace XXXX with your bucket key
ACCESS_KEY = credentials_is['ACCESS_KEY']
```
---/hint---
---/hints---


If you've followed the [standard installation instructions](https://www.raspberrypi.org/learning/weather-station-guide/){:target="_blank"}, this script should be run every five minutes via Cron, which is a sensible frequency.

Once you have data uploading regularly, you can use your Initial State dashboard to analyse how your local climate is changing over time.
