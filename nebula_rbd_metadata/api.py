from nebula_rbd_metadata import exception
from nebula_rbd_metadata.clients import one
from nebula_rbd_metadata.clients import ceph
from nebula_rbd_metadata.logger import log


class nebula_rbd_metadata(object):
    """
    This class allows to sync between OpenNebula template variables and rbd
    metadata
    """

    def __init__(self, one_kwargs={}, ceph_kwargs={}):
        try:
            self._one = one.OneClient(**one_kwargs)
            self._ceph = ceph.CephClient(**ceph_kwargs)
        except exception.SecretFileError as e:
            e.log()
            raise

    def _check_vm_for_backup(self, vm):
        """
        Checks a vm template variable for BACKUP=true
        """
        if hasattr(vm.user_template, 'backup'):
            if vm.user_template.backup.lower() == 'true':
                return True
        return False

    def _check_for_disks(self, vm):
        if not hasattr(vm.template, 'disks'):
            raise exception.NoDisksError(vm)

    def _get_disk_names(self, vm):
        """
        Returns an array of rbd devices
        """
        vm_id = vm.id
        # log.debug("vm " + str(vm_id))
        disk_array = []
        for disk in vm.template.disks:
            # log.debug(disk)
            if hasattr(disk, 'image_id'):
                disk_array.append('{pool}/one-{image_id}-{vm_id}-{disk_id}'.format(
                        pool=disk.pool_name, image_id=disk.image_id, vm_id=vm_id,
                        disk_id=disk.disk_id))
        return disk_array

    def _check_image_for_backup(self, image):
        """
        Checks for image template variable BACKUP=true
        """
        if hasattr(image.template, 'backup'):
            if image.template.backup.lower() == 'true':
                return True
        return False

    def _get_image_imagespec(self, image):
        """
        Gets the rbd device in imagespec format for an opennebula image
        """
        return image.source

    def sync(self):
        """
        Sync metadata from nebula template variables to rbd metadata
        """
        vms_addedtrue = []
        vms_addedfalse = []
        images_addedtrue = []
        images_addedfalse = []
        for vm in self._one.vms():
            vm_backup_flag = self._check_vm_for_backup(vm)
            try:
                self._check_for_disks(vm)
                for disk_imagespec in self._get_disk_names(vm):
                    log.debug(disk_imagespec)
                    disk_metadata_lower = self._ceph.get_metadata(imagespec=disk_imagespec,
                        key='backup').lower()
                    if vm_backup_flag and disk_metadata_lower != 'true':
                        log.debug('setting disk {imagespec} to backup'
                            ' true'.format(imagespec=disk_imagespec))
                        self._ceph.set_metadata(imagespec=disk_imagespec,
                            key='backup', value='true')
                    if (not vm_backup_flag and disk_metadata_lower == 'true'):
                        log.debug('setting disk {imagespec} to backup'
                            ' false'.format(imagespec=disk_imagespec))
                        self._ceph.set_metadata(imagespec=disk_imagespec,
                            key='backup', value='false')
            except exception.NoDisksError as e:
                e.log(warn=True)
            except exception.CantSetMetadataError as e:
                e.log(warn=True)
        for image in self._one.images():
            image_backup_flag = self._check_image_for_backup(image)
            try:
                image_metadata_lower = self._ceph.get_metadata(imagespec=image.source,
                    key='backup').lower()
                if image_backup_flag and image_metadata_lower != 'true':
                    log.debug('setting image {imagespec} to backup'
                        ' true'.format(imagespec=image.source))
                    self._ceph.set_metadata(imagespec=image.source, key='backup',
                        value='true')
                if (not image_backup_flag and image_metadata_lower == 'true'):
                    log.debug('setting image {imagespec} to backup'
                        ' false'.format(imagespec=image.source))
                    self._ceph.set_metadata(imagespec=image.source, key='backup',
                        value='false')
            except exception.CantSetMetadataError as e:
                e.log(warn=True)
        log.info('done')
