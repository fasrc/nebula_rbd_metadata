import time

from nebula_rbd_metadata import api


class nebula_rbd_metadata_monitor(api.nebula_rbd_metadata):
    """
    Daemon that syncs OpenNebula with rbd metadata
    """
    def run(self, interval=60):
        while True:
            self.sync()
            time.sleep(interval)
