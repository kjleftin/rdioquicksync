Rdio Quick Sync
=============

Rdio Quick Sync is an interactive command line utility for syncing albums from Rdio.

## Features
* Page through all your albums and select / deselect what you'd like synced to your mobile device.
* Filter based on a search string.
* Add all or clear all synced music with one command.
* Sort your albums by album name or artist name.
* See how many total albums you have synced to your mobile device.

## Commandline Options
	    usage: sync.py [-h] [--fetch_token] [--fake]
	    
	    Interactive command line interface for syncing music from Rdio.
	    
	    optional arguments:
	      -h, --help     show this help message and exit
	      --fetch_token  Fetch a fresh OAuth token. If not provided, will expect TOKEN
	          to be defined in rdio_consumer_credentials.py
	      --fake         Use a fake set of albums. (For testing only)
