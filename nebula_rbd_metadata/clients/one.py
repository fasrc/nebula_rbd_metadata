import oca
import os
from nebula_rbd_metadata import exception


class OneClient(object):
    """
    OpenNebula Python client
    """
    def __init__(self, secret=None, address=None, proxy=None):
        if ( secret[0] == '/' ):
            secretfile = secret
            if os.path.isfile(secretfile):
                try:
                    f = open(secretfile,'r')
                    secret = f.readlines()[0].strip('\n')
                    f.close()
                except (IOError, OSError) as e:
                    raise exception.SecretFileError(secretfile, e)
            else:
                e = 'secret file does not exist'
                raise exception.SecretFileError(secretfile, e)
        self._oca = oca.Client(secret=secret, address=address, proxy=proxy)
        self._vm_pool = oca.VirtualMachinePool(self._oca)
        self._image_pool = oca.ImagePool(self._oca)

    def vms(self):
        self._vm_pool.info(filter=-1)
        return self._vm_pool

    def images(self):
        self._image_pool.info(filter=-1)
        return self._image_pool
