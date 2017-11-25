"""
Measures features of the PSFs, 
individually for each subfield.
"""
import multiprocessing
import datetime
import numpy as np
import astropy.table

import megalut

import measfcts
import config

import os
import measfcts

import logging
logger = logging.getLogger(__name__)

addprefix = "psf"

starpos = np.array([[0.5+config.stampsize/2.0, 0.5+config.stampsize/2.0]])
starcat = astropy.table.Table([starpos[:,0], starpos[:,1]], names=('{}x'.format(addprefix), '{}y'.format(addprefix)))
 
# To measure the stars, we attach the image:
starcat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
    filepath=os.path.join(config.psfdir, "psf.fits"),
    xname="{}x".format(addprefix),
    yname="{}y".format(addprefix),
    stampsize=config.stampsize,
    workdir=os.path.join(config.psfdir, "psf_measworkdir"),
    pixelscale=config.pixelscale
    )

starcat = measfcts.default(starcat, stampsize=config.stampsize, gain=config.gain)

for colname in starcat.colnames:
    if colname == "{}x".format(addprefix) or colname == "{}y".format(addprefix):
        continue
    starcat.rename_column(colname, "{}{}".format(addprefix, colname))

megalut.tools.io.writepickle(starcat, os.path.join(config.psfdir, "psf_meascat.pkl"))
    
for col in starcat.colnames:
    print starcat[col] 
    
print 
print 
print starcat["psfadamom_sigma"] * 2.35
