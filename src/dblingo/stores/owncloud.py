import owncloud

from dblingo.settings import NEXTCLOUD_LINK


class OwncloudStore:
    def __init__(self):
        self.client = owncloud.Client.from_public_link(NEXTCLOUD_LINK)

    def upload(self, file_path):
        self.client.put_file(file_path, file_path)
