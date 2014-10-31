import os

import logging
logger = logging.getLogger(__name__)


def mkdir(somedir):
    """
    A wrapper around os.makedirs, with some logging.
    :param somedir: a name or path to a directory which I should make.
    """
    if not os.path.isdir(somedir):
        os.makedirs(somedir)
