
import os
import megalut
import numpy as np

import config

import logging
logger = logging.getLogger(__name__)


incatname = "vo-2"
#incatname = "tw-1"
#incatname = "tw-1-snc"
#incatname = "tw-1"


#variant = "snr"
variant = "snrsigma"

incatpath = os.path.join(config.simmeasdir, incatname, "groupmeascat.pkl")
cat = megalut.tools.io.readpickle(incatpath)
logger.info("Fraction of masked gals in input catalog:")
logger.info(float(np.sum(cat["adamom_sigma"].mask)) / np.size(cat["adamom_sigma"].mask))

#print megalut.tools.table.info(cat)

if variant is "snr":

	outcatname = incatname + "-snr-above-10"
	newmask = cat["snr"] < 10.0

elif variant is "snrsigma":

	outcatname = incatname + "-snr-above-10-sigma-above-1.5"
	newmask = np.logical_or(cat["snr"] < 10.0, cat["adamom_sigma"] < 1.5)

else:
	raise RuntimeError("Unknown")

logger.info("Fraction of selected gals:")
logger.info(float(np.sum(newmask)) / np.size(newmask) )


origmask = cat["adamom_sigma"].mask
combimask = np.logical_or(newmask, origmask)
cat["adamom_sigma"].mask = combimask


logger.info("Fraction of masked gals in output catalog:")
logger.info(float(np.sum(cat["adamom_sigma"].mask)) / np.size(cat["adamom_sigma"].mask))

outcatdir = os.path.join(config.simmeasdir, outcatname)
if not os.path.exists(outcatdir):
	os.mkdir(outcatdir)

megalut.tools.io.writepickle(cat, os.path.join(outcatdir, "groupmeascat.pkl"))
