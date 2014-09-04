

import astropy.table


import logging
logger = logging.getLogger(__name__)



def readcat(filepath):
	"""
	
	"""
	return astropy.table.Table.read(filepath, hdu=1) # Despite beeing not documented, this hdu=1 works !



def removejunk(cat):
	"""
	Tries to make those catalogs a bit smaller by removing some columns
	"""
	
	toremove = [
		"MAG_APER_i", "MAGERR_APER_i", "FLUX_APER_i", "FLUXERR_APER_i",
		"MAG_APER_y", "MAGERR_APER_y", "FLUX_APER_y", "FLUXERR_APER_y",
		"MAG_APER_z", "MAGERR_APER_z", "FLUX_APER_z", "FLUXERR_APER_z",
		"MAG_APER_r", "MAGERR_APER_r", "FLUX_APER_r", "FLUXERR_APER_r",
		"MAG_APER_g", "MAGERR_APER_g", "FLUX_APER_g", "FLUXERR_APER_g",
		"MAG_APER_u", "MAGERR_APER_u", "FLUX_APER_u", "FLUXERR_APER_u",
		"MAG_APER", "MAGERR_APER",
		"PZ_full"
	]
	
	for colname in toremove:
		if colname not in cat.colnames:
			logger.warning("No %s in cat" % (colname))
			continue
		
		cat.remove_column(colname)
	




def computepos(imgfilepath, cat):
	"""
	I use the fits header WCS to compute the pixel postions of the galaxies in cat.
	"""


	pass



