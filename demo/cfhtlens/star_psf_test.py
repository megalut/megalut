import megalut
import megalut.cfhtlens
import megalut.meas

import logging
logging.basicConfig(level=logging.INFO)

import numpy as np



catfile = "/vol/fohlen11/fohlen11_1/hendrik/data/CFHTLenS/release_cats/W1m0m0_izrgu_release_mask.cat"
cat = megalut.cfhtlens.utils.readcat(catfile)

megalut.cfhtlens.utils.removejunk(cat)
starcat = megalut.cfhtlens.utils.stars(cat)

megalut.utils.writepickle(starcat, "starcat.pkl")


imgfilepath = "/vol/braid1/vol1/thomas/SHEARCOLLAB/Bonn/W1m0m0/i/coadd_V2.2A/W1m0m0_i.V2.2A.swarp.cut.fits"

img = megalut.meas.galsim_adamom.loadimg(imgfilepath)
starcat_coaddmes = megalut.meas.galsim_adamom.measure(img, starcat, stampsize=32, xname="Xpos", yname="Ypos", prefix="coaddmes")


megalut.utils.writepickle(starcat_coaddmes, "starcat_coaddmes.pkl")





starcat_coaddmes = megalut.utils.readpickle("starcat_coaddmes.pkl")

pointing = megalut.cfhtlens.utils.Pointing(label="W1m0m0", filtername="i")

megalut.cfhtlens.lensfitpsf.makeexppsfs(starcat_coaddmes, pointing, workdir = "test")
starcat_coaddmes = megalut.cfhtlens.lensfitpsf.stackexppsfs(starcat_coaddmes, workdir = "test")

img = megalut.meas.galsim_adamom.loadimg("test/psfgrid.fits")

starcat_bothmes = megalut.meas.galsim_adamom.measure(img, starcat_coaddmes, stampsize=32, xname="psfgridx", yname="psfgridy", prefix="psfmes")

megalut.utils.writepickle(starcat_bothmes, "starcat_bothmes.pkl")




cat = megalut.utils.readpickle("starcat_bothmes.pkl")
cat.meta = {}
#cat.remove_column("")
cat.write("starcat_bothmes.fits")



