# Connect to transmission daemon and get torrent information
import transmissionrpc
from transmissionrpc import Client, TransmissionError
import argparse
import os

def get_torrents(host, port, username=None, password=None):
    """
    Connect to the Transmission daemon and retrieve torrent information.
    
    :param host: Hostname or IP address of the Transmission daemon.
    :param port: Port number of the Transmission daemon.
    :param username: Optional username for authentication.
    :param password: Optional password for authentication.
    :return: List of torrents with their details.
    """
    try:
        client = Client(host, port, user=username, password=password)
        torrents = client.get_torrents()
        return torrents
    except TransmissionError as e:
        print(f"Error connecting to Transmission daemon: {e}")
        return []
    
def get_torrent_info(torrent):
    """
    Extract relevant information from a torrent object.
    
    :param torrent: Torrent object from Transmission.
    :return: Dictionary with torrent details.
    """
    return {
        'id': torrent.id,
        'name': torrent.name,
        'status': torrent.status,
        'progress': torrent.progress,
        'downloaded': torrent.downloadedEver,
        'uploaded': torrent.uploadedEver,
        'ratio': torrent.uploadRatio,
        'size': torrent.totalSize,
        'files': [file['name'] for file in torrent.files().values()],
    }

def get_all_torrents_info(host, port, username=None, password=None):
    """
    Retrieve information for all torrents from the Transmission daemon.
    
    :param host: Hostname or IP address of the Transmission daemon.
    :param port: Port number of the Transmission daemon.
    :param username: Optional username for authentication.
    :param password: Optional password for authentication.
    :return: List of dictionaries with torrent details.
    """
    torrents = get_torrents(host, port, username, password)
    return [get_torrent_info(torrent) for torrent in torrents]

def check_completed_torrents(torrents, download_path):
    """
    Check which torrents have completed downloading.
    Also check if the download path has files/directories that are not in the torrent list.
    :param torrents: List of torrent dictionaries.
    :param download_path: Path where completed torrents are stored.
    :return: List of completed torrents.
    """
    completed_torrents = [torrent for torrent in torrents if torrent['status'] == 'seeding' or torrent['status'] == 'finished']
    # Check for any files in the download path that are not in the completed torrents
    existing_files = set(os.listdir(download_path))
    torrent_files = set(file for torrent in completed_torrents for file in torrent['files'])
    missing_files = existing_files - torrent_files
    if missing_files:
        print(f"Warning: The following files are not tracked by Transmission:")
        for file in missing_files:
            print(f" - {file}")
    return completed_torrents

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transmission Torrent Viewer")
    parser.add_argument("--host", type=str, default="ds220plus", help="Hostname or IP address of the Transmission daemon")
    parser.add_argument("--downloadpath", type=str, default="./downloads/", help="Download path for torrents (default: ./downloads/)")
    parser.add_argument("--port", type=int, default=9091, help="Port number of the Transmission daemon")
    parser.add_argument("--username", default=None, type=str, help="Username for authentication")
    parser.add_argument("--password", default=None, type=str, help="Password for authentication")
    
    args = parser.parse_args()
    
    # Create download directory if it doesn't exist
    os.makedirs(args.downloadpath, exist_ok=True)
    
    print(f"Connecting to Transmission daemon at {args.host}:{args.port}")
    print(f"Download path: {args.downloadpath}")

    torrents_info = get_all_torrents_info(args.host, args.port, args.username, args.password)
    completed_torrents = check_completed_torrents(torrents_info, args.downloadpath)
    # for torrent in completed_torrents:
    #     print(torrent)