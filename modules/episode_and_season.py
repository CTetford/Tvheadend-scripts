#!/usr/bin/python3
#This script will determine the season and episode number of a TV show given the Title and episode Subtitle. 
#If it cannot find the correct episode from the subtitle, the airdate will alternatively be used.
import requests

from xml.etree import ElementTree
import Levenshtein

def get_tvdb_id(title):
	tvdb_id_list = []
	#Get tvdb ID(s) for show based on title. TVDB may return multiple entries for a given title.
	print ("Looking for TVDB series ID based on given title of \"%s\"." % title)
	print ("Getting show information. Attemping URL \"http://thetvdb.com/api/GetSeries.php?seriesname=%s\"" % title)
	tvdb_xml = ElementTree.fromstring(requests.get("http://thetvdb.com/api/GetSeries.php?seriesname=%s" % title).content)
	for entry in tvdb_xml.findall(".//Series"):
		#Compare each series result to title and calculate levenshtein ratio
		levenshtein = Levenshtein.ratio(title, entry.find("SeriesName").text)
		tvdb_id_list.append ([entry.find("seriesid").text, entry.find("SeriesName").text, levenshtein])
	for entry in tvdb_id_list:
		print ("Series ID \"%s\" found for \"%s\"." %(entry[0], entry[1]))
	if tvdb_id_list == []:
		raise NameError("tvdb_id could not be determined. Episode and season not found.")
		return
	else:
		#Sort list by levenshtien ratio to order by most likely match
		tvdb_id_list = sorted(tvdb_id_list, key=lambda x: x[2], reverse=True)
		return (tvdb_id_list)

def get_episode_by_subtitle(tvdb_api, title, subtitle_input, tvdb_id_list):
	result = []
	for subtitle in subtitle_input:
		tvdb_id_list_flag = False
		#Search each series based on the returned tvdb ID's for the correct episode name (subtitle).
		series_results = []
		for entry in tvdb_id_list:
			tvdb_id = entry[0] #Current tvdb_id
			episodes = []
			episodes_xml = ElementTree.fromstring(requests.get("http://thetvdb.com/api/%s/series/%s/all" %(tvdb_api, tvdb_id)).content)
			for entry in episodes_xml.findall(".//Episode"):
				#Get the name, season number, episode number, and Levenshtein value comparison of all episodes
				if entry.find("EpisodeName").text != None:
					levenshtein = Levenshtein.ratio(subtitle, entry.find("EpisodeName").text)
					if levenshtein == 1:
						#If an exact episode name match has been found (levenshtein = 1), break tvdb_id_list loop
						tvdb_id_list_flag = True
						episodes = [[entry.find("EpisodeName").text, entry.find("SeasonNumber").text, entry.find("EpisodeNumber").text, tvdb_id, levenshtein]]
						break
					else:
						episodes.append ([entry.find("EpisodeName").text, entry.find("SeasonNumber").text, entry.find("EpisodeNumber").text, tvdb_id, levenshtein])
			#If an exact episode name match has been found, break tvdb_id_list loop
			if tvdb_id_list_flag:
				series_results =  [(max(episodes,key=lambda x:x[4]))]
				break
			if episodes != []:
				#Search for most likely within that given series and append to result list
				series_results.append (max(episodes,key=lambda x:x[4]))
		#Return the result of the highest levenshtein value. If the closestly matched episode is less than 70% confidence, episode has not been found.
		if max(series_results,key=lambda x:x[4])[4] < 0.7:
			raise NameError("Episode match less than 70% confidence. Episode subtitle not found.")
			return
		else:
			result.append (max(series_results,key=lambda x:x[4]))
	return result
	
def get_episode_by_airdate(tvdb_api, title, airdate, tvdb_id_list):
	result = []
	tvdb_id_list_flag = False
	#Search each series based on the returned tvdb ID's for the correct airdate (YYYY-MM-DD).
	series_results = []
	for entry in tvdb_id_list:
		tvdb_id = entry[0]
		episodes_xml = ElementTree.fromstring(requests.get("http://thetvdb.com/api/%s/series/%s/all" %(tvdb_api, tvdb_id)).content)
		for entry in episodes_xml.findall(".//Episode"):
			if entry.find("FirstAired").text == airdate:
				#Return episode in list-within-list to be consistent with get_episode_by_subtitle function
				episode = [[entry.find("EpisodeName").text, entry.find("SeasonNumber").text, entry.find("EpisodeNumber").text, tvdb_id]]
				return episode
	raise NameError("Episode airdate not found.")
	return