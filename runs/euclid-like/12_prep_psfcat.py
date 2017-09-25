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
import includes

import os

import logging
logger = logging.getLogger(__name__)

addprefix = "psf"

starpos = np.array([[0.5+includes.stampsize/2.0, 0.5+includes.stampsize/2.0]])
starcat = astropy.table.Table([starpos[:,0], starpos[:,1]], names=('{}x'.format(addprefix), '{}y'.format(addprefix)))
 
# To measure the stars, we attach the image:
starcat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
    filepath=os.path.join(includes.psfdir, "psf.fits"),
    xname="{}x".format(addprefix),
    yname="{}y".format(addprefix),
    stampsize=includes.stampsize,
    workdir=os.path.join(includes.psfdir, "psf_measworkdir"),
    pixelscale=includes.pixelscale
    )

starcat = measfcts.default(starcat, stampsize=includes.stampsize, gain=includes.gain)

for colname in starcat.colnames:
    if colname == "{}x".format(addprefix) or colname == "{}y".format(addprefix):
        continue
    starcat.rename_column(colname, "{}{}".format(addprefix, colname))

megalut.tools.io.writepickle(starcat, os.path.join(includes.psfdir, "psf_meascat.pkl"))
    
print starcat 
