"""
spotdl_plex_playlist_sync.py

This script syncs a Spotify playlist (exported via SpotDL) to a Plex playlist.
It reads configuration from config.json, fetches music items from a specified Plex library and folder,
and uses the song sequence from a .spotdl file to create a new Plex playlist in the correct order.

Usage:
    python spotdl_plex_playlist_sync.py

Requirements:
    - Python 3.8+
    - plexapi (pip install plexapi)
    - Access to your Plex server with a valid token
"""

import json
import os
from plexapi.server import PlexServer

# Read config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

plex_config = config['plex']
playlist_config = config['playlists'][0]  # Only using the first playlist for now

baseurl = f"http://{plex_config['host']}:{plex_config['port']}"
token = plex_config['token']
plex = PlexServer(baseurl, token)

library_name = playlist_config['library']
folder_name = playlist_config['folder']
playlist_name = playlist_config['name']

englishMusicLibrary = plex.library.section(library_name)

folders = englishMusicLibrary.folders()
# Find the folder named as specified in config
usTopFolder = None
for folder in folders:
    if folder.title.lower() == folder_name.lower():
        print(f"Found folder: {folder.title}")
        usTopFolder = folder
        break
if usTopFolder:
    usTopFolder_items = usTopFolder.fetchItems()
else:
    usTopFolder_items = []
item = None
for track in usTopFolder.items():
    if track.title.lower() == 'back to friends':
        item = track
        break
if item:
    # Create the playlist with the item
    newPlaylist = englishMusicLibrary.createPlaylist(playlist_name, items=[item])
    print("Playlist created and item added.")
else:
    print("Track 'back to friends' not found in the folder.")
