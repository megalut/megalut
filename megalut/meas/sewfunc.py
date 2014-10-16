"""
This module provides a measurement function using SExtractor via sewpy that can be
passed to meas.run.multi().

You could also simply define such a function yourself, to control all parameters in 
a most flexible way.
"""


import sewpy



def measure(img, catalog, xname="x", yname="y", params=None, config=None, workdir=None,
	sexpath="sex", prefix="sewpy_"):
	"""
	Looking at my API, I am very similar to galsim_adamom.measure().
	I return a copy of your catalog with new columns appended.
	
	:param params: sewpy params. If ``None``, I'll use a default set with many WIN parameters.
	:param config: sewpy config. If ``None``, I'll use a reasonable (?) default.
	
	"""
	
	if params == None:
		params = ["XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
			"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
			"FWHM_IMAGE", "BACKGROUND", "FLAGS"]
	
	if config == None:
		config = {"DETECT_MINAREA":10}
		
	sew = sewpy.SEW(sexpath=sexpath, params=params, config=config, workdir=workdir, nice=19)
	out = se.run(imgpath, assoc_cat=catalog, assoc_xname=xname, assoc_yname=yname, prefix=prefix)
		
	return out["table"]
	
	
