from owncloud import Client

from dblingo.settings import NEXTCLOUD_LINK
from . import AbstractRemote

class OwncloudRemote(AbstractRemote):
    def __init__(self):
        if not NEXTCLOUD_LINK or NEXTCLOUD_LINK == '' or NEXTCLOUD_LINK == 'your_link_here':
            print("NEXTCLOUD_LINK not set, skipping owncloud upload")
            self.client = None
            return
        self.client = Client.from_public_link(NEXTCLOUD_LINK)

    def upload(self, file_path):
        if not self.client:
            return
        self.client.put_file(file_path, file_path)
