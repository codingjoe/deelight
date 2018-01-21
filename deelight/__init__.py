import asyncio
import datetime
import functools
import json
import logging
import random
import signal
import urllib.error
import urllib.parse
import urllib.request
from collections import namedtuple

from pysolar import solar
from yeelib import search_bulbs, bulbs, Bulb

from deelight.exceptions import CommandError

logger = logging.getLogger(__package__)

WEATHER_API_KEY = 'c44a9ddf88c84c19e721be068956dd5d'

WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather?%s'

LightSetting = namedtuple('LightSetting', ['temprature', 'brightness', 'power_mode'])

weather_data = {}


class CeiligLight(Bulb):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        light_setting = get_light_setting()
        if light_setting:
            asyncio.Task(self.set_light_setting(light_setting))

    async def set_light_setting(self, light_setting: LightSetting, duration=5000):
        logger.info("Setting %s to %s", self, light_setting)
        await self.send_command("set_power", ["on", "sudden", duration, light_setting.power_mode])
        if light_setting.power_mode == 1:
            await self.send_command("set_ct_abx", [light_setting.temprature, "smooth", duration])
        await self.send_command("set_bright", [light_setting.brightness, "smooth", duration])


def get_light_setting():
    if not weather_data:
        logger.info("Waiting for weather data...")
        return
    latitude = weather_data['coord']['lat']
    longitude = weather_data['coord']['lon']
    cloudiness = weather_data['clouds']['all'] / 100.0
    temperature = weather_data['main']['temp']
    pressure = weather_data['main']['pressure'] * 100

    altitude = solar.get_altitude(latitude, longitude, datetime.datetime.now(),
                                  temperature=temperature, pressure=pressure)

    logger.info("Sun's altitude is %.1f degrees", altitude)
    logger.info("Cloudiness is %.0f%%", cloudiness * 100)

    if altitude > 6:
        # daylight
        temperature = 5200
        brightness = 100
        if random.random() < cloudiness:
            cloud_thickness = random.random()
            temperature += 1300 * cloud_thickness
            brightness -= 75 * cloud_thickness
        return LightSetting(int(temperature), int(brightness), power_mode=1)
    elif altitude > 0.0:
        temperature = 2700 + 2500 * altitude / 6
        brightness = 100 * altitude / 6
        return LightSetting(int(temperature), int(brightness), power_mode=1)
    elif altitude > -6:
        temperature = 2700 + 4800 * altitude / 6
        brightness = 100 * altitude / 6
        return LightSetting(int(temperature), int(brightness), power_mode=5)
    elif altitude < -6:
        return LightSetting(1700, 10, power_mode=5)


async def update_weather_data(city):
    while True:
        params = urllib.parse.urlencode({'q': city, 'APPID': WEATHER_API_KEY})
        try:
            url = WEATHER_API_URL % params
            logger.info("GET %s", url)
            response = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            raise CommandError("City '%s' could not be found." % city) from e
        except urllib.error.URLError:
            logger.exception("Network Error")
            await asyncio.sleep(10)
        else:
            content = response.read().decode()
            weather_data.update(json.loads(content))
            logger.debug(weather_data)

            await asyncio.sleep(60 * 30)  # every half hour


async def update_bulbs():
    while True:
        light_setting = get_light_setting()
        if light_setting is None:
            return

        for b in bulbs.values():
            asyncio.Task(b.set_light_setting(light_setting))

        await asyncio.sleep(60)  # every minute


def control_lights(city):
    loop = asyncio.get_event_loop()

    loop.create_task(update_weather_data(city))
    loop.create_task(update_bulbs())
    loop.create_task(search_bulbs(bulb_class=CeiligLight, loop=loop))

    def ask_exit(signame):
        logger.critical("Got signal %s: exit", signame)
        logger.critical("Stopping...")
        loop.stop()

    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(ask_exit, signame))

    try:
        loop.run_forever()
    finally:
        loop.close()
