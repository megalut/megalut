import astropy.units as u
import numpy as np

def ABmag(nu, flux, transmittance=None):
	if transmittance is None:
		def transmittance(nu):
			return 1.
		
	dnu = (-nu[1]+nu[0])  
		
	top = flux * transmittance(nu) * dnu / nu
	top = top.sum()
	top = top.to(u.Jy / u.arcsec / u.arcsec)
	
	down = 3631 * u.Jy / nu * transmittance(nu) * dnu
	down = down.sum()
	
	return -5./2 * np.log10((top/down).value) 
