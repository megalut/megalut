"""
This module provides a measurement function using SExtractor via sewpy that can be
passed to the meas.run wrappers.

You could also simply define such a function yourself, to control all parameters in 
a most flexible way.
"""


import sewpy
import os


def measure(img, catalog, xname="x", yname="y", params=None, config=None, workdir=None,
	sexpath="sex", prefix="sewpy_"):
	"""
	This is similar (in terms of API) to galsim_adamom.measure().
	Returns a copy of the given catalog, with new columns appended.
	
	:param params: sewpy params. If ``None``, a default set, with many WIN parameters, is used.
	:param config: sewpy config. If ``None``, a reasonable (?) default is used.
	:param workdir: path where all SExtractor files, settings, and **logs** are kept.
	
	When this function is passed to megalut.meas.run(), the suggested workdir location is, e.g.,::
	
		os.path.join(measdir, "sewpy")
	
	This way all relevant files will be kept together in the measdir, close to the catalogs.
	
	"""
	
	# We make the workdir, to avoid race hazard:
	if not os.path.exists(workdir):
		os.makedirs(workdir)
	
	if params == None:
		params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
			"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
			"FWHM_IMAGE", "BACKGROUND", "FLAGS"]
	
	if config == None:
		config = {"DETECT_MINAREA":5, "ASSOC_RADIUS":5, "ASSOC_TYPE":"NEAREST"}
		
	sew = sewpy.SEW(sexpath=sexpath, params=params, config=config, workdir=workdir, nice=19)
	out = sew(img, assoc_cat=catalog, assoc_xname=xname, assoc_yname=yname, prefix=prefix)
		
	return out["table"]
	
	
