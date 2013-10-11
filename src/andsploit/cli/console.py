#!/usr/bin/python

import logging
import sys

from mwr.common import logger

from andsploit.console import Console

logger.setLevel(logging.DEBUG)
logger.addStreamHandler()

Console().run(sys.argv[2::])
