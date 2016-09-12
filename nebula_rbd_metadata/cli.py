import argparse

from nebula_rbd_metadata import api
from nebula_rbd_metadata import utils
from nebula_rbd_metadata import logger
from nebula_rbd_metadata import monitor
import os


def daemon(args, one_args, ceph_args):
    mon = monitor.nebula_rbd_metadata_monitor(
        one_kwargs=one_args, ceph_kwargs=ceph_args)
    mon.run(args.interval)


def runonce(args, one_args, ceph_args):
    nebula_rbd_metadata = api.nebula_rbd_metadata(
        one_kwargs=one_args, ceph_kwargs=ceph_args)
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
                        action='store_true',
                        default=(
                            os.environ.get(
                                'NEB_RBD_MET_DEBUG',
                                'False').lower() == 'true'),
                        help='enable debug output')
    parser.add_argument('--syslog', required=False,
                        action='store_true',
                        default=(
                            os.environ.get(
                                'NEB_RBD_MET_SYSLOG',
                                'False').lower() == 'true'),
                        help=(
                            'enable logging to syslog, default false'
                            ' (stdout only)'))
    parser.add_argument('--one-address', required=False,
                        default=(
                            os.environ.get('NEB_RBD_MET_ONE_ADDRESS')),
                        help='ONE controller host address')
    parser.add_argument('--one-secret', required=False,
                        default=(
                            os.environ.get(
                                'NEB_RBD_MET_ONE_SECRET',
                                '/var/lib/one/.one/one_auth')),
                        help=(
                            'ONE credentials to use (e.g. user:key, or'
                            ' /path/to/one_auth),'
                            ' default /var/lib/one/.one/one_auth'))
    parser.add_argument('--one-proxy', required=False,
                        default=(
                            os.environ.get('NEB_RBD_MET_ONE_PROXY')),
                        help='proxy host to use to connect to ONE controller')
    parser.add_argument('--ceph-cluster', required=False,
                        default=(
                            os.environ.get(
                                'NEB_RBD_MET_CEPH_CLUSTER', 'ceph')),
                        help='ceph cluster, default ceph')
    parser.add_argument('--ceph-user', required=False,
                        default=(
                            os.environ.get(
                                'NEB_RBD_MET_CEPH_CLUSTER', 'admin')),
                        help='ceph user, default admin')

    subparsers = parser.add_subparsers()

    daemon_parser = subparsers.add_parser(
        'daemon', help='run as daemon, sync every INTERVAL seconds')
    daemon_parser.set_defaults(func=daemon)
    daemon_parser.add_argument(
        '-i', '--interval', required=False, type=int, default=60,
        help="how often in seconds to poll ONE and update RBD metadata")

    runonce_parser = subparsers.add_parser(
        'runonce', help='run one sync and then exit')
    runonce_parser.set_defaults(func=runonce)

    shell_parser = subparsers.add_parser(
        'shell', help='enter debug shell')
    shell_parser.set_defaults(func=shell)

    args = parser.parse_args(args=args)

    logger.configure_nebula_rbd_metadata_logging(
        debug=args.debug, use_syslog=args.syslog)

    args_dict = vars(args)
    one_args = utils.get_kwargs_from_dict(args_dict, 'one_')
    ceph_args = utils.get_kwargs_from_dict(args_dict, 'ceph_')

    args.func(args, one_args, ceph_args)
