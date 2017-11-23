
import os
import simparamsgauss
import megalut
import megalut.meas
import numpy as np

import logging

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s',level=logging.INFO)



#### Parameters ###################

genworkdir = "/vol/fohlen11/fohlen11_1/mtewes/snr_fig/"
sexpath="/vol/software/software/astro/sextractor/sextractor-2.19.5/64bit/bin/sex"
stampsize = 48

name = "v1"

n = 12
nc = 3
nrea = 100
ncpu = 10
stampsize = 30
gain = 1.0e12

sexpath="/vol/software/software/astro/sextractor/sextractor-2.19.5/64bit/bin/sex"

####################################



sp = simparamsgauss.Simple1()


workdir = os.path.join(genworkdir, name)
if not os.path.isdir(workdir):
	os.makedirs(workdir)
fitsimgpath = os.path.join(workdir, "img.fits")
catpath = os.path.join(workdir, "cat.pkl")
writecatpath = os.path.join(workdir, "writecat.txt")


cat = megalut.sim.stampgrid.drawcat(sp, n=n, nc=nc, stampsize=stampsize)

megalut.sim.stampgrid.drawimg(cat, simgalimgfilepath=fitsimgpath, simtrugalimgfilepath=None, simpsfimgfilepath=None)


def measfct(catalog, stampsize):
	"""
	Default measfct, runs on "img".
	"""	
	# HSM adamom
	catalog = megalut.meas.galsim_adamom.measfct(catalog, stampsize=stampsize, variant="wider")
	catalog = megalut.meas.adamom_calc.measfct(catalog)
	# And skystats
	catalog = megalut.meas.skystats.measfct(catalog, stampsize=stampsize)
	# And snr
	catalog = megalut.meas.snr.measfct(catalog, gain=gain) # Gain set to give sky-limited SNR
	
	# And SExtractor
	params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
	"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
	"FWHM_IMAGE", "BACKGROUND", "FLAGS",
	"FLUX_ISO", "FLUXERR_ISO"]
	
	config = {"DETECT_MINAREA":5, "ASSOC_RADIUS":5, "GAIN":gain, "ASSOC_TYPE":"NEAREST"}
		
	# FOR SOME STRANGE REASON, I CAN'T GET SEXTRACTOR TO WORK HERE
	#catalog = megalut.meas.sewfunc.measfct(catalog, params=params, config=config, sexpath=sexpath)

	#catalog["sex_snr_iso"] = catalog["sewpy_FLUX_ISO"] / catalog["sewpy_FLUXERR_ISO"]
	#catalog["sex_snr_auto"] = catalog["sewpy_FLUX_AUTO"] / catalog["sewpy_FLUXERR_AUTO"]

	return catalog
	

groupcols = [
'adamom_flag',
'adamom_flux',
'adamom_x',
'adamom_y',
'adamom_g1',
'adamom_g2',
'adamom_sigma',
'adamom_rho4',
'adamom_logflux',
'adamom_g',
'adamom_theta',
'skystd',
'skymad',
'skymean',
'skymed',
'skystampsum',
'skyflag',
'snr'
#'sewpy_XWIN_IMAGE',
#'sewpy_YWIN_IMAGE',
#'sewpy_AWIN_IMAGE',
#'sewpy_BWIN_IMAGE',
#'sewpy_THETAWIN_IMAGE',
#'sewpy_FLUX_WIN',
#'sewpy_FLUXERR_WIN',
#'sewpy_NITER_WIN',
#'sewpy_FLAGS_WIN',
#'sewpy_FLUX_AUTO',
#'sewpy_FLUXERR_AUTO',
#'sewpy_FWHM_IMAGE',
#'sewpy_KRON_RADIUS',
#'sewpy_FLUX_RADIUS',
#'sewpy_FLUX_RADIUS_1',
#'sewpy_FLUX_RADIUS_2',
#'sewpy_FLUX_RADIUS_3',
#'sewpy_FLUX_RADIUS_4',
#'sewpy_FLUX_RADIUS_5',
#'sewpy_FLUX_RADIUS_6',
#'sewpy_FLUX_APER',
#'sewpy_FLUX_APER_1',
#'sewpy_FLUXERR_APER',
#'sewpy_FLUXERR_APER_1',
#'sewpy_BACKGROUND',
#'sewpy_FLAGS',
#'sewpy_assoc_flag',
#'sewpy_snr',
]
removecols = []

megalut.sim.run.multi(
	simdir=workdir,
	simparams=sp,
	drawcatkwargs={"n":n, "nc":nc, "stampsize":stampsize},
	drawimgkwargs={}, 
	psfcat=None, psfselect="random",
	ncat=1, nrea=nrea, ncpu=ncpu,
	savepsfimg=False, savetrugalimg=False
)


# Measuring the newly drawn images
megalut.meas.run.onsims(
	simdir=workdir,
	simparams=sp,
	measdir=workdir,
	measfct=measfct,
	measfctkwargs={"stampsize":stampsize},
	ncpu=ncpu,
	skipdone=False
)
	

cat = megalut.meas.avg.onsims(
	measdir=workdir, 
	simparams=sp,
	task="group",
	groupcols=groupcols, 
	removecols=removecols
)



"""
cat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
	fitsimgpath,
	xname="x",
	yname="y",
	stampsize=stampsize,
	pixelscale=1.0
	)

cat = megalut.meas.galsim_adamom.measfct(cat, stampsize=stampsize, variant="wider")
cat = megalut.meas.skystats.measfct(cat, stampsize=stampsize)
#cat = megalut.meas.snr.measfct(cat, gain=1.0)
cat = megalut.meas.snr.measfct(cat, gain=gain)
"""


cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_flux", "tru_sigma", "x", "y"])
megalut.tools.table.addstats(cat, "snr")
#megalut.tools.table.addstats(cat, "sex_snr_iso")
#megalut.tools.table.addstats(cat, "sex_snr_auto")
megalut.tools.table.addstats(cat, "adamom_sigma")
megalut.tools.table.addstats(cat, "adamom_flux")

megalut.tools.io.writepickle(cat, catpath)

cat.sort(["y", "x"])

print megalut.tools.table.info(cat)
#writecat = cat["tru_x", "tru_y", "tru_flux", "tru_sigma", "snr_mean", "sex_snr_iso_mean", "sex_snr_auto_mean", "adamom_sigma_mean", "adamom_flux_mean"]
writecat = cat["x", "y", "snr_n", "tru_flux", "adamom_flux_mean", "tru_sigma", "adamom_sigma_mean", "snr_mean"]

print writecat
writecat.write(writecatpath, format="ascii")


