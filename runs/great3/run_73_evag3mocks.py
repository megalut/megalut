#import matplotlib
#matplotlib.use("AGG")

import megalut
import megalut.tools
import megalut.plot
from megalut.tools.feature import Feature

import megalutgreat3
import astropy


import config
import numpy as np
import os
import matplotlib.pyplot as plt


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


catpath = config.great3.path("{}_summary_{}.pkl".format(config.datasets["mimic-great3"], config.predcode))
cat = megalut.tools.io.readpickle(catpath)


mets = megalutgreat3.utils.metrics(cat, ("tru_s1", "tru_s2"), ("pre_s1w", "pre_s2w"), psfgcols=("tru_psf_g1", "tru_psf_g2"))

