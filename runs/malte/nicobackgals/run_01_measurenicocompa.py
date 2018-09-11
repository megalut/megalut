import megalut
import config
import measfcts
import glob
import os
import numpy as np
import astropy

import logging
logger = logging.getLogger(__name__)



compadir = os.path.join(config.workdir, "compa_with_nico")
nside = 100
stampsize = 64

imgpaths = glob.glob(os.path.join(compadir, "sim_*.fits"))


logger.info("Found {} files".format(len(imgpaths)))


incatfilepaths = []
outcatfilepaths = []

for imgpath in imgpaths:
	
	imgname = os.path.splitext(os.path.split(imgpath)[-1])[0]
	
	logger.info("Making catalog for image '{}'...".format(imgname))
	
	gals = []
	for i in range(nside):
		for j in range(nside):
			gals.append( [0.5 + stampsize/2.0 + i*stampsize, 0.5 + stampsize/2.0 + j*stampsize] )
	gals = np.array(gals)
	cat = astropy.table.Table([gals[:,0], gals[:,1]], names=('x', 'y'))
	
	cat.meta["name"]= imgname
	
	cat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
		filepath=imgpath,
		xname="x",
		yname="y",
		stampsize=config.stampsize,
		workdir=os.path.join(compadir, imgname)
		)

	incatfilepath = os.path.join(compadir, "incat_"+imgname+".pkl")
	outcatfilepath = os.path.join(compadir, "meascat_"+imgname+".pkl")

	incatfilepaths.append(incatfilepath)
	outcatfilepaths.append(outcatfilepath)

	megalut.tools.io.writepickle(cat, incatfilepath)
	


# And we run with ncpu
megalut.meas.run.general(incatfilepaths, outcatfilepaths, measfcts.default, measfctkwargs={"stampsize":config.stampsize}, ncpu=1, skipdone=False)

