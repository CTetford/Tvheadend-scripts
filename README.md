# Tvheadend-scripts

What it does
----------

Tvheadend-scripts will provide an interface between Tvheadend and TVDB and Sonarr.

Using the following inputs for Tvheadend's pre/post-recording scripts it will accurately determine the season and episode numbers of a given show from TVDB and forward the file to Sonarr for processing.

Rename default_config.yml to config.yml and modify to suit your setup.

Run the scripts with the following order (e.g. recording-start.py  "%s" "%f" "%b" "%S" "%e")

* "%t" - Title of episode
* "%s" - Subtitle of episode
* "%f" - Filepath of recording
* "%b" - Filename of recording
* "%S" - Current time in seconds from epoch
* "%e" - Error codes

##### Pre-processing Script Sequence:

1. Determine season and episode number from title/subtitle/date.
2. I use Sonarr to organize and download metadata for my episodes, so it will check Sonarr's database to see if it's an existing episode or not. If yes, it will abort the recording. If no, the script ends.

##### Post-processing Sequence:

1. Determine season and episode number as above.
2. Determine quality (HDTV or SDTV) based on video resolution height. If 480p it's SDTV, otherwise assume 720p or 1080p.
3. Parse filename into acceptable Sonarr input, i.e. Title.S01E01.Subtitle.1080p.HDTV.x262.mkv
4. Make a symlink of recording in Sonarr's scanning folder and tell it to scan for a new episode.

##### Requirements:

1. ffprobe is used to determine the recording resolution height.
2. The scripts require the following to be installed using pip3: requests, pyyaml, python-levenshtein

    $ sudo apt-get install python3-pip

    $ sudo pip3 install requests pyyaml python-levenshtein

##### A detailed explanation of the TVDB part:

1. It begins by looking up the title and TVDB returns xml data of any matching shows. 
2. Then it will sequentially look up the title of each show returned and create a sorted list from most similar name to least similar by using the levenshtein function. 
3. It can then look up every episode for the first show on that list, and again use the levenshtein function to find the most likely episode name match. If it finds an episode name with a levenshtein distance >0.7, it will assume it is the correct episode name.
4. If it doesn't find a match for that show, it moves on to the next on the list and continues until it finds a match or runs out.

##### Features:

- [x] It can handle multi-part episodes for premiers or finales, depending on the syntax of the guide data. This should work with both zap2xml and Schedules Direct data.
- [x] It uses fuzzy pattern matching in case TVDB differs from than the guide data by a few characters. 
- [x] It can also handle if TVDB's API returns multiple shows ID's for a given title and sequentially select the most likely match.

##### Planned features:

- [ ] If an episode cannot be matched with a given subtitle (or the subtitle is missing/blank), it should match the TVDB data by airdate.
