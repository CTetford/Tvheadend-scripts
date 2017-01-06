#!/usr/bin/python3
#This module will read the subtitle input and split into an episode list if it is a multi-episode recording.
#Otherwise it will return a list with a single entry or the original subtitle.

def verify(subtitle_input):
	subtitle = []
	#Search for either "/" or "; " as a delimiter between multi-episode recordings. Split string into list of individual episodes.
	if "/" in subtitle_input or "; " in subtitle_input:
		if "/" in subtitle_input:
			subtitle = subtitle_input.split("/")
		elif "; " in subtitle_input:
			subtitle = subtitle_input.split("; ")
	else:
		#If recording is a single episode, return the single subtitle as a single-element list to maintain syntax consistency.
		subtitle.append (subtitle_input)
	return subtitle