"""
Measuring sample data
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



imgnames = ["sensitivity_testing_1_0.fits"]
catnames = ["sensitivity_testing_1_0_details.fits"]

incatfilepaths = []
outcatfilepaths = []

for (imgname, catname) in zip(imgnames, catnames):
	
	
	
	imgpath = os.path.join(config.obsdir, imgname)
	catpath = os.path.join(config.obsdir, catname)
	imgwdname = os.path.splitext(imgname)[0]
	workdir=os.path.join(config.obsproddir, imgwdname)
	if not os.path.isdir(workdir):
		os.makedirs(workdir)
	
	logger.info("Working on {}...".format(imgwdname))

	#cathdulist = astropy.io.fits.open(catpath)
	#cat = cathdulist[1].data
	
	cat = astropy.table.Table.read(catpath)
	cat["ccdgain"] = float(cat.meta["CCDGAIN"])
	print megalut.tools.table.info(cat)
	
	
	#print cat
	cat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
		filepath=imgpath,
		xname="x_center_pix",
		yname="y_center_pix",
		stampsize=config.stampsize,
		workdir=workdir
		)
	
	incatfilepath = os.path.join(workdir, "incat_"+imgwdname+".pkl")
	outcatfilepath = os.path.join(workdir, "meascat_"+imgwdname+".pkl")

	incatfilepaths.append(incatfilepath)
	outcatfilepaths.append(outcatfilepath)

	megalut.tools.io.writepickle(cat, incatfilepath)


megalut.meas.run.general(incatfilepaths, outcatfilepaths, measfcts.default, measfctkwargs={"stampsize":config.stampsize}, ncpu=1, skipdone=False)

