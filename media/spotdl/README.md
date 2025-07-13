# SpotDL to Plex Playlist Sync

## Overview

This project provides a Python script that automates the creation of Plex playlists based on Spotify playlist data. It reads configuration from config.json, fetches music items from a specified Plex library and folder, and uses the song sequence from a `.spotdl` file to create a new Plex playlist in the correct order.

## Features

- Reads Plex server connection details and playlist configuration from config.json
- Loads Spotify playlist data from a `.spotdl` file (JSON format)
- Fetches music items from the specified Plex library and folder
- Matches and orders Plex tracks according to the Spotify playlist sequence
- Creates a new Plex playlist with the matched tracks in the correct order

## How It Works

1. **Configuration**  
   - The script reads config.json for Plex server details and playlist settings.
   - Example:
     ```json
     {
         "plex": {
             "host": "ds220plus",
             "port": 32400,
             "token": "your_plex_token"
         },
         "playlists": [
             {
                 "name": "ustop50",
                 "library": "English Music",
                 "folder": "ustop50"
             }
         ]
     }
     ```

2. **Spotify Playlist Data**  
   - The script loads the `.spotdl` file (e.g., ustop50.spotdl), which contains the Spotify playlist and song metadata.

3. **Plex Library Access**  
   - Connects to the Plex server using the provided host, port, and token.
   - Accesses the specified library and folder to fetch available music items.

4. **Track Matching and Ordering**  
   - Matches Plex tracks to Spotify tracks using metadata (e.g., track name, artist).
   - Orders the matched Plex tracks according to the sequence in the `.spotdl` file.

5. **Playlist Creation**  
   - Creates a new Plex playlist with the matched and ordered tracks.

## Usage

1. Place your config.json and `.spotdl` file in the project directory.
2. Run the Python script:
   ```bash
   python plex.py
   ```
3. The script will create a new Plex playlist named as specified in config.json, containing the tracks in the order from the `.spotdl` file.

## Requirements

- Python 3.8+
- [plexapi](https://github.com/pkkid/python-plexapi) (`pip install plexapi`)
- Access to your Plex server with a valid token

## Notes

- Track matching relies on metadata; ensure your Plex library is well-tagged for best results.
- The script does not download music; it only organizes existing Plex items into playlists.

## Example Workflow

1. Export a Spotify playlist using SpotDL to a `.spotdl` file.
2. Update config.json with your Plex server details and playlist settings.
3. Run the script to sync the playlist to Plex.

---

**Contributions and issues are welcome!**