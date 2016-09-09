import subprocess
import shlex
from nebula_rbd_metadata import exception

GET_METADATA_COMMAND = ('rbd --cluster {cluster} --id {user} image-meta'
                        ' get {imagespec} {key}')

SET_METADATA_COMMAND = ('rbd --cluster {cluster} --id {user} image-meta'
                        ' set {imagespec} {key} {value}')


class CephClient(object):
    """
    Ceph client for setting RBD metadata
    (Note, Python librbd bindings do not support rbd metadata yet)
    """
    def __init__(self, cluster=None, user=None):
        self._cluster = cluster
        self._user = user


    def get_metadata(self, imagespec, key):
        """
        Get RBD metadata for a device
        """
        command = shlex.split(GET_METADATA_COMMAND.format(
            cluster=self._cluster, user=self._user,
            imagespec=imagespec, key=key))
        p = subprocess.Popen(command, stdout=subprocess.PIPE,
            stderr = subprocess.PIPE)
        stdout, stderr = p.communicate()
        value = stdout.strip('\n')
        if p.returncode != 0:
            # this is OK if a vm doesn't have any metadata yet
            pass
        return value


    def set_metadata(self, imagespec, key, value):
        """
        Set RBD metadata for a device
        """
        command = shlex.split(SET_METADATA_COMMAND.format(
            cluster=self._cluster, user=self._user,
            imagespec=imagespec, key=key, value=value))
        p = subprocess.Popen(command, stdout=subprocess.PIPE,
            stderr = subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise exception.CantSetMetadataError(imagespec, key, value, p.returncode, stderr)
        return True
