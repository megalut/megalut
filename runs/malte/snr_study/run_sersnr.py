import matplotlib
matplotlib.use("AGG")

import os
import simparamssersnr
import megalut
import megalut.meas
import numpy as np

import logging

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s',level=logging.INFO)



#### Parameters ###################

genworkdir = "/vol/fohlen11/fohlen11_1/mtewes/snr_study/"
sexpath="/vol/software/software/astro/sextractor/sextractor-2.19.5/64bit/bin/sex"




name =  "sersnr_v1"
n = 20
nrea = 100
gain = 3.1
stampsize = 64
####################################



sp = simparamssersnr.Simple1()


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

#cat = megalut.meas.snr.measfct(cat, gain=1.0e9, prefix="gain1e9_", aper=2.0)
#cat = megalut.meas.snr.measfct(cat, gain=1.0, prefix="gain1_aper3hlr_", aper=3.0)

# Now we run sextractor
params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
	"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
	"FWHM_IMAGE", "BACKGROUND", "FLAGS",
	"FLUX_ISO", "FLUXERR_ISO"]
	
config = {"DETECT_MINAREA":5, "ASSOC_RADIUS":5, "GAIN":gain, "ASSOC_TYPE":"NEAREST"}
		
cat = megalut.meas.sewfunc.measfct(cat, params=params, config=config, sexpath=sexpath)

cat["sex_snr_iso"] = cat["sewpy_FLUX_ISO"] / cat["sewpy_FLUXERR_ISO"]
cat["sex_snr_auto"] = cat["sewpy_FLUX_AUTO"] / cat["sewpy_FLUXERR_AUTO"]


cat = megalut.tools.table.fastgroupreshape(cat, groupcolnames=["tru_mag", "zeropoint", "tru_sersicn", "tru_flux"])
megalut.tools.table.addstats(cat, "snr")
megalut.tools.table.addstats(cat, "sex_snr_iso")
megalut.tools.table.addstats(cat, "sex_snr_auto")
megalut.tools.table.addstats(cat, "adamom_flux")
megalut.tools.table.addstats(cat, "adamom_sigma")
megalut.tools.table.addstats(cat, "skystd")
megalut.tools.table.addstats(cat, "skymad")
megalut.tools.table.addstats(cat, "sewpy_FLUX_AUTO")
megalut.tools.table.addstats(cat, "skystampsum")



megalut.tools.io.writepickle(cat, catpath)

print megalut.tools.table.info(cat)
writecat = cat["zeropoint", "tru_mag", "tru_sersicn", "snr_mean", "sex_snr_auto_mean", "adamom_sigma_mean", "adamom_flux_mean", "tru_flux", "sewpy_FLUX_AUTO_mean", "skystampsum_mean"]
print writecat

#writecat.write(writecatpath, format="ascii")


