import os

__version__ = '0.2.2'
__port__ = 0


def get_base_path():
    """
    get package base dir
    """
    return os.path.dirname(__file__)