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
import sys
import shutil
import re
from plexapi.server import PlexServer

# Read config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

plex_config = config['plex']

baseurl = f"http://{plex_config['host']}:{plex_config['port']}"
token = plex_config['token']
plex = PlexServer(baseurl, token)

def parse_filename(filename):
    # Remove extension
    name = os.path.splitext(os.path.basename(filename))[0]
    # Split by ' - '
    parts = name.split(' - ')
    if len(parts) < 3:
        return None, None, None
    track_number = parts[0].strip()
    artist = parts[1].strip().lower()
    # Join all remaining parts for the title
    title = ' - '.join(parts[2:]).strip().lower()
    return track_number, artist, title

def sanitize_dir_name(name):
    # Remove or replace invalid Windows path characters
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remove any remaining non-alphanumeric characters except spaces and underscores
    name = re.sub(r'[^\w\s]', '', name)
    # Optionally, replace multiple spaces/underscores with a single underscore
    name = re.sub(r'[\s_]+', '_', name).strip('_')
    return name

def process_playlist(plex, playlist_config):
    library_name = playlist_config['library']
    playlist_name = playlist_config['name']

    musicLibrary = plex.library.section(library_name)

    # Read the .spotdl file for this playlist
    spotdl_path = os.path.join(os.path.dirname(__file__), f"{playlist_name}.spotdl")
    if not os.path.exists(spotdl_path):
        print(f"SpotDL file not found: {spotdl_path}")
        return
    with open(spotdl_path, 'r', encoding='utf-8') as f:
        spotdl_data = json.load(f)
    spotdl_songs = spotdl_data.get('songs', [])

    # Build a mapping from list_position to SpotDL song
    spotdl_by_position = {}
    for song in spotdl_songs:
        pos = song.get('list_position')
        if pos is not None:
            spotdl_by_position[str(pos).zfill(2)] = song

    # For each SpotDL song, search for the matching Plex track
    matched_tracks = []
    diff_log = []
    for pos in sorted(spotdl_by_position.keys(), key=lambda x: int(x)):
        song = spotdl_by_position[pos]
        song_name = song.get('name', '').strip().lower()
        album_artist = song.get('album_artist', '').strip().lower()
        song_album = song.get('album_name', '').strip().lower()
        # Search for track in Plex by title only
        plex_tracks = musicLibrary.searchTracks(title=song_name)
        # If no results, try removing (feat. ...) and search again
        if not plex_tracks or len(plex_tracks) == 0:
            alt_song_name = re.sub(r'\s*\(feat\.[^)]+\)', '', song_name, flags=re.IGNORECASE)
            alt_song_name = re.sub(r'\s*\[feat\.[^\]]+\]', '', alt_song_name, flags=re.IGNORECASE)
            plex_tracks = musicLibrary.searchTracks(title=alt_song_name.strip())
        plex_track = None
        for track in plex_tracks:
            # Filter by artist and album using grandparentTitle and parentTitle
            plex_artist = getattr(track, 'grandparentTitle', '').strip().lower()
            plex_album = getattr(track, 'parentTitle', '').strip().lower()
            album_match = True
            if song_album:
                if plex_album != song_album:
                    # Try removing (feat. ...) and [feat. ...] from song_album and compare again
                    alt_song_album = re.sub(r'\s*\(feat\.[^)]+\)', '', song_album, flags=re.IGNORECASE)
                    alt_song_album = re.sub(r'\s*\[feat\.[^\]]+\]', '', alt_song_album, flags=re.IGNORECASE).strip()
                    if plex_album != alt_song_album:
                        album_match = False
            if album_artist and plex_artist != album_artist:
                continue
            if not album_match:
                continue
            plex_track = track
            break
        if plex_track:
            # Compare Plex and SpotDL album/artist info
            plex_album = getattr(plex_track, 'parentTitle', '').strip()
            plex_album_artist = getattr(plex_track, 'grandparentTitle', '').strip()
            spotdl_album = song.get('album_name', '').title().strip()
            spotdl_album_artist = song.get('album_artist', '').title().strip()
            if plex_album.lower() != spotdl_album.lower() or plex_album_artist.lower() != spotdl_album_artist.lower():
                diff_log.append({
                    'track': song.get('name'),
                    'plex_album': plex_album,
                    'spotdl_album': spotdl_album,
                    'plex_album_artist': plex_album_artist,
                    'spotdl_album_artist': spotdl_album_artist
                })
            # Update Plex track metadata from SpotDL info
            updates = {}
            if song.get('artist'): updates['artist'] = song['artist']
            if song.get('album_name'): updates['album'] = song['album_name']
            if song.get('album_artist'): updates['albumArtist'] = song['album_artist']
            if song.get('year'): updates['year'] = song['year']
            if song.get('genres'): updates['genre'] = ', '.join(song['genres'])
            # Only update if there are changes
            if updates:
                try:
                    plex_track.edit(**updates)
                    plex_track.reload()
                except Exception as e:
                    print(f"Failed to update metadata for {song.get('name')}: {e}")
            matched_tracks.append(plex_track)
        else:
            print(f"Not found in Plex: {song_name} by {album_artist} (track number {pos})")
    # Log all detected differences
    if diff_log:
        print("--- Album/Artist Differences Detected ---")
        for entry in diff_log:
            print(f"Track: {entry['track']} | Plex Album: '{entry['plex_album']}' | SpotDL Album: '{entry['spotdl_album']}' | Plex Album Artist: '{entry['plex_album_artist']}' | SpotDL Album Artist: '{entry['spotdl_album_artist']}'")
        print("----------------------------------------")

    if matched_tracks:
        # Check if playlist already exists
        existing_playlist = None
        for pl in musicLibrary.playlists():
            if pl.title == playlist_name:
                existing_playlist = pl
                break
        # If playlist exists, delete the playlist and recreate it with the matched tracks
        if existing_playlist:
            existing_playlist.delete()
        musicLibrary.createPlaylist(playlist_name, items=matched_tracks)
    else:
        print(f"No tracks matched for playlist '{playlist_name}'.")

