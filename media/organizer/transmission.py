# Connect to transmission daemon and get torrent information
import transmissionrpc
from transmissionrpc import Client, TransmissionError

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

if __name__ == "__main__":
    host = 'ds220plus'
    port = 9091
    username = None  # Replace with your username if needed
    password = None  # Replace with your password if needed

    torrents_info = get_all_torrents_info(host, port, username, password)
    for torrent in torrents_info:
        print(torrent)