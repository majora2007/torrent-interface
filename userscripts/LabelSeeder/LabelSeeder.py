'''
	@name LabelSeeder.py
	@author Joseph Milazzo
	@description Stop seeding any freshly completed torrent without correct label.
'''
import httplib
import json

context = httplib.HTTPConnection('localhost', 5000)

# Get information about torrent
context.request('POST', '/getTorrent', '{}')
torrent = json.loads(context.getresponse().read())

if torrent.label is not str(None) or not torrent.label.lower() in ['BakaBT']:
	context.request('POST', '/stopTorrent', json.dump({'hash': torrent.info_hash}))
	print 'Stopping torrent'

# Script is done, ensure interface knows it.
context.request('POST', '/done', '{}')
doc = context.getresponse().read()