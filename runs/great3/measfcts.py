"""
This files holds a user-defined measfct.

It's a very good idea to keep this function in a separate module and not in your
script, so that it can be imported by the multiprocessing pool workers that will call,
it without causing any trouble!
"""

import megalut.meas
import megalut.meas.sewfunc
import megalut.meas.aperphot
import config


def psf(catalog, branch=None):
	"""
	This is to measure PSF shapes when running on the PSF catalog, and therefore the PSF image stamps
	are to be referenced in "img", not in "psf"...
	"""	
	
#	sewpy_config = {"DETECT_MINAREA":6, "DETECT_THRESH":2, "ANALYSIS_THRESH":2,
#		"PHOT_FLUXFRAC":"0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9",
#		"ASSOC_RADIUS":5, "ASSOC_TYPE":"NEAREST"}
#	
#	sewpy_params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
#		"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
#		"FWHM_IMAGE", "KRON_RADIUS", "FLUX_RADIUS(7)", "BACKGROUND", "FLAGS"]
#	
#	catalog = megalut.meas.sewfunc.measfct(catalog, runon="img", config=sewpy_config,
#		params=sewpy_params, sexpath=config.sexpath,
#		prefix="psf_sewpy_")
	
	# We run galsim_adamom :
	catalog = megalut.meas.galsim_adamom.measfct(catalog, stampsize=branch.stampsize(), prefix="psf_adamom_", variant="wider")
	
	# We run skystats:
	catalog = megalut.meas.skystats.measfct(catalog, stampsize=branch.stampsize(), prefix="psf_")
			
	return catalog




def gal(catalog, branch=None):
	"""
	The measfct for galaxies.
	
	"""	
	
#	sewpy_config = {"DETECT_MINAREA":6, "DETECT_THRESH":2, "ANALYSIS_THRESH":2,
#		"PHOT_FLUXFRAC":"0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9",
#		"ASSOC_RADIUS":5, "ASSOC_TYPE":"NEAREST"}
#	
#	sewpy_params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
#		"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
#		"FWHM_IMAGE", "KRON_RADIUS", "FLUX_RADIUS(7)", "BACKGROUND", "FLAGS"]
#	
#	catalog = megalut.meas.sewfunc.measfct(catalog, runon="img", config=sewpy_config,
#		params=sewpy_params, sexpath=config.sexpath)
	
	# We run galsim_adamom :
	catalog = megalut.meas.galsim_adamom.measfct(catalog, stampsize=branch.stampsize(), variant="wider")
	
	# We run skystats:
	catalog = megalut.meas.skystats.measfct(catalog, stampsize=branch.stampsize())
	
	# aperphot:
	catalog = megalut.meas.aperphot.measfct(catalog, radii=(2, 3, 5, 8))
	
	# and snr
	catalog = megalut.meas.snr.measfct(catalog, gain=1.0)
		
	
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
 'skyflag',
 'skystd',
 'skymad',
 'skymean',
 'skymed',
 'skystampsum',
 'aperphot_sb2',
 'aperphot_sb3',
 'aperphot_sb5',
 'aperphot_sb8',
 'snr'
]

removecols = [
		
]



"""
# Some previously used values:

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


['id',
 'ix',
 'iy',
 'snc_type',
 'tru_flux',
 'tru_g1',
 'tru_g2',
 'tru_gain',
 'tru_mu',
 'tru_pixel',
 'tru_rad',
 'tru_read_noise',
 'tru_s1',
 'tru_s2',
 'tru_sersicn',
 'tru_sky_level',
 'tru_type',
 'x',
 'y',
 'psfx',
 'psfy',
 'psf_adamom_flag',
 'psf_adamom_flux',
 'psf_adamom_x',
 'psf_adamom_y',
 'psf_adamom_g1',
 'psf_adamom_g2',
 'psf_adamom_sigma',
 'psf_adamom_rho4',
 'psf_skyflag',
 'psf_skystd',
 'psf_skymad',
 'psf_skymean',
 'psf_skymed',
 'psf_skystampsum',
 'adamom_flag',
 'adamom_flux',
 'adamom_x',
 'adamom_y',
 'adamom_g1',
 'adamom_g2',
 'adamom_sigma',
 'adamom_rho4',
 'skyflag',
 'skystd',
 'skymad',
 'skymean',
 'skymed',
 'skystampsum',
 'aperphot_sb2',
 'aperphot_sb3',
 'aperphot_sb5',
 'aperphot_sb8',
 'snr']

"""


