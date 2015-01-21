"""
This files holds a user-defined measfct.

It's a very good idea to keep this function in a separate module and not in your
script, so that it can be imported by the multiprocessing pool workers that will call,
it without causing any trouble!
"""

import megalut.meas
import megalut.meas.galsim_adamom

def psf(catalog, branch=None):
	"""
	This is to measure PSF shapes when running on the PSF catalog, and therefore the PSF image stamps
	are to be referenced in "img", not in "psf"...
	"""	

	catalog = megalut.meas.galsim_adamom.measfct(catalog, stampsize=branch.stampsize(), 
		measuresky=True, prefix="psf_adamom_")
	
	return catalog


def galaxies(catalog, branch=None):
	"""
	The normal measfct, for galaxies.
	
	"""	

	# We run galsim_adamom :
	catalog = megalut.meas.galsim_adamom.measfct(catalog, stampsize=branch.stampsize(), measuresky=True)
		
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
'adamom_skystd',
'adamom_skymad',
'adamom_skymean',
'adamom_skymed'
]

removecols = []

