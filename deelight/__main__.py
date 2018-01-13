"""Make your Xiaomi Mi YeeLight bulb emulate outside lighting conditions."""
import argparse
import logging
import sys

from deelight import control_lights

LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'

logger = logging.getLogger(__package__)


def main():
    args = get_args()
    setup_logging(args.verbosity)
    control_lights(args.city)


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


def get_args():
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('city',
                        help='name of the city to emulate')
    parser.add_argument("-v", "--verbosity", action="count", default=0,
                        help="increase output verbosity")
    return parser.parse_args()


if __name__ == '__main__':
    sys.exit(main())
