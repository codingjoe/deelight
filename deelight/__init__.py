import asyncio
import datetime
import logging
import random
from collections import namedtuple

from pysolar import solar
from yeelib import Bulb

from deelight.exceptions import CommandError

logger = logging.getLogger(__package__)

LightSetting = namedtuple("LightSetting", "temprature brightness power_mode")


class CeilingLight(Bulb):
    update_interval = 45
    daylight = 4000
    moonlight = 2700
    peak = 6500

    def __init__(self, latitude, longitude, clouds=0.1, **kwargs):
        self.latitude = latitude
        self.longitude = longitude
        self.clouds = clouds
        super().__init__(**kwargs)
        asyncio.Task(self.update_light_setting())

    def __del__(self):
        self.alive = False
        super().__del__()

    async def set_light_setting(self, light_setting: LightSetting, duration=5000):
        logger.info("Setting %s to %s", self, light_setting)
        self.power = "on"
        await self.send_command(
            "set_power", ["on", "sudden", duration, light_setting.power_mode]
        )
        self.ct = light_setting.temprature
        if light_setting.power_mode == 1:
            await self.send_command(
                "set_ct_abx", [light_setting.temprature, "smooth", duration]
            )
        self.bright = light_setting.brightness
        await self.send_command(
            "set_bright", [light_setting.brightness, "smooth", duration]
        )

    def get_light_setting(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        sun_altitude_deg = solar.get_altitude(self.latitude, self.longitude, now)
        logger.info("Sun altitude: %.1fº", sun_altitude_deg)

        logger.info("Cloudiness is %.0f%%", self.clouds * 100)
        cloudiness = self.clouds

        if sun_altitude_deg > 16:
            # daylight
            temperature = self.daylight
            brightness = 100
            if self.clouds:
                if random.random() < cloudiness:
                    cloud_thickness = random.random()
                    temperature += (self.peak - self.daylight) * cloud_thickness
                    brightness -= 75 * cloud_thickness
            return LightSetting(int(temperature), int(brightness), power_mode=1)
        elif sun_altitude_deg > 8:
            ratio = 1 - abs((sun_altitude_deg + 8) / 24)
            temperature = self.moonlight + (self.daylight - self.moonlight) * ratio
            brightness = 1 + 99 * ratio
            return LightSetting(int(temperature), int(brightness), power_mode=1)
        elif sun_altitude_deg > -8:
            ratio = 1 - abs((sun_altitude_deg + 8) / 16)
            brightness = 10 + 90 * ratio
            return LightSetting(self.moonlight, int(brightness), power_mode=5)
        elif sun_altitude_deg > -24:
            ratio = 1 - abs((sun_altitude_deg + 8) / 16)
            brightness = 10 * ratio
            return LightSetting(self.moonlight, int(brightness), power_mode=5)
        else:
            return LightSetting(self.moonlight, 0, power_mode=5)

    async def update_light_setting(self):
        while self.alive and not self.manual_override:
            await self.set_light_setting(self.get_light_setting())
            await asyncio.sleep(self.update_interval)
        logger.info("stop updating %r", self)
