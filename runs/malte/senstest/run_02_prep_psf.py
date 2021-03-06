import megalut
import config
import measfcts
import glob
import os
import numpy as np
import astropy

import logging
logger = logging.getLogger(__name__)


psffilename = "sensitivity_testing_psf_{}.fits".format(config.pcode[1:3])
psfpath = os.path.join(config.psfdir, psffilename)

psfcatpath = os.path.join(config.psfdir, "psfcat_{}.pkl".format(config.pcode))

psfstampsize = 256
supersampling = 5.0

# We make a 1-row catalog for this PSF

cat = astropy.table.Table([[0.5 + psfstampsize/2.0], [0.5 + psfstampsize/2.0]], names=('psfx', 'psfy'))
cat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
	filepath=psfpath,
	xname="psfx",
	yname="psfy",
	stampsize=psfstampsize,
	workdir=None,
	pixelscale=1.0/supersampling
	)
megalut.tools.io.writepickle(cat, psfcatpath)

logger.info(cat.meta)

logger.info("Done.")


