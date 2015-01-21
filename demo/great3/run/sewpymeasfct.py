"""
This files holds a user-defined measfct.

It's a very good idea to keep this function in a separate module and not in your
script, so that it can be imported by the multiprocessing pool workers that will call,
it without causing any trouble!
"""

import megalut.meas
import megalut.meas.sewfunc
import config


def psf(catalog, branch=None):
	"""
	This is to measure PSF shapes when running on the PSF catalog, and therefore the PSF image stamps
	are to be referenced in "img", not in "psf"...
	"""	
	
	sewpy_config = {"DETECT_MINAREA":6, "DETECT_THRESH":2, "ANALYSIS_THRESH":2,
		"PHOT_FLUXFRAC":"0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9",
		"ASSOC_RADIUS":5, "ASSOC_TYPE":"NEAREST"}
	
	sewpy_params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
		"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
		"FWHM_IMAGE", "KRON_RADIUS", "FLUX_RADIUS(7)", "BACKGROUND", "FLAGS"]
	
	catalog = megalut.meas.sewfunc.measfct(catalog, runon="img", config=sewpy_config,
		params=sewpy_params, sexpath=config.sexpath,
		prefix="psf_sewpy_")
	
	# We run galsim_adamom :
	catalog = megalut.meas.galsim_adamom.measfct(catalog, stampsize=branch.stampsize(), measuresky=True, prefix="psf_adamom_")
		
	return catalog




def galaxies(catalog, branch=None):
	"""
	The normal measfct, for galaxies.
	
	"""	
	
	sewpy_config = {"DETECT_MINAREA":6, "DETECT_THRESH":2, "ANALYSIS_THRESH":2,
		"PHOT_FLUXFRAC":"0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9",
		"ASSOC_RADIUS":5, "ASSOC_TYPE":"NEAREST"}
	
	sewpy_params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
		"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
		"FWHM_IMAGE", "KRON_RADIUS", "FLUX_RADIUS(7)", "BACKGROUND", "FLAGS"]
	
	catalog = megalut.meas.sewfunc.measfct(catalog, runon="img", config=sewpy_config,
		params=sewpy_params, sexpath=config.sexpath)
	
	# We run galsim_adamom :
	catalog = megalut.meas.galsim_adamom.measfct(catalog, stampsize=branch.stampsize(), measuresky=True)
		
	return catalog



groupcols = [
'sewpy_XWIN_IMAGE',
'sewpy_YWIN_IMAGE',
'sewpy_AWIN_IMAGE',
'sewpy_BWIN_IMAGE',
'sewpy_THETAWIN_IMAGE',
'sewpy_FLUX_WIN',
'sewpy_FLUXERR_WIN',
'sewpy_NITER_WIN',
'sewpy_FLAGS_WIN',
'sewpy_FLUX_AUTO',
'sewpy_FLUXERR_AUTO',
'sewpy_FWHM_IMAGE',
'sewpy_KRON_RADIUS',
'sewpy_FLUX_RADIUS',
'sewpy_FLUX_RADIUS_1',
'sewpy_FLUX_RADIUS_2',
'sewpy_FLUX_RADIUS_3',
'sewpy_FLUX_RADIUS_4',
'sewpy_FLUX_RADIUS_5',
'sewpy_FLUX_RADIUS_6',
'sewpy_BACKGROUND',
'sewpy_FLAGS',
'sewpy_assoc_flag',
'adamom_flag',
'adamom_flux',
'adamom_x',
'adamom_y',
'adamom_g1',
'adamom_g2',
'adamom_sigma',
'adamom_rho4',
'adamom_skystd',
'adamom_skymad',
'adamom_skymean',
'adamom_skymed'
]

removecols = []