def normalize_name(name):
    # Remove (feat. ...) and [feat. ...] from name
    name = re.sub(r'\s*\(feat\.[^)]+\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\[feat\.[^\]]+\]', '', name, flags=re.IGNORECASE)
    # Lowercase, remove punctuation, collapse whitespace
    name = name.lower()
    name = re.sub(r'[\W_]+', ' ', name)  # Replace non-word chars with space
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def process_files(playlist_config, spotdl_songs):
    source_path = os.path.join(*playlist_config['sourcePath'])
    dest_path = os.path.join(*playlist_config['destinationPath'])
    delete_files = playlist_config.get('deleteFilesFromDestination', False)
    files = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path, f)) and not f.lower().endswith('.spotdl')]
    # Build SpotDL mapping by normalized track number and song name
    spotdl_map = {}
    copied_count = 0
    skipped_count = 0
    for song in spotdl_songs:
        pos = song.get('list_position')
        name = song.get('name', '')
        norm_name = normalize_name(name)
        if pos is not None and norm_name:
            spotdl_map[(str(pos).zfill(2), norm_name)] = song
        else:
            print(f"Missing list_position or name for song: {song.get('name')}")
    for file in files:
        
        tracknum, _, title = parse_filename(file)
        norm_title = normalize_name(title)
        if not tracknum or not norm_title:
            print(f"File missing track number or song name: {file}")
            skipped_count += 1
            continue
        key = (tracknum, norm_title)
        song = spotdl_map.get(key)
        if not song:
            print(f"No SpotDL mapping for track number {tracknum} and song name '{title}' in file: {file}")
            skipped_count += 1
            continue
        album_artist = song.get('album_artist')
        album = song.get('album_name')
        if not album_artist or not album:
            print(f"No album_artist or album name in SpotDL for track {tracknum} ({title})")
            skipped_count += 1
            continue
        # Sanitize album_artist and album names for directory creation
        safe_album_artist = sanitize_dir_name(album_artist)
        safe_album = sanitize_dir_name(album)
        dest_dir = os.path.join(dest_path, safe_album_artist, safe_album)
        try:
            os.makedirs(dest_dir, exist_ok=True)
        except Exception as e:
            print(f"Failed to create directory {dest_dir}: {e}")
            skipped_count += 1
            continue
        # If config says to delete files, do so before copying
        if delete_files:
            for f in os.listdir(dest_dir):
                file_path = os.path.join(dest_dir, f)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                        print(f"Deleted file from destination: {file_path}")
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")
            delete_files = False
        # Change destination filename to just song name + extension
        ext = os.path.splitext(file)[1]
        dest_file_name = f"{title}{ext}"
        dest_file = os.path.join(dest_dir, dest_file_name)
        src_file = os.path.join(source_path, file)
        if os.path.exists(dest_file):
            print(f"Destination file already exists: {dest_file}")
            skipped_count += 1
            continue
        try:
            shutil.copy2(src_file, dest_file)
            print(f"Copied {src_file} to {dest_file}")
            copied_count += 1
        except Exception as e:
            print(f"Failed to copy {src_file} to {dest_file}: {e}")
            skipped_count += 1
    print(f"Files copied: {copied_count}, Files skipped: {skipped_count}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python spotdl_plex_playlist_sync.py [synchfiles|synchplaylist]")
        sys.exit(1)
    mode = sys.argv[1].lower()
    for playlist_cfg in config['playlists']:
        spotdl_path = os.path.join(os.path.dirname(__file__), f"{playlist_cfg['name']}.spotdl")
        if not os.path.exists(spotdl_path):
            print(f"SpotDL file not found: {spotdl_path}")
            continue
        with open(spotdl_path, 'r', encoding='utf-8') as f:
            spotdl_data = json.load(f)
        spotdl_songs = spotdl_data.get('songs', [])
        if mode == "synchfiles":
            process_files(playlist_cfg, spotdl_songs)
        elif mode == "synchplaylist":
            process_playlist(plex, playlist_cfg)
        else:
            print("Unknown mode. Use 'synchfiles' or 'synchplaylist'.")
            sys.exit(1)
