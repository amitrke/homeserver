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

baseurl = f"http://{plex_config['host']}:{plex_config['port']}"
token = plex_config['token']
plex = PlexServer(baseurl, token)

def process_playlist(plex, playlist_config):
    library_name = playlist_config['library']
    folder_name = playlist_config['folder']
    playlist_name = playlist_config['name']

    musicLibrary = plex.library.section(library_name)
    folders = musicLibrary.folders()
    # Find the folder named as specified in config
    target_folder = None
    for folder in folders:
        if folder.title.lower() == folder_name.lower():
            print(f"Found folder: {folder.title}")
            target_folder = folder
            break
    if target_folder:
        folder_items = target_folder.fetchItems(target_folder.key)
    else:
        folder_items = []

    # Read the .spotdl file for this playlist
    spotdl_path = os.path.join(os.path.dirname(__file__), f"{playlist_name}.spotdl")
    if not os.path.exists(spotdl_path):
        print(f"SpotDL file not found: {spotdl_path}")
        return
    with open(spotdl_path, 'r', encoding='utf-8') as f:
        spotdl_data = json.load(f)
    spotdl_songs = spotdl_data.get('songs', [])

    # Match Plex tracks to SpotDL songs by name and artist
    matched_tracks = []
    for song in spotdl_songs:
        song_name = song.get('name', '').strip().lower()
        song_artist = song.get('artist', '').strip().lower()
        found = None
        for track in folder_items:
            track_name = getattr(track, 'title', '').strip().lower()
            track_artist = getattr(track, 'artist', '').strip().lower()
            if track_name == song_name and track_artist == song_artist:
                found = track
                break
        if found:
            matched_tracks.append(found)
        else:
            print(f"Not found in Plex: {song_name} by {song_artist}")

    if matched_tracks:
        # Create the playlist with the matched tracks in order
        newPlaylist = musicLibrary.createPlaylist(playlist_name, items=matched_tracks)
        print(f"Playlist '{playlist_name}' created with {len(matched_tracks)} tracks.")
    else:
        print(f"No tracks matched for playlist '{playlist_name}'.")

# Loop through all playlists in config.json
for playlist_cfg in config['playlists']:
    process_playlist(plex, playlist_cfg)
