import os
import tempfile


def cwd():
    return os.path.dirname(os.path.realpath(__file__))


def get_log(name: str):
    """
    Parameters
    ----------
    name: log name (http, wsgi etc)
    Returns
    -------
    string: valid full path for log file
    """
    return os.path.normpath(f'{cwd()}/logs/{name}.log')


def get_tmp():
    """
    Parameters
    ----------
    Returns
    -------
    string: valid full path for temp
    """
    # todo: os.path should be cross-platform, but need to validate
    # if platform.system() == 'Windows':
    #     tmp_dir = '.\\tmp\\'
    return tempfile.gettempdir()