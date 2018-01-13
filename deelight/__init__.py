import asyncio
import datetime
import functools
import json
import logging
import random
import signal
import urllib.parse
import urllib.request
from collections import namedtuple
from urllib.error import HTTPError

from pysolar import solar
from yeelib import search_bulbs, bulbs, Bulb

from deelight.exceptions import CommandError

logger = logging.getLogger(__package__)

WEATHER_API_KEY = 'c44a9ddf88c84c19e721be068956dd5d'

WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather?%s'

LightSetting = namedtuple('LightSetting', ['temprature', 'brightness', 'power_mode'])


class MutableBool:

    def __init__(self, state):
        self.__state = bool(state)

    def __bool__(self):
        return self.__state

    def set(self, value):
        self.__state = bool(value)


class CeiligLight(Bulb):
    async def set_light_setting(self, light_setting: LightSetting, duration=5000):
        logger.info("Setting %s to %s", self, light_setting)
        await self.send_command("set_power", ["on", "sudden", duration, light_setting.power_mode])
        if light_setting.power_mode == 1:
            await self.send_command("set_ct_abx", [light_setting.temprature, "smooth", duration])
        await self.send_command("set_bright", [light_setting.brightness, "smooth", duration])


def get_light_setting(data):
    latitude = data['coord']['lat']
    longitude = data['coord']['lon']
    cloudiness = data['clouds']['all'] / 100.0
    temperature = data['main']['temp']
    pressure = data['main']['pressure'] * 100

    altitude = solar.get_altitude(latitude, longitude, datetime.datetime.now(),
                                  temperature=temperature, pressure=pressure)

    logger.info("Sun's altitude is %.1f°", altitude)
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


def get_weather_data(city, data=None):
    if data is None:
        data = {}
    params = urllib.parse.urlencode({'q': city, 'APPID': WEATHER_API_KEY})
    try:
        url = WEATHER_API_URL % params
        logger.info("GET %s", url)
        response = urllib.request.urlopen(url)
    except HTTPError as e:
        raise CommandError("City '%s' could not be found." % city) from e
    else:
        content = response.read().decode()
        data.update(json.loads(content))
        logger.debug(data)
        return data


def control_lights(city):
    loop = asyncio.get_event_loop()

    data = get_weather_data(city)

    loop.create_task(update_weather_data(city, data))
    loop.create_task(update_bulbs(data))

    def ask_exit(signame):
        logger.critical("Got signal %s: exit", signame)
        logger.critical("Stopping...")
        loop.stop()

    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(ask_exit, signame))

    try:
        with search_bulbs(bulb_class=CeiligLight, loop=loop):
            loop.run_forever()
    finally:
        loop.close()


async def update_weather_data(city, data):
    while True:
        get_weather_data(city, data)
        await asyncio.sleep(60 * 30)  # every half hour


async def update_bulbs(data):
    while True:
        light_setting = get_light_setting(data)

        for b in bulbs.values():
            asyncio.Task(b.set_light_setting(light_setting))

        await asyncio.sleep(60)  # every minute
