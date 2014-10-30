import os

import logging
logger = logging.getLogger(__name__)


def mkdir(somedir):
    """
    A wrapper around os.makedirs, with some logging.
    :param somedir: a name or path to a directory which I should make.
    """
    if os.path.isdir(somedir):
        logger.warning("Directory '%s' exists, be careful! I might (maybe silently) delete or overwrite stuff." % (somedir))    
    else:
        logger.info("Making new directory '%s'" % (somedir))
        os.makedirs(somedir)