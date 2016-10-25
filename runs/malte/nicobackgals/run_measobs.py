"""
MegaLUT-style running on Nicolas' simulations.

"""


import megalut
import config
import measfcts
import glob
import os
import numpy as np
import astropy

import logging
logger = logging.getLogger(__name__)


imgpaths = glob.glob(os.path.join(config.obsdir, "*.fits"))

#imgpaths = glob.glob(os.path.join(config.obsdir, "i**.fits"))


logger.info("Found {} files".format(len(imgpaths)))


if not os.path.exists(config.obsworkdir):
	os.mkdir(config.obsworkdir)

incatfilepaths = []
outcatfilepaths = []

for imgpath in imgpaths:
	
	imgname = os.path.splitext(os.path.split(imgpath)[-1])[0]
	
	logger.info("Making catalog for image '{}'...".format(imgname))
	
	gals = []
	for i in range(config.nside):
		for j in range(config.nside):
			gals.append( [0.5 + config.stampsize/2.0 + i*config.stampsize, 0.5 + config.stampsize/2.0 + j*config.stampsize] )
	gals = np.array(gals)
	cat = astropy.table.Table([gals[:,0], gals[:,1]], names=('x', 'y'))
	
	cat.meta["name"]= imgname
	
	cat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
		filepath=imgpath,
		xname="x",
		yname="y",
		stampsize=config.stampsize,
		workdir=os.path.join(config.obsworkdir, imgname)
		)

	incatfilepath = os.path.join(config.obsworkdir, "incat_"+imgname+".pkl")
	outcatfilepath = os.path.join(config.obsworkdir, "meascat_"+imgname+".pkl")

	incatfilepaths.append(incatfilepath)
	outcatfilepaths.append(outcatfilepath)

	megalut.tools.io.writepickle(cat, incatfilepath)
	


# And we run with ncpu
megalut.meas.run.general(incatfilepaths, outcatfilepaths, measfcts.default, measfctkwargs={"stampsize":config.stampsize}, ncpu=config.ncpu, skipdone=False)


