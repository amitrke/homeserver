# SpotDL to Plex Playlist Sync

## Overview

This project provides a Python script that automates the creation of Plex playlists and organizes music files based on Spotify playlist data. It reads configuration from `config.json`, fetches music items from a specified Plex library and folder, and uses the song sequence from a `.spotdl` file to create a new Plex playlist in the correct order. It also supports organizing music files into artist/album/song structure.

## Features

- Reads Plex server connection details and playlist configuration from `config.json`
- Loads Spotify playlist data from a `.spotdl` file (JSON format)
- Organizes music files into artist/album/song structure
- Matches and orders Plex tracks according to the Spotify playlist sequence
- Creates or updates Plex playlists with the matched tracks in the correct order
- Logs any issues with missing metadata, duplicate files, or mismatches
- Supports syncing multiple playlists in one run

## Modes of Operation

The program supports two main modes, selected via command-line arguments:

### 1. `synchfiles`
- Uses `sourcePath` and `destinationPath` from the config file (as string lists, joined with `os.path.join()` for cross-platform compatibility).
- Scans the source folder for music files (no recursion).
- For each music file, extracts playlist track number and song name from the filename.
- Maps this information to the SpotDL file to get the correct artist name and album name for that track (do not rely on the artist name in the filename).
- Copies the song to the destination path, organizing as `artist/album/song`, if it doesn’t already exist.
- If a file is missing metadata, is a duplicate, or the destination file exists with different metadata, logs the issue and skips processing.

### 2. `synchplaylist`
- Reads the SpotDL file for the playlist.
- If the playlist exists in Plex, deletes all songs from it; otherwise, creates a new playlist.
- For each song in the SpotDL file, looks up the Plex item by song name, artist, and album.
- If the Plex item is not found, logs the missing track and continues.
- If found, adds the item to the playlist in the order specified by `list_position` in the SpotDL file.
- No metadata updates are performed for Plex items or albums.

## Usage

```bash
python spotdl_plex_playlist_sync.py synchfiles
python spotdl_plex_playlist_sync.py synchplaylist
```
- The mode (`synchfiles` or `synchplaylist`) must be provided as the first argument.
- All configuration (paths, library, folder, etc.) is read from `config.json`.
- Multiple playlists can be synced in one run (all items in the `playlists` array).

## Requirements

- Python 3.8+
- [plexapi](https://github.com/pkkid/python-plexapi) (`pip install plexapi`)
- Access to your Plex server with a valid token

## Notes

- Track matching relies on metadata; ensure your Plex library is well-tagged for best results.
- The script does not download music; it only organizes existing Plex items into playlists and copies files.
- All logging is done to the console; no log files are generated.
- If any required metadata is missing in the SpotDL file or music files, the issue is logged and the item is skipped.
- No recursive search is performed in source folders.
- No dry-run mode is supported; all actions are performed as described.

## Example Workflow

1. Export a Spotify playlist using SpotDL to a `.spotdl` file.
2. Update `config.json` with your Plex server details, playlist settings, and source/destination paths.
3. Run the script in `synchfiles` mode to organize and copy music files.
4. Run the script in `synchplaylist` mode to create or update the Plex playlist, matching the Spotify playlist order.

---

**Contributions and issues are welcome!**