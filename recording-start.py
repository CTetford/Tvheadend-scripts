#!/usr/bin/python3

import sys
import time
import requests
import os

from xml.etree import ElementTree
import yaml

from modules import episode_and_season
from modules import sonarr_functions
from modules import tvheadend_functions
from modules import subtitle_verify

config = yaml.safe_load(open(os.path.split(sys.argv[0])[0]+"/config.yml"))

title = sys.argv[1]
subtitle_input = sys.argv[2]
filepath = sys.argv[3]
filename = sys.argv[4]
date_epoch = sys.argv[5]
error = sys.argv[6]
#Convert tvheadend's time since epoch airdate to %Y-%m-%d format
airdate = time.strftime('%Y-%m-%d', time.localtime(int(date_epoch)))

#Import Parameters
pushbullet_api = config["pushbullet"]["api"]
tvdb_api = config["tvdb"]["api"]
sonarr_api = config["sonarr"]["api"]
sonarr_ip = config["sonarr"]["host"]
sonarr_port = config["sonarr"]["port"]
tvheadend_ip = config["tvheadend"]["host"]
tvheadend_port = config["tvheadend"]["port"]
tvheadend_user = config["tvheadend"]["user"]
tvheadend_pass = config["tvheadend"]["pass"]

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
	try:
		episode_info = episode_and_season.get_episode_by_airdate(tvdb_api, title, airdate, tvdb_id_list)
	except NameError as err:
		requests.post("https://api.pushbullet.com/v2/pushes", data = {"type":"note", "body":err.args, "title":"Tvheadend"}, headers={"Access-Token":pushbullet_api})
		print(err.args)
		quit()
	else:
		print ("Episode info found by airdate:")
		print (episode_info)
		requests.post("https://api.pushbullet.com/v2/pushes", data = {"type":"note", "body":"Episode found by airdate. %s" %(episode_info), "title":"Tvheadend"}, headers={"Access-Token":pushbullet_api})
		tvdb_id = episode_info[0][3]
else:
	print ("Episode info found by subtitle:")
	print (episode_info)
	tvdb_id = episode_info[0][3]

#Prevent Sonarr from downloading episode while recording is taking place. 
print ("Looking up show in Sonarr...")
try:
	sonarr_id = sonarr_functions.get_sonarr_id(sonarr_ip, sonarr_port, sonarr_api, tvdb_id)
except NameError as err:
	requests.post("https://api.pushbullet.com/v2/pushes", data = {"type":"note", "body":err.args, "title":"Tvheadend"}, headers={"Access-Token":pushbullet_api})
	print(err.args)
	quit()

file_info = []
print ("Looking up episode in Sonarr...")
for element in episode_info: #For each episode in episode list, look up sonarr episode ID.
	file_info.append (sonarr_functions.get_episode_id(sonarr_ip, sonarr_port, sonarr_api, sonarr_id, element))
for index in file_info: #Check if file has been downloaded. If yes, cancel recording. If no, prevent download.
	if index[1]:
		print ("Sonarr has episode downloaded. Cancelling recording.")
		#file_info[hasFile] is True, cancel recording
		time.sleep(5)
		tvheadend_functions.cancel_recording(tvheadend_ip, tvheadend_port, tvheadend_user, tvheadend_pass, title)
		break
	elif not index[1]:
		#file_info[hasFile] is False, unmonitor that episode in Sonarr.
		print ("Sonarr does not have episode. Marking as unmonitored.")
		sonarr_functions.unmonitor(sonarr_ip, sonarr_port, sonarr_api, sonarr_id, index[0])
print ("********************************FINISH********************************")
