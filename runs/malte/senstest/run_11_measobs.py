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


datasets = []
for i in range(1, 11):
	for j in range(0, 10):
		imgname = "sensitivity_testing_{}_{}".format(i, j)
		catname = "sensitivity_testing_{}_{}_details".format(i, j)
		datasets.append({"i":i, "j":j, "imgname":imgname, "catname":catname})


incatfilepaths = []
outcatfilepaths = []

for dataset in datasets:
	
	
	
	imgpath = os.path.join(config.obsdir, dataset["imgname"] + ".fits")
	catpath = os.path.join(config.obsdir, dataset["catname"] + ".fits")
	imgwdname = dataset["imgname"]
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


megalut.meas.run.general(incatfilepaths, outcatfilepaths, measfcts.default, measfctkwargs={"stampsize":config.stampsize}, ncpu=20, skipdone=False)

