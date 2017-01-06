#!/usr/bin/python3

import sys
import time
import requests
import os
import re
import json
import subprocess

import yaml
from xml.etree import ElementTree

from modules import episode_and_season
from modules import sonarr_functions
from modules import subtitle_verify

config = yaml.safe_load(open(os.path.split(sys.argv[0])[0]+"/config.yml"))

title = sys.argv[1]
subtitle_input = sys.argv[2]
filepath = sys.argv[3]
filename = sys.argv[4]
date_epoch = sys.argv[5]
error = sys.argv[6]
#Convert tvheadend's time since epoch airdate to %Y-%m-%d format
date = time.strftime('%Y-%m-%d', time.localtime(int(date_epoch)))

#User parameters from config file
pushbullet_api = config["pushbullet"]["api"]
output = config["sonarr"]["output"]
tvdb_api = config["tvdb"]["api"]
sonarr_api = config["sonarr"]["api"]
sonarr_ip = config["sonarr"]["host"]
sonarr_port = config["sonarr"]["port"]

print ("*********************************BEGIN*********************************")
print ("Command run: \"%s\" \"%s\" \"%s\" \"%s\" \"%s\" \"%s\" \"%s\"." %(sys.argv[0], sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]))

#Check if subtitle contains multiple episodes. If yes, split subtitle into list
subtitle = subtitle_verify.verify(subtitle_input)

#Get list of tvdb_id's for a given title
tvdb_id_list = episode_and_season.get_tvdb_id(title)

#Get episode info (season number, episode number, tvdb_id of show, etc.)
try:
	episode_info = episode_and_season.get_episode_by_subtitle(tvdb_api, title, subtitle, tvdb_id_list)
except NameError as err:
	requests.post("https://api.pushbullet.com/v2/pushes", data = {"type":"note", "body":err.args, "title":"Tvheadend"}, headers={"Access-Token":pushbullet_api})
	print(err.args)
	quit()
else:
	print ("Episode info found:")
	print (episode_info)
	tvdb_id = episode_info[0][3]

#Look up episode in Sonarr and quit if episode is already downloaded. 
try:
	sonarr_id = sonarr_functions.get_sonarr_id(sonarr_ip, sonarr_port, sonarr_api, tvdb_id)
except NameError as err:
	requests.post("https://api.pushbullet.com/v2/pushes", data = {"type":"note", "body":err.args, "title":"Tvheadend"}, headers={"Access-Token":pushbullet_api})
	print(err.args)
	quit()
file_info = []
for element in episode_info: #For each episode in episode list, look up sonarr episode ID.
	file_info.append (sonarr_functions.get_episode_id(sonarr_ip, sonarr_port, sonarr_api, sonarr_id, element))
for index in file_info: #Check if file has been downloaded. If yes, cancel recording. If no, prevent download.
	if index[1]:
		#file_info[hasFile] is True, cancel recording
		print ("Sonarr has already downloaded this episode. Exiting.")
		quit()
	elif not index[1]:
		#file_info[hasFile] is False, unmonitor that episode in Sonarr.
		print ("Episode found in Sonarr database, has not been downloaded yet.")

#Determine video resolution height from ffprobe of recording file
jsonout = json.loads(subprocess.check_output(["/usr/bin/ffprobe", "-i", filepath, "-v", "quiet", "-of", "json", "-show_entries", "stream=height"]).decode("utf-8"))
height = str(jsonout["streams"][0]["height"])
print ("Video resolution height is \"%s\"." % height)
#Determine quality from resolution height
if height == "480":
	quality = "SDTV"
else:
	quality = "HDTV"

#Produce season/episode number in the format of S00E00 from episode_info
episode = ""
for element in episode_info:
	season = "S%0.2d" % int(element[1])
	episode += "E%0.2d" % int(element[2])

#Generate filename from all attributes and sanitize non-alphanumeric characters 
fileout = re.sub("[^0-9a-zA-Z]+", ".", title+"."+season+episode+"."+subtitle_input+"."+height+"p"+"."+quality)+".x262-Antenna.mkv"
print ("Recording filename is %s" % fileout)

#Create symlink to output location
os.symlink(filepath, output+fileout)

#Start Sonarr processing
print ("Start Sonarr processing.")
sonarr_functions.scan(sonarr_ip, sonarr_port, sonarr_api, output+fileout)
print ("********************************FINISH********************************")
