"""
This calls the GREAT3 evaluation function
"""


import megalut
import megalut.tools

import astropy

import config
import numpy as np
import os
import sys


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


outcatpath = config.great3.path("submission_{}.txt".format(config.predcode))

metricsdirpath = os.path.join(config.great3.g3publicdir, "metrics")
sys.path.append(metricsdirpath)
import evaluate

results = evaluate.q_constant(
	outcatpath, config.great3.experiment, config.great3.obstype,
	storage_dir=config.great3.path("eva_storage_dir_{}".format(config.predcode)),
	truth_dir=config.great3.truthdir,
	plot=config.great3.path("eva_plot_{}".format(config.predcode)),
	logger=logger,
	pretty_print=True)

