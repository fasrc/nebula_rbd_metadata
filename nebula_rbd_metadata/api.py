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

    def _get_disks(self, vm):
        """
        Returns an array of rbd devices
        """
        vm_id = vm.id
        # log.debug("vm " + str(vm_id))
        disk_array = []
        for disk in vm.template.disks:
            # log.debug(disk)
            if (hasattr(disk, 'image_id') and hasattr(disk, 'clone') and
                    hasattr(disk, 'source') and disk.clone == 'NO'):
                disk_array.append((disk.source, disk.image_id))
            elif hasattr(disk, 'image_id') and hasattr(disk, 'pool_name'):
                disk_array.append((
                        '{pool}/one-{image_id}-{vm_id}-{disk_id}'.format(
                            pool=disk.pool_name, image_id=disk.image_id,
                            vm_id=vm_id, disk_id=disk.disk_id), False))
            elif hasattr(disk, 'image_id') and hasattr(disk, 'source'):
                disk_array.append(('{source}-{vm_id}-{disk_id}'.format(
                    source=disk.source, vm_id=vm_id, disk_id=disk.disk_id),
                    False))
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

    def _set_imagespec_backup_metadata(self, imagespec, value):
        log.info(
            'setting disk {imagespec} to backup'
            ' {value}'.format(imagespec=imagespec, value=value))
        self._ceph.set_metadata(
            imagespec=imagespec, key='backup',
            value=value)

    def sync(self):
        """
        Sync metadata from nebula template variables to rbd metadata
        """
        vms = self._one.vms()
        images = self._one.images()
        for vm in vms:
            vm_backup_flag = self._check_vm_for_backup(vm)
            log.debug(
                "checking vm id: {id} name: '{name}'"
                " has nebula variable BACKUP={neb_backup}".format(
                    id=vm.id, name=vm.name, neb_backup=vm_backup_flag))
            try:
                self._check_for_disks(vm)
                for (disk_imagespec, persistent_id) in self._get_disks(vm):
                    try:
                        log.debug("checking disk {imagespec}".format(
                            imagespec=disk_imagespec))
                        disk_metadata_lower = self._ceph.get_metadata(
                            imagespec=disk_imagespec, key='backup').lower()
                        if not vm_backup_flag and persistent_id:
                            # vm not set for backup has a persistent disk
                            # so ignore here
                            log.debug("skipping disk {id}, defer to image"
                                      " backup flag".format(id=persistent_id))
                            continue
                        elif vm_backup_flag and persistent_id:
                            # vm set for backup with a persistent disk
                            # so update the image
                            image = [image for image in images if
                                     image.id == persistent_id][0]
                            image_backup_flag = self._check_image_for_backup(
                                image)
                            if not image_backup_flag:
                                log.debug("adding backup true to image"
                                          " {id}".format(id=image.id))
                                image.update('<TEMPLATE><BACKUP>True</BACKUP>'
                                             '</TEMPLATE>', Merge=True)
                        if vm_backup_flag and disk_metadata_lower != 'true':
                            # vm set for backup and disk doesn't have
                            # metadata true
                            self._set_imagespec_backup_metadata(
                                disk_imagespec, 'true')
                            continue
                        if (not vm_backup_flag and
                                disk_metadata_lower == 'true'):
                            # vm set to not get backed up and disk is
                            # set for backup
                            self._set_imagespec_backup_metadata(
                                disk_imagespec, 'false')
                            continue
                        log.debug(
                            "OK vmid: {id} rbd disk: {disk}"
                            " already has rbd metadata"
                            " backup='{rbd_backup}'".format(
                                id=vm.id, disk=disk_imagespec,
                                rbd_backup=disk_metadata_lower))
                    except exception.CantSetMetadataError as e:
                        e.log(warn=True)
            except exception.NoDisksError as e:
                e.log(warn=True)
        for image in images:
            image_backup_flag = self._check_image_for_backup(image)
            log.debug(
                "checking image id: {id} name: '{name}' source: {source}"
                " has nebula variable BACKUP={neb_backup}".format(
                    id=image.id, name=image.name, source=image.source,
                    neb_backup=image_backup_flag))
            try:
                if not image_backup_flag and image.vm_ids:
                    log.debug("skipping image {id}, defer to vm backup"
                              " flag".format(id=image.id))
                    continue
                image_metadata_lower = self._ceph.get_metadata(
                    imagespec=image.source, key='backup').lower()
                if image_backup_flag and image_metadata_lower != 'true':
                    # image set to be backed up but rbd doesn't have
                    # metadata true
                    self._set_imagespec_backup_metadata(image.source, 'true')
                    continue
                if (not image_backup_flag and image_metadata_lower == 'true'):
                    # image set to be not backed up and rbd has metadata true
                    self._set_imagespec_backup_metadata(image.source, 'false')
                    continue
                log.debug(
                    "OK image: {id} rbd device: {source}"
                    " already has rbd metadata backup='{rbd_backup}'".format(
                        id=image.id,
                        source=image.source,
                        rbd_backup=image_metadata_lower))
            except exception.CantSetMetadataError as e:
                e.log(warn=True)
        log.info('done')
