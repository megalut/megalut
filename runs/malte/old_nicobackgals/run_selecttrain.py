import matplotlib
matplotlib.use("AGG")


import megalut
import config
import measfcts
import simparams
import mlparams

import glob
import os
import numpy as np
import astropy

import logging
logger = logging.getLogger(__name__)


spname = "Nico4"

cat = megalut.tools.io.readpickle(os.path.join(config.simdir, spname, "groupmeascat.pkl"))
print megalut.tools.table.info(cat)

megalut.tools.table.addstats(cat, "snr")
#cat["adamom_frac"] = np.sum(cat["adamom_g1"].mask, axis=1)/float(cat["adamom_g1"].shape[1])
#print cat["adamom_frac"]

print min(cat["snr_mean"]), max(cat["snr_mean"]), np.median(cat["snr_mean"])

# Keep only good SNR ones

s = megalut.tools.table.Selector("train", [("in", "snr_mean", 20, 100)])
cat = s.select(cat)

print min(cat["snr_mean"]), max(cat["snr_mean"]), np.median(cat["snr_mean"])
#print cat["adamom_frac"]

megalut.tools.io.writepickle(cat, os.path.join(config.simdir, spname, "groupmeascat_select.pkl"))

