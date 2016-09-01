import os

import logging
logger = logging.getLogger(__name__)


def mkdir(somedir):
	"""
	A wrapper around os.makedirs, with some logging.
	:param somedir: a name or path to a directory which I should make.
	"""
	
	raise RuntimeError("I suggest to stop using this, it doesn't even log so I don't see the point.")
	
	if not os.path.isdir(somedir):
		os.makedirs(somedir)
