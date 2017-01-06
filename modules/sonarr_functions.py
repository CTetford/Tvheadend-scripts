#!/usr/bin/python3
#This script will determine the season and episode number of a TV show given the Title and episode Subtitle. 
#If it cannot find the correct episode from the subtitle, the airdate will alternatively be used.
import requests
import json

def get_sonarr_id(sonarr_ip, sonarr_port, sonarr_api, tvdb_id):
	#Get series data from Sonarr database and look for matching show
	print ("Getting Sonarr show ID.")
	series_json = json.loads(requests.get("http://%s:%s/api/series" % (sonarr_ip, sonarr_port), headers={"X-Api-Key":sonarr_api}).text)
	#Get sonarr_id by matching tvdb_id
	for series in series_json:
		if str(series["tvdbId"]) == tvdb_id:
			sonarr_id = series["id"]
			break
	try:
		sonarr_id
	except NameError:
		#Show not found in Sonarr database
		raise NameError("Show not found in Sonarr database. Not marked as unmonitored.")
		return
	else:
		print ("Found Sonarr ID: \"%s\"." % sonarr_id)
		return sonarr_id

def get_episode_id(sonarr_ip, sonarr_port, sonarr_api, sonarr_id, episode_info):
	#Get sonarr episode id and check if file exists already
	season = episode_info[1]
	episode = episode_info[2]
	show_json = json.loads(requests.get("http://%s:%s/api/episode/" % (sonarr_ip, sonarr_port), params = {"seriesID":sonarr_id}, headers={"X-Api-Key":sonarr_api}).text)
	for show in show_json:
		if str(show["episodeNumber"]) == episode and str(show["seasonNumber"]) == season:
			hasfile = show["hasFile"]
			episode_id = show["id"]
			break
	try:
		episode_id
	except NameError:
		raise NameError("Episode not found in Sonarr episode list for sonarr_id %s." % sonarr_id)
		return
	else:
		return (episode_id, hasfile)

def unmonitor(sonarr_ip, sonarr_port, sonarr_api, sonarr_id, episode_id):
	#Send sonarr_id and episode_id to Sonarr to mark as unmonitored.
	r = requests.put("http://%s:%s/api/episode/" % (sonarr_ip, sonarr_port), json = {"seriesId": sonarr_id, "id": episode_id, "monitored": "false"}, headers={"X-Api-Key":sonarr_api})
	print (r.content.decode("utf-8"))
	return

def scan(sonarr_ip, sonarr_port, sonarr_api, path):
	#Initiate Sonarr scan
	r = requests.post("http://%s:%s/api/command/" % (sonarr_ip, sonarr_port), json = {"name": "downloadedepisodesscan", "path": path}, headers={"X-Api-Key":sonarr_api})
	print (r.content.decode("utf-8"))
	return