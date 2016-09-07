import subprocess
import shlex

GET_METADATA_COMMAND = 'rbd image-meta get {imagespec} {key}'
SET_METADATA_COMMAND = 'rbd image-meta set {imagespec} {key} {value}'

def get_metadata(imagespec, key):
    """
    Get RBD metadata for a device
    """
    command = shlex.split(GET_METADATA_COMMAND.format(
        imagespec=imagespec, key=key))
    p = subprocess.Popen(command, stdout=subprocess.PIPE,
        stderr = subprocess.PIPE)
    stdout, stderr = p.communicate()
    value = stdout.strip('\n')
    if p.returncode != 0:
        # this is OK if a vm doesn't have any metadata yet
        pass
    return value


def set_metadata(imagespec, key, value):
    """
    Set RBD metadata for a device
    """
    command = shlex.split(SET_METADATA_COMMAND.format(
        imagespec=imagespec, key=key, value=value))
    p = subprocess.Popen(command, stdout=subprocess.PIPE,
        stderr = subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise CantSetMetadatError
    return True
