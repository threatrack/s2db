import configparser
import os

config = configparser.ConfigParser()

config_paths = [
	"s2db.conf",
	"/opt/s2db/s2db.conf",
	"/etc/s2db/s2db.conf",
	"/etc/s2db.conf",
	os.path.join(os.path.abspath(os.path.dirname(__file__)), "../s2db.conf"),
	os.path.expanduser("~") + "/.s2db.conf",
	os.path.expanduser("~") + "/.s2db/s2db.conf",
]

for config_path in config_paths:
	if config.read(config_path) != []:
		break

