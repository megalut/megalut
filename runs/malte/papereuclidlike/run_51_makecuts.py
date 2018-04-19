
import os
import megalut
import numpy as np

import config

import logging
logger = logging.getLogger(__name__)


incatname = "vo-1"
outcatname = "vo-1-snr-above-10"


incatpath = os.path.join(config.simmeasdir, incatname, "groupmeascat.pkl")
cat = megalut.tools.io.readpickle(incatpath)

#print megalut.tools.table.info(cat)


logger.info("Fraction of masked gals in input catalog:")
logger.info(float(np.sum(cat["adamom_sigma"].mask)) / np.size(cat["adamom_sigma"].mask))

snrmask = cat["snr"] < 10.0

logger.info("Fraction of gals with SNR < 10:")
logger.info(float(np.sum(snrmask)) / np.size(snrmask) )


origmask = cat["adamom_sigma"].mask
combimask = np.logical_or(snrmask, origmask)
cat["adamom_sigma"].mask = combimask


logger.info("Fraction of masked gals in output catalog:")
logger.info(float(np.sum(cat["adamom_sigma"].mask)) / np.size(cat["adamom_sigma"].mask))




outcatdir = os.path.join(config.simmeasdir, outcatname)
if not os.path.exists(outcatdir):
	os.mkdir(outcatdir)

megalut.tools.io.writepickle(cat, os.path.join(outcatdir, "groupmeascat.pkl"))
