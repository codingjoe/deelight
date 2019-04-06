"""Make your Xiaomi Mi YeeLight bulb emulate outside lighting conditions."""
import logging
import sys

import click

from deelight import control_lights

LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'

logger = logging.getLogger(__package__)


@click.command()
@click.argument('city')
@click.option('--verbosity', '-v', default=0, count=True,
              help='increase output verbosity')
@click.option('--update/--no-update', default=True,
              help='Do not update light setting for running lights.')
@click.option('--clouds/--no-clouds', default=True,
              help='Dim light to simulate clouds.')
def main(city, verbosity, update, clouds):
    setup_logging(verbosity)
    control_lights(city, update=update, clouds=clouds)


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
    logger.addHandler(hdlr)
    logger.setLevel(get_logging_level(verbosity))

    yeelib = logging.getLogger('yeelib')
    yeelib.addHandler(hdlr)
    yeelib.setLevel(get_logging_level(verbosity - 1))

    ssdp = logging.getLogger('ssdp')
    ssdp.addHandler(hdlr)
    ssdp.setLevel(get_logging_level(verbosity - 2))


if __name__ == '__main__':
    sys.exit(main())
