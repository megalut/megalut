import megalut.meas


def default(catalog, stampsize):
	"""
	Default measfct, runs on "img".
	"""	
	
	# HSM adamom
	catalog = megalut.meas.galsim_adamom.measfct(catalog, stampsize=stampsize, variant="wider")
	
	# And skystats
	catalog = megalut.meas.skystats.measfct(catalog, stampsize=stampsize)
	
	# And snr
	catalog = megalut.meas.snr.measfct(catalog, gain=50.0)
	
	return catalog
	
	


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
