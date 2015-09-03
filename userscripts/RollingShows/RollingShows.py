''' 
	@name RollingShows.py
	@author Joseph Milazzo
	@description Ensure only N episodes are allowed for supplied directories
'''
import ConfigParser
from collections import namedtuple
import datetime
import httplib
import os
import time

SCRIPT_NAME = 'RollingShows'
# This is needed due to how called
SCRIPT_PATH = 'userscripts/RollingShows'
Info = namedtuple('Info', ['mtime', 'filepath'])

def config_section_map(section):
    dict1 = {}
    options = config.options(section);
    for option in options:
        try:
            dict1[option] = config.get(section, option);
            if dict1[option] == -1:
                print("skip: %s" % option);
        except:
            print("exception on %s!" % option);
            dict1[option] = None;
    return dict1;

def get_config(option, default=None):
	try:
		val = config_section_map('Config')[option]
		return val
	except Exception, e:
		pass
	return default

def find_oldest(dates):
	''' 
		Expects dates to be a list of Info namedtuple.
		Returns index of oldest Info.
	'''
	datetime_objs = [date.mtime for date in dates]
	return datetime_objs.index(min(datetime_objs))

def create_info(root, file):
	filepath = os.path.join(root, file)
	(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(os.path.normpath(filepath))
	d_time = datetime.datetime.fromtimestamp(mtime)
	return Info(d_time, filepath)

if __name__ == '__main__':
	print '%s has executed!' % SCRIPT_NAME

	config = ConfigParser.ConfigParser()
	config.read(os.path.join(SCRIPT_PATH,'config.ini'))

	NUM_EPISODES = int(get_config('max_episodes', 3))
	PATHS = get_config('tracked_shows', []).split(',')
	infos = []

	for path in config_section_map('Config')['tracked_shows'].split(','):
		for root, dirs, files in os.walk(path, topdown=True):
			for file in files:
				infos.append(create_info(root, file))

	# Do the actual work
	if len(infos) > NUM_EPISODES:
		index = find_oldest(infos)
		if index >= 0:
			# Delete the file
			print 'Deleting file: ' + infos[index].filepath
			#os.remove(infos[index].filepath)

	# All userscripts must call /done when finished.
	c = httplib.HTTPConnection('localhost', 5000)
	c.request('POST', '/done', '{}')

				

	





