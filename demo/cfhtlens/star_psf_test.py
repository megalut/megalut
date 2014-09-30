"""
demo test of lensfit PSF reconstruction

"""

import megalut
import megalut.cfhtlens
import megalut.meas

import logging
logging.basicConfig(level=logging.INFO)

import numpy as np


pointing = megalut.cfhtlens.utils.Pointing(label="W1m0m0", filtername="i")

catpath = pointing.catpath()
cat = megalut.cfhtlens.utils.readcat(catpath)

megalut.cfhtlens.utils.removejunk(cat)
starcat = megalut.cfhtlens.utils.stars(cat)

megalut.utils.writepickle(starcat, "starcat.pkl")


imgfilepath = pointing.coaddimgpath()
img = megalut.gsutils.loadimg(imgfilepath)

starcat_coaddmes = megalut.meas.galsim_adamom.measure(img, starcat, stampsize=32, xname="Xpos", yname="Ypos", prefix="coaddmes")


megalut.utils.writepickle(starcat_coaddmes, "starcat_coaddmes.pkl")
#starcat_coaddmes = megalut.utils.readpickle("starcat_coaddmes.pkl")


megalut.cfhtlens.lensfitpsf.makeexppsfs(starcat_coaddmes, pointing, workdir = "test")
starcat_coaddmes = megalut.cfhtlens.lensfitpsf.stackexppsfs(starcat_coaddmes, workdir = "test")

img = megalut.gsutils.loadimg("test/psfgrid.fits")

starcat_bothmes = megalut.meas.galsim_adamom.measure(img, starcat_coaddmes, stampsize=32, xname="psfgridx", yname="psfgridy", prefix="psfmes")

megalut.utils.writepickle(starcat_bothmes, "starcat_bothmes.pkl")
starcat_bothmes.write("starcat_bothmes.fits")

"""
cat = megalut.utils.readpickle("starcat_bothmes.pkl")
cat.meta = {}
#cat.remove_column("")
cat.write("starcat_bothmes.fits")
"""


