import oca


class OneClient(object):
    """
    OpenNebula Python client
    """
    def __init__(self, secret=None, address=None, proxy=None):
        self._oca = oca.Client(secret=secret, address=address, proxy=proxy)
        self._vm_pool = oca.VirtualMachinePool(self._oca)
        self._image_pool = oca.ImagePool(self._oca)

    def vms(self):
        self._vm_pool.info(filter=-1)
        return self._vm_pool

    def images(self):
        self._image_pool.info(filter=-1)
        return self._image_pool
