import numpy as np
import megalut
import galsim
import astropy.table
import os

import includes


import logging
logger = logging.getLogger(__name__)


if not os.path.exists(includes.workdir):
	os.mkdir(includes.workdir)

supersampling = 4 # Relative to the Euclid pixel size

psfstampsize = includes.stampsize * supersampling

logger.info("Drawing PSF stamp...")

psf = galsim.Gaussian(fwhm=0.18)
pixel_scale = 0.1 / supersampling
image = galsim.ImageF(psfstampsize, psfstampsize)
image = psf.drawImage(image=image, scale=pixel_scale)
image.write(includes.psfimgpath)


logger.info("Making PSF catalog...")


cat = astropy.table.Table([[0.5 + psfstampsize/2.0], [0.5 + psfstampsize/2.0]], names=('psfx', 'psfy'))
cat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
	filepath=includes.psfimgpath,
	xname="psfx",
	yname="psfy",
	stampsize=psfstampsize,
	workdir=None,
	pixelscale=1.0/supersampling
	)
megalut.tools.io.writepickle(cat, includes.psfcatpath)

logger.info(cat.meta)

logger.info("Done.")
