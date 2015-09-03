'''
@author: Joseph Milazzo
@description: A script which is run after a uTorrent torrent has completed downloading. This script will copy the torrent data to the appropriate directory on
                a remote machine. Directory is determined by torrent's label. This script is configurable through config.ini file.

This takes arguments from command line.

Script Arguements:
--name Name of downloaded file (for single file torrents)
--dir Directory where files are saved
--title Title of torrent
--state State of torrent*
--label Label
--tracker Tracker
--status_msg Status message string (same as status column)
--info_hash hex encoded info-hash
--prev_state Previous state of torrent
--kind kind of torrent (single|multi)
--log_dir Directory to store log data in

*State is a combination of:
started = 1
checking = 2
start-after-check = 4
checked = 8
error = 16
paused = 32
auto = 64
loaded = 128

For example, if a torrent job has a status of 201 = 128 + 64 + 8 + 1, then it is loaded, queued, checked, and started.
A bitwise AND operator should be used to determine whether the given STATUS contains a particular status.


Example Input:
Directory="K:\Applications\Advanced SystemCare Pro 7.3.0.454 [ChingLiu]"
Torrent Name="Advanced SystemCare Pro 7.3.0.454 [ChingLiu]"
Label="Test"
Kind="multi"
Filename="Activation pictures\Snap1.jpg"
Hash="E2BCFD4306B905E3B785F5DB8BA54ACCAE46FFB6"
'''

''' The way the ending script will work is it will start and read needed info
    from config file. The application will then load all scripts from userscripts (nested folders) and create a queue from them (scripts can define priority to ensure they are scheduled before another). Each script will execute in priority order on a separate thread or coroutine. Once all scripts execute (or expire if not completed after threadshold (user defined) is met, the program logs and terminates.)

    This script is defined for uTorrent, but it should be usable by other torrenting programs. Ensure you use proper encapsulation and inheritance for this. :)
'''
import argparse
import commands
import ConfigParser
from collections import namedtuple
from flask import Flask # Used for web API
import flask
import logging
import json
import uTorrent
import os
import signal
import subprocess
import sys
import threading
import time


Torrent = namedtuple('Torrent', ['directory', 'kind', 'label', 'name', 
    'title', 'state', 'prev_sate', 'tracker', 'status_msg', 'info_hash']) 

class ScriptThread(threading.Thread):
    try:
        def __init__(self, script_file):
            threading.Thread.__init__(self)
            self.script_file = script_file
        def run(self):
            print 'Thread runnning for ' + os.path.abspath(self.script_file)
            subprocess.call('python ' + self.script_file, stderr=subprocess.STDOUT, shell=True)
    except Exception, e:
        raise e

# TODO: Fix this
def sig_handler():
    logger.log('Signal Handler called')
    app.stop()
    flask.request.environ.get('werkzeug.server.shutdown')()
    app_thread.join()
    [t.join() for t in threads]

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

def get_argument(argument, default="None"):
    if argument:
        return argument[0]
    else:
        return default

def start_app():
    app.run()

def init():
    global config
    # Create Configuration Parser and setup Logger
    config = ConfigParser.ConfigParser()
    config.read("config.ini")

    log_file = config_section_map("Logging")['log_file']
    lpath = config_section_map("Logging")['log_directory']
    if lpath is None:
        lpath = '.'
    log_directory = os.path.abspath(lpath)

    if not os.path.exists(log_directory):
        os.mkdir(log_directory)

    log_filePath = os.path.join(log_directory, log_file)

    if not os.path.isfile(log_filePath):
        with open(log_filePath, "w") as emptylog_file:
            emptylog_file.write('');

    logging.basicConfig(filename=log_filePath,level=logging.DEBUG)
    logger = logging.getLogger(__name__);

    logger.info("######### Script Executed at " + time.asctime(time.localtime(time.time())))

    # CLI
    parser = argparse.ArgumentParser()

    parser.add_argument('--state', required=False, nargs=1, help="State of torrent")
    parser.add_argument('--prev_state', required=False, nargs=1, help="Previous state of torrent")
    parser.add_argument('--tracker', required=False, nargs=1, help="Torrent's tracker")
    parser.add_argument('--status_msg', required=False, nargs=1, help="Status message string (same as status column)")

    parser.add_argument('--dir', required=False, nargs=1, help="Directory where files are saved")
    parser.add_argument('--name', required=False, nargs=1, help="Name of downloaded file (for single file torrents)")
    parser.add_argument('--title', required=False, nargs=1, help="Title of torrent")
    parser.add_argument('--label', required=False, nargs=1, help="Torrent's label")
    parser.add_argument('--kind', required=False, nargs=1, help="Kind of torrent (single | multi)")
    parser.add_argument('--info_hash', required=False, nargs=1, help="Hex encoded info-hash")

    args = parser.parse_args()
    torrent = None

    try:
        logger.info("Parsing Arguments")

        # Required Arguments
        torrent_dir = str(get_argument(args.dir))
        torrent_kind = str(get_argument(args.kind))
        torrent_label = str(get_argument(args.label))
        torrent_name = str(get_argument(args.name))
        torrent_title = str(get_argument(args.title))

        # Optional Arguments
        torrent_state = int(get_argument(args.state, -1))
        torrent_prev_state = int(get_argument(args.prev_state, -1))
        torrent_tracker = str(get_argument(args.tracker))
        torrent_status_msg = str(get_argument(args.status_msg))
        torrent_info_hash = str(get_argument(args.info_hash))

        torrent = Torrent(torrent_dir, torrent_kind, torrent_label, torrent_name, torrent_title, 
            torrent_state, torrent_prev_state, torrent_tracker, torrent_status_msg, torrent_info_hash)

    except Exception, e:
        logger.info(str(e))

    logger.info("Finished Parsing Arguments")
    return torrent


app = Flask(__name__)
@app.route('/getTorrent', methods=['GET', 'POST'])
def get_torrent():
    ''' Returns the torrent that has triggered this script '''
    return json.dumps(torrent.__dict__)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    ''' Kills the server. ''' 
    flask.request.environ.get('werkzeug.server.shutdown')()
    return 'Server Shutdown'

@app.route('/done', methods=['POST'])
def userscript_finished():
    ''' Userscript is finished executing. Increment script counter. '''
    global finished_userscripts
    finished_userscripts += 1
    if finished_userscripts >= len(scripts):
        flask.request.environ.get('werkzeug.server.shutdown')()
    return str(finished_userscripts)

@app.route('/stopTorrent', methods=['POST'])
def stop_torrent(arguments):
    global torrent_client
    print arguments
    torrent_client.stop_torrent(arguments.hash)
    return '{}'

scripts = []
threads = []
finished_userscripts = 0
if __name__ == '__main__':

    # Register signals, such as CTRL + C
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    global torrent
    global torrent_client
    torrent = init()
    if torrent is None:
        logger.warn('Torrent is not set!')

     # Setup WebAPI-enabled Torrent Client
    url = 'http://' + config_section_map("Web API")['address'] + ':' + config_section_map("Web API")['port'] + '/gui/'
    torrent_client = uTorrent.uTorrent(url, config_section_map("Web API")['username'], config_section_map("Web API")['password'])

    global app_thread
    app_thread = threading.Thread(target=start_app).start()

    # Find userscripts
    userscript_dir = os.path.abspath('userscripts')
    exclude = []
    for root, dirs, files in os.walk(userscript_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file in files:
            if file.endswith('.py'):
                # Add file to pqueue
                scripts.append(os.path.join(root, file))

    # Let's execute some coroutines
    for script in scripts:
        t = ScriptThread(script).start()
        threads.append(t)



