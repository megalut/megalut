import megalut.meas


def default(catalog, stampsize):
	"""
	Default measfct, runs on "img".
	"""	
	
	# HSM adamom
	catalog = megalut.meas.galsim_adamom.measfct(catalog, stampsize=stampsize)
	
	# And skystats
	catalog = megalut.meas.skystats.measfct(catalog, stampsize=stampsize)
	
	# And snr
	
	print "wait why is this gain 1.7"
	exit()
	catalog = megalut.meas.snr.measfct(catalog, gain=1.7)
	
	return catalog
	
	"""
	# First we run SExtractor:
	
	sewpy_config = {"DETECT_MINAREA":5, "DETECT_THRESH":2.0, "ANALYSIS_THRESH":2.0,
		"PHOT_FLUXFRAC":"0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9",
		"PHOT_APERTURES":"20, 50",
		"BACK_TYPE":"MANUAL", "BACK_VALUE":0.0,
		"ASSOC_RADIUS":5, "ASSOC_TYPE":"NEAREST",
		"FILTER_NAME":"/vol/fohlen11/fohlen11_1/mtewes/SEx_FILTERs/gauss_3.0_5x5.conv"
		}
		
	# "FILTER_NAME":"/vol/fohlen11/fohlen11_1/mtewes/SEx_FILTERs/gauss_3.0_5x5.conv"
	# "DETECT_MINAREA":5, "DETECT_THRESH":2.0, "ANALYSIS_THRESH":2.0,
	
	
	sewpy_params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
		"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
		"FWHM_IMAGE", "KRON_RADIUS", "FLUX_RADIUS(7)", "FLUX_APER(2)", "FLUXERR_APER(2)", "BACKGROUND", "FLAGS"]
	
	
	catalog = megalut.meas.sewfunc.measfct(catalog,
		config=sewpy_config,
		params=sewpy_params,
		sexpath="/vol/software/software/astro/sextractor/sextractor-2.19.5/64bit/bin/sex",
		prefix="sewpy_"
		)
	
	# We compute some further useful fields:
	
	#catalog["sewpy_snr"] = catalog["sewpy_FLUX_AUTO"] / catalog["sewpy_FLUXERR_AUTO"]	
	"""
	"""
	# And HSM adamom

	catalog = megalut.meas.galsim_adamom.measfct(catalog, stampsize=stampsize)
	
	# Fourier
	#catalog = megalut.meas.fourier.measfct(catalog, stampsize=stampsize)
	
	# And skystats
	catalog = megalut.meas.skystats.measfct(catalog, stampsize=stampsize)

	
	return catalog
	"""


default_groupcols = [
'adamom_flag',
'adamom_flux',
'adamom_x',
'adamom_y',
'adamom_g1',
'adamom_g2',
'adamom_sigma',
'adamom_rho4',
'skystd',
'skymad',
'skymean',
'skymed',
'skystampsum',
'skyflag',
'snr'
]


#'fourier_x',
#'fourier_y',
#'fourier_adamom_flag',
#'fourier_adamom_flux',
#'fourier_adamom_x',
#'fourier_adamom_y',
#'fourier_adamom_g1',
#'fourier_adamom_g2',
#'fourier_adamom_sigma',
#'fourier_adamom_rho4',
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


default_removecols = []
