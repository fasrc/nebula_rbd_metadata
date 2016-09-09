from nebula_rbd_metadata.logger import log


class nebula_rbd_metadataException(Exception):
    def __init__(self, *args):
        self.args = args
        self.msg = args[0]

    def __str__(self):
        return self.msg

    def explain(self):
        return '%s: %s' % (self.__class__.__name__, self.msg)

    def log(self, warn=False, show_tb=False):
        if warn:
            log.warn(self.explain(), exc_info=show_tb)
        else:
            log.error(self.explain(), exc_info=show_tb)


class NoDisksError(nebula_rbd_metadataException):
    """
    Raised when a VM doesn't have any disks
    """
    def __init__(self, vm):
        self.msg = "No disks found for VM {id}: {vm}".format(vm=vm.name,
                                                             id=vm.id)


class CantSetMetadataError(nebula_rbd_metadataException):
    def __init__(self, imagespec, key, value, returncode, stderr):
        self.msg = ("Metadata could not be set for device {imagespec}:"
                    " {key} {value}: exit code {returncode} stderr"
                    " {stderr}".format(imagespec=imagespec, key=key,
                                           value=value, returncode=returncode,
                                           stderr=stderr))

class SecretFileError(nebula_rbd_metadataException):
    def __init__(self, secretfile, e):
        self.msg = ("Error reading OpenNebula secret file {secretfile} with"
                    " error: {e}".format(secretfile=secretfile, e=e))
