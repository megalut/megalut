"""
This module provides a measurement function using SExtractor via sewpy that can be
passed to the meas.run wrappers.

You could also simply define such a function yourself, to control all parameters in 
a most flexible way.
"""

import logging
logger = logging.getLogger(__name__)

try:
	import sewpy
except ImportError:
	logger.warning("sewpy is not available, get it here: https://github.com/megalut/sewpy")
	raise

import os


def measfct(catalog, runon="img", **kwargs):
	"""
	MegaLUT-conform measfct wrapper, offering the possiblity to run either on "img" stamps, or on
	the "psf" stamps associated to the catalog. This might be useful for FDNT, depending on how
	a pipeline handles PSF measurements.
	
	:param runon: "img" or "psf" or ... -- decides on which image this should run.
		You might want to adjust the prefix, if running on something else than the default "img".
	
	Possible additional kwargs are params, config, sexpath, prefix... see function measure() below.
	"""
	
	# Here we do not have to load the image, as sewpy works on FITS files
	# However, we offer the choice to run on the "img" or the "psf" FITS file.
	
	if runon == "img":
		imgfilepath = catalog.meta["img"].filepath
	elif runon == "psf":
		if not "psf" in catalog.meta:
			raise RuntimeError("Cannot run on the psfs, as catalog.meta['psf'] is not defined.")
		imgfilepath = catalog.meta["psf"].filepath
	else:
		raise RuntimeError("Unknown value for runon")
	
	return measure(
		imgfilepath, catalog,
		xname=catalog.meta["img"].xname,
		yname=catalog.meta["img"].yname,
		workdir=catalog.meta["img"].workdir,
		**kwargs)


def measure(img, catalog, xname="x", yname="y",
	    params=None, config=None, workdir=None, sexpath="sex", prefix="sewpy_"):
	"""
	This is similar (in terms of API) to galsim_adamom.measure().
	Returns a copy of the given catalog, with new columns appended.
	
	:param img: path to a FITS image
	:param catalog: astropy table of objects to be measured
	:param xname: column name containing the x coordinates in pixels
	:param yname: idem for y
	:param params: sewpy params. If ``None``, a default set, with many WIN parameters, is used.
	:param config: sewpy config. If ``None``, a reasonable (?) default is used.
	:param workdir: path where all SExtractor files, settings, and **logs** are kept.
	
	When this function is passed to megalut.meas.run(), the suggested workdir location is, e.g.,::
	
		os.path.join(measdir, "sewpy")
	
	This way all relevant files will be kept together in the measdir, close to the catalogs.
	
	"""
	
	# We make the workdir.
	# Indeed, if we leave this to sewpy, there is a race hazard.
	# We cannot use the normal "if exists: os.makedirs()" !
	
	if workdir != None:
		try:
			os.makedirs(workdir)
			logger.debug("Made workdir %s" % (workdir))
		except OSError:
			pass

	if params == None:
		params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
			"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
			"FWHM_IMAGE", "BACKGROUND", "FLAGS"]
	
	if config == None:
		config = {"DETECT_MINAREA":5, "ASSOC_RADIUS":5, "ASSOC_TYPE":"NEAREST"}
		
	sew = sewpy.SEW(sexpath=sexpath, params=params, config=config, workdir=workdir, nice=19)
	out = sew(img, assoc_cat=catalog, assoc_xname=xname, assoc_yname=yname, prefix=prefix)
		
	return out["table"]
	
	
