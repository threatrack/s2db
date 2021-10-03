import os
import sys
import logging

_S2DB_ROOT = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
sys.path.append(_S2DB_ROOT)

from common.config import config

logging.basicConfig(filename=config['log']['path'], level=config['log'].get('level','WARNING'))

def get_logger(name):
	return logging.getLogger(name)

