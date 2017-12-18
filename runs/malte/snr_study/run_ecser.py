import matplotlib
matplotlib.use("AGG")

import os
import simparamsecser
import megalut
import megalut.meas
import numpy as np

import logging

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s',level=logging.INFO)



#### Parameters ###################

genworkdir = "/vol/fohlen11/fohlen11_1/mtewes/snr_study/"
sexpath="/vol/software/software/astro/sextractor/sextractor-2.19.5/64bit/bin/sex"




name =  "ecser_v1"
n = 20
nrea = 10
gain = 3.1
stampsize = 64

####################################



sp = simparamsecser.Simple1()


workdir = os.path.join(genworkdir, name)
if not os.path.isdir(workdir):
	os.makedirs(workdir)
fitsimgpath = os.path.join(workdir, "img.fits")
catpath = os.path.join(workdir, "cat.pkl")
writecatpath = os.path.join(workdir, "writecat.txt")


cat = megalut.sim.stampgrid.drawcat(sp, n=n*nrea, nc=nrea, stampsize=stampsize)

megalut.sim.stampgrid.drawimg(cat, simgalimgfilepath=fitsimgpath, simtrugalimgfilepath=None, simpsfimgfilepath=None)


#print cat["y", "tru_cropper_snr"]


cat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
	fitsimgpath,
	xname="x",
	yname="y",
	stampsize=stampsize,
	pixelscale=1.0
	)

cat = megalut.meas.galsim_adamom.measfct(cat, stampsize=stampsize, variant="wider")
cat = megalut.meas.skystats.measfct(cat, stampsize=stampsize)
cat = megalut.meas.snr.measfct(cat, gain=gain)


# Now we run sextractor
params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
	"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
	"FWHM_IMAGE", "BACKGROUND", "FLAGS",
	"FLUX_ISO", "FLUXERR_ISO"]
	
config = {"DETECT_MINAREA":5, "ASSOC_RADIUS":5, "GAIN":gain, "ASSOC_TYPE":"NEAREST"}
		
cat = megalut.meas.sewfunc.measfct(cat, params=params, config=config, sexpath=sexpath)

cat["sex_snr_iso"] = cat["sewpy_FLUX_ISO"] / cat["sewpy_FLUXERR_ISO"]
cat["sex_snr_auto"] = cat["sewpy_FLUX_AUTO"] / cat["sewpy_FLUXERR_AUTO"]

cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_mag", "zeropoint", "tru_flux", "tru_rad"])
megalut.tools.table.addstats(cat, "snr")
megalut.tools.table.addstats(cat, "sex_snr_iso")
megalut.tools.table.addstats(cat, "sex_snr_auto")
megalut.tools.table.addstats(cat, "adamom_flux")
megalut.tools.table.addstats(cat, "adamom_sigma")
megalut.tools.table.addstats(cat, "skystd")
megalut.tools.table.addstats(cat, "skymad")

megalut.tools.io.writepickle(cat, catpath)

print megalut.tools.table.info(cat)

print cat["tru_mag", "zeropoint", "snr_mean", "sex_snr_auto_mean", "tru_flux", "adamom_flux_mean", "tru_rad", "adamom_sigma_mean", "skystd_mean", "skymad_mean"]

#writecat = cat["tru_flux", "tru_cropper_snr", "gain1_snr_mean", "gain1e9_snr_mean", "gain1_aper3hlr_snr_mean", "sex_snr_iso_mean", "sex_snr_auto_mean"]
#print writecat
#writecat.write(writecatpath, format="ascii")


