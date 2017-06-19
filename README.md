# Nebula_RBD_Metadata

Sync OpenNebula template variables to RBD metadata

## Summary

This script will sync custom attributes stored in OpenNebula (on VMs and Images) to metadata stored in Ceph on the corresponding RBD devices (via `rbd image-meta set`). This can be used by OpenNebula administrators to pass data from OpenNebula (Sunstone or CLI) to the Ceph cluster itself, for use by systems or scripts such as backups.

## Details

Currently this will mirror the value of the OpenNebula custom attribute `BACKUP` to the RBD metadata value `backup`, to be used for whitelisting backups; note there is special handling for persistent images (if the VM has BACKUP = True but it has a persistent image that doesn't, set BACKUP true on the image in OpenNebula as well as setting RBD metadata True; if the VM has BACKUP False, defer to the Image's setting).

This will work for persistent and also for non-persistent images.


### Usage

Set BACKUP = True on some VMs (in Sunstone on the main info page for a VM under Attributes) or in onevm update, set `BACKUP="True"``

Then look at the corresponding RBD devices, currently `rbd image-meta list <rbd device>` would be empty (and `image-meta get backup` will return error)

```
# rbd image-meta list one-10
#
# rbd image-meta get  one-10 backup
failed to get metadata backup of image : (2) No such file or directory
rbd: getting metadata failed: (2) No such file or directory
```

After running nebula_rbd_metadata, such as via: `nebula_rbd_metadata --debug runonce` (to run once and print to stdout), now check RBD metadata:

```
# rbd image-meta list one-10
There is 1 metadata on this image.
Key    Value
backup true
# rbd image-meta get one-10 backup
true
```

## Config

Set these environment variables (can also set as CLI flags, see below), key parts are ONE_ADDRESS, the XMLRPC API for OpenNebula, and ONE_SECRET, a path to the credentials (you'll need to make an OpenNebula user for this).

Also note this is designed to be run on a host that already has access to the Ceph cluster that is used by OpenNebula.

```
NEB_RBD_MET_DEBUG          enable debug output
NEB_RBD_MET_SYSLOG         enable logging to syslog, default false (stdout only)
NEB_RBD_MET_ONE_ADDRESS    ONE controller host address
NEB_RBD_MET_ONE_SECRET     ONE credentials to use (e.g. user:key, or
                           /path/to/one_auth), default
                           /var/lib/one/.one/one_auth
NEB_RBD_MET_ONE_PROXY      proxy host to use to connect to ONE controller
NEB_RBD_MET_CEPH_CLUSTER   ceph cluster, default ceph
NEB_RBD_MET_CEPH_USER      ceph user, default admin
```


### Full command-line options

```
usage: nebula_rbd_metadata [-h] [--debug] [--syslog]
                           [--one-address ONE_ADDRESS]
                           [--one-secret ONE_SECRET] [--one-proxy ONE_PROXY]
                           [--ceph-cluster CEPH_CLUSTER]
                           [--ceph-user CEPH_USER]
                           {daemon,runonce,shell} ...

nebula_rbd_metadata - sync nebula variables with rbd metadata

positional arguments:
  {daemon,runonce,shell}
    daemon              run as daemon, sync every INTERVAL seconds
    runonce             run one sync and then exit
    shell               enter debug shell

optional arguments:
  -h, --help            show this help message and exit
  --debug               enable debug output
  --syslog              enable logging to syslog, default false (stdout only)
  --one-address ONE_ADDRESS
                        ONE controller host address
  --one-secret ONE_SECRET
                        ONE credentials to use (e.g. user:key, or
                        /path/to/one_auth), default /var/lib/one/.one/one_auth
  --one-proxy ONE_PROXY
                        proxy host to use to connect to ONE controller
  --ceph-cluster CEPH_CLUSTER
                        ceph cluster, default ceph
  --ceph-user CEPH_USER
                        ceph user, default admin
```
