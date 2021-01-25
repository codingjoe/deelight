"""Make your Xiaomi Mi YeeLight bulb emulate outside lighting conditions."""
import asyncio
import logging
import socket
import sys

import click
from yeelib import YeelightProtocol

from deelight import CeilingLight

LOG_FORMAT = "%(asctime)s %(name)-8s %(levelname)-8s %(message)s"

logger = logging.getLogger(__package__)


@click.command()
@click.argument("latitude", type=float)
@click.argument("longitude", type=float)
@click.option(
    "--clouds",
    "-c",
    default=0.1,
    help="Cache of clouds between. Between 0 and 1, default 0.1.",
)
@click.option(
    "--verbosity", "-v", default=0, count=True, help="Increase output verbosity."
)
def main(latitude, longitude, clouds, verbosity):
    setup_logging(verbosity)
    loop = asyncio.get_event_loop()
    unicast_connection = loop.create_datagram_endpoint(
        lambda: YeelightProtocol(
            CeilingLight,
            loop=loop,
            latitude=latitude,
            longitude=longitude,
            clouds=clouds,
        ),
        family=socket.AF_INET,
    )
    ucast_transport, _ = loop.run_until_complete(unicast_connection)
    loop.run_forever()
    loop.close()


def get_logging_level(verbosity):
    level = logging.WARNING
    level -= verbosity * 10
    if level < logging.DEBUG:
        level = logging.DEBUG
    return level


def setup_logging(verbosity):
    hdlr = logging.StreamHandler(sys.stdout)
    hdlr.setLevel(get_logging_level(verbosity))
    hdlr.setFormatter(logging.Formatter(LOG_FORMAT))
    for name in [__package__, "yeelib", "ssdp"]:
        l = logging.getLogger(name)
        l.addHandler(hdlr)
        l.setLevel(get_logging_level(verbosity))


if __name__ == "__main__":
    sys.exit(main())
