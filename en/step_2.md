## What you will need

### Hardware

- A Raspberry Pi Oracle Weather Station kit

You should have built and installed your Oracle Weather Station kit. If you have not done so yet, follow [these instructions](https://www.raspberrypi.org/learning/weather-station-guide/), and then come back here when you've finished!

The steps in this guide assume that you will be regularly uploading data to Initial State. You can do this **and** continue to upload data to the Oracle database.

### Software

- The [Oracle Weather Station software](https://www.raspberrypi.org/learning/weather-station-guide/software.md){:target="_blank"}

 - The Python `ISStreamer` library — install it by logging in to your Weather Station Pi, opening a terminal window, and typing:

```bash
sudo pip3 install ISStreamer

```
- If you're running a version of the Weather Station software from **before September 2017**, you'll also need to have installed the Python 2.7 version of the `ISStreamer` library:

```bash
sudo pip install ISStreamer

```
### Additional resources

As a user of one of our Oracle Weather Station kits, you will have been issued with a **subscription code** and a **streaming key**. You can use these to access and upload data to the dedicated white-label area hosted by Initial State.

If you can't find these details, please email weather@raspberrypi.org with your school name and address, and the email address of the person who applied for the Weather Station kit.
