#!/usr/bin/python

import logging
import sys

from mwr.common import logger

from andsploit.ssl import SSLManager

logger.setLevel(logging.DEBUG)
logger.addStreamHandler()

SSLManager().run(sys.argv[2::])
    
