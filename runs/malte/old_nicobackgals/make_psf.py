import galsim
import numpy as np
import megalut
import galsim
import config
import os
import astropy
import numpy as np


import logging
logger = logging.getLogger(__name__)

supersampling = 4 # Relative to the Euclid detector

psfstampsize = 64 * supersampling

logger.info("Drawing PSF stamp...")

lam = 800
diam = 1.2
lam_over_diam = lam*1.0e-9/diam
lam_over_diam_arcsec = lam_over_diam * (180.0/np.pi) * 3600.0 
psf = galsim.Airy(lam_over_diam=lam_over_diam_arcsec, obscuration=0.3)
pixel_scale = 0.1 / supersampling
image = galsim.ImageF(psfstampsize, psfstampsize)
image = psf.drawImage(image=image, scale=pixel_scale)
image.write(config.psfimgpath)


logger.info("Making PSF catalog...")


cat = astropy.table.Table([[0.5 + psfstampsize/2.0], [0.5 + psfstampsize/2.0]], names=('psfx', 'psfy'))
cat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
	filepath=config.psfimgpath,
	xname="psfx",
	yname="psfy",
	stampsize=psfstampsize,
	workdir=None,
	pixelscale=1.0/supersampling
	)
megalut.tools.io.writepickle(cat, config.psfcatpath)

logger.info(cat.meta)

logger.info("Done.")
