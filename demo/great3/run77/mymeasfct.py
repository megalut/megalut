"""
This files holds a user-defined measfct.

It's a very good idea to keep this function in a separate module and not in your
script, so that it can be imported by the multiprocessing pool workers that will call,
it without causing any trouble!
"""

import megalut.meas
import megalut.meas.sewfunc


def sewpyadamom(catalog, branch=None):
	"""
	This function is made to demonstrate the MegaLUT GREAT3 wrapper.
	
	Given that measurement functions might need adjustments depending on the branch,
	it seems useful to pass the branch object to them.
	"""	

	# We run SExtractor on the "img" stamps:
	
	sewpy_config = {"DETECT_MINAREA":6, "DETECT_THRESH":2, "ANALYSIS_THRESH":2,
		"PHOT_FLUXFRAC":"0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9",
		"ASSOC_RADIUS":5, "ASSOC_TYPE":"NEAREST"}
	
	sewpy_params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
		"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
		"FWHM_IMAGE", "KRON_RADIUS", "FLUX_RADIUS(7)", "BACKGROUND", "FLAGS"]
	
	catalog = megalut.meas.sewfunc.measfct(catalog, runon="img", config=sewpy_config,
		params=sewpy_params, sexpath="/vol/software/software/astro/sextractor/sextractor-2.19.5/64bit/bin/sex")
	
	# We run galsim_adamom :
	catalog = megalut.meas.galsim_adamom.measfct(catalog, stampsize=branch.stampsize(), measuresky=True)
		
	return catalog


