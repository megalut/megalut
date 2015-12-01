"""
Analysis of the auto SBE results
"""

import numpy as np

import megalut.tools
from megalut.tools.feature import Feature

import logging
logger = logging.getLogger(__name__)


def quicktest(cat,
		colname_pre_s1="pre_s1",
		colname_pre_s2="pre_s2",
		colname_tru_s1="Galaxy_e1",
		colname_tru_s2="Galaxy_e2"
	):
	"""
	This is really just to log if something is completely wrong.
	"""
	
	txt = str(cat[0:15])
	logger.info("Logging a few lines from the catalog: \n" + txt)
	
	e1m = megalut.tools.metrics.metrics(cat, labelfeature=Feature(colname_tru_s1), predlabelfeature=Feature(colname_pre_s1))
	e2m = megalut.tools.metrics.metrics(cat, labelfeature=Feature(colname_tru_s2), predlabelfeature=Feature(colname_pre_s2))
	txte1m = "e1: m/100 = %.4f +/- %.4f, c/100 = %.4f +/- %.4f, predfrac = %.2f %%" % (e1m["m"]*100.0, e1m["merr"]*100.0, e1m["c"]*100.0, e1m["cerr"]*100.0, e1m["predfrac"]*100.0)
	txte2m = "e2: m/100 = %.4f +/- %.4f, c/100 = %.4f +/- %.4f, predfrac = %.2f %%" % (e2m["m"]*100.0, e2m["merr"]*100.0, e2m["c"]*100.0, e2m["cerr"]*100.0, e2m["predfrac"]*100.0)
	
	logger.info("Comparing shear estimates with true galaxy **ellipticities** (not shear): \n" + txte1m + "\n" + txte2m)
	
	#import matplotlib.pyplot as plt
	#plt.plot(cat[colname_tru_s1], cat[colname_pre_s1], "b.")
	#plt.show()
