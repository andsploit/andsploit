#!/usr/bin/python

import logging
import sys

from mwr.common import logger

from andsploit.server import Server

logger.setLevel(logging.INFO)
logger.addStreamHandler()

Server().run(sys.argv[2::])
