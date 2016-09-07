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


class CantSetMetadataErrror(nebula_rbd_metadataException):
    def __init__(self, pool, device, key, value):
        self.msg = ("Metadata could not be set for device {pool}/{device}:"
                    "{key} {value}".format(pool=pool, device=device, key=key,
                                           value=value))
