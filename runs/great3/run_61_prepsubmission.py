"""
This generates the "submission file" (for constant shear branches), bypassing the GREAT3 "presubmission script".
"""


import megalut
import megalut.tools

import astropy

import config
import numpy as np
import os


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

catpath = config.great3.path("summary_{}.pkl".format(config.predcode))
cat = megalut.tools.io.readpickle(catpath)

subcat = cat["subfield","pre_s1w","pre_s2w"]

outcatpath = config.great3.path("submission_{}.txt".format(config.predcode))
logger.info("Writing {}...".format(outcatpath))
subcat.write(outcatpath, format="ascii.commented_header")

