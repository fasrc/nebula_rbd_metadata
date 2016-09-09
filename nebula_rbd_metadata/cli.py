import argparse

from nebula_rbd_metadata import api
from nebula_rbd_metadata import utils
from nebula_rbd_metadata import logger
from nebula_rbd_metadata import monitor


def daemon(args, one_args, ceph_args):
    mon = monitor.nebula_rbd_metadata_monitor(one_kwargs=one_args,
        ceph_kwargs=ceph_args)
    mon.run(args.interval)


def runonce(args, one_args, ceph_args):
    nebula_rbd_metadata = api.nebula_rbd_metadata(one_kwargs=one_args,
        ceph_kwargs=ceph_args)
    nebula_rbd_metadata.sync()

def shell(args, one_args, ceph_args):
    nebula_rbd_metadata_monitor = monitor.nebula_rbd_metadata_monitor(
        one_kwargs=one_args, ceph_kwargs=ceph_args)
    oneclient = nebula_rbd_metadata_monitor._one
    ns = dict(nebula_rbd_metadata_monitor=nebula_rbd_metadata_monitor,
              oneclient=oneclient, log=logger.log)
    utils.shell(local_ns=ns)


def main(args=None):
    parser = argparse.ArgumentParser(
        description='nebula_rbd_metadata - sync nebula variables with'
            ' rbd metadata')
    parser.add_argument('--debug', required=False,
                        action='store_true', default=False,
                        help='ONE controller host address')

    parser.add_argument('--one-address', required=False,
                        help='ONE controller host address')
    parser.add_argument('--one-secret', required=False,
                        help='ONE credentials to use (e.g. user:key, or'
                        ' /path/to/one_auth)')
    parser.add_argument('--one-proxy', required=False,
                        help='proxy host to use to connect to ONE controller')
    parser.add_argument('--ceph-cluster', required=False, default='ceph',
                        help='ceph cluster')
    parser.add_argument('--ceph-user', required=False, default='admin',
                        help='ceph user')

    subparsers = parser.add_subparsers()

    daemon_parser = subparsers.add_parser('daemon')
    daemon_parser.set_defaults(func=daemon)
    daemon_parser.add_argument(
        '-i', '--interval', required=False, type=int, default=60,
        help="how often in seconds to poll ONE and update RBD metadata")

    runonce_parser = subparsers.add_parser('runonce')
    runonce_parser.set_defaults(func=runonce)


    shell_parser = subparsers.add_parser('shell')
    shell_parser.set_defaults(func=shell)

    args = parser.parse_args(args=args)

    logger.configure_nebula_rbd_metadata_logging(debug=args.debug)

    args_dict = vars(args)
    one_args = utils.get_kwargs_from_dict(args_dict, 'one_')
    ceph_args = utils.get_kwargs_from_dict(args_dict, 'ceph_')

    args.func(args, one_args, ceph_args)
