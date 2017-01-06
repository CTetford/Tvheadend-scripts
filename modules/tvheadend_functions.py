#!/usr/bin/python3
#This script will determine the season and episode number of a TV show given the Title and episode Subtitle. 
#If it cannot find the correct episode from the subtitle, the airdate will alternatively be used.
import requests
import json

def cancel_recording(tvheadend_ip, tvheadend_port, tvheadend_user, tvheadend_pass, title):
	#Use Tvheadend API to stop recording based on Title and Subtitle.
	tvheadend_response = requests.get("http://%s:%s/api/dvr/entry/grid_upcoming" % (tvheadend_ip, tvheadend_port), auth=(tvheadend_user, tvheadend_pass))
	tvheadend_json = json.loads(tvheadend_response.text)
	for dvr_entry in tvheadend_json["entries"]:
		if str(dvr_entry["disp_title"]) == title:
			#If matching display title is found, remove recording from DVR entries by matching recording uuid.
			tvheadend_response = requests.get("http://%s:%s/api/dvr/entry/remove" % (tvheadend_ip, tvheadend_port), auth=(tvheadend_user, tvheadend_pass), params={"uuid":dvr_entry["uuid"]})
			print ("Recording found in DVR list, entry removed.")
	return ("Recording attemped to be removed.")