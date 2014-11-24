"""
This module is a wrapper around sewfunc.py, specialized to measure only the PSFs.

This specialized wrapper is used when the PSFs in simulated images are repeated for testing purposes.
This becomes necessary because the catalog entry corresponds to each galaxy (where #galaxies >> #PSFs is possible).
"""

import logging
logger = logging.getLogger(__name__)

try:
	import sewpy
except ImportError:
	logger.warning("sewpy is not available, get it here: https://github.com/megalut/sewpy")
	raise

import os, sys
import numpy as np
from astropy.table import Table, Column


def measure(psfimg, catalog, psfxname="psfx", psfyname="psfy",
	    params=None, config=None, workdir=None, sexpath="sex", prefix="psf_"):
	"""
	Returns a copy of the given catalog, with new columns appended.
	
	:param psfimg: either the path to a FITS image, or a galsim image object of the PSF(s).
	:param catalog: astropy table of objects to be measured (each row corresponds to an object)
	:param psfxname: column name containing the PSF x coordinates in pixels
	:param psfyname: idem for y
	:param params: sewpy params. If ``None``, a default set, with many WIN parameters, is used.
	:param config: sewpy config. If ``None``, a reasonable (?) default is used.
	:param workdir: path where all SExtractor files, settings, and **logs** are kept.
	
	When this function is passed to megalut.meas.run(), the suggested workdir location is, e.g.,::
	
		os.path.join(measdir, "sewpy")
	
	This way all relevant files will be kept together in the measdir, close to the catalogs.
	
	"""
	
	# We make the workdir.
	# Indeed, if we leave this to sewpy, there is a race hazard.
	# We cannot use the normal "if exists: os.makedirs()" !
	
	if workdir != None:
		try:
			os.makedirs(workdir)
			logger.debug("Made workdir %s" % (workdir))
		except OSError:
			pass

	if params == None:
		params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
			"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
			"FWHM_IMAGE", "BACKGROUND", "FLAGS"]
	
	if config == None:
		config = {"DETECT_MINAREA":5, "ASSOC_RADIUS":5, "ASSOC_TYPE":"NEAREST"}
		
        # extract all unique (psfx, psfy) pairs from the catalog, and create a temporary PSF catalog
        # create "psf_catalog"
        all_psf_coords = []
        for obj in catalog:
            all_psf_coords += [(obj[psfxname], obj[psfyname]),]
        uniq_psf_coord = list(set(all_psf_coords))
        psf_catalog = Table(rows=uniq_psf_coord, names=(psfxname, psfyname), meta={'name':'psf_catalog'})
        psf_catalog[psfxname].unit = 'pix'
        psf_catalog[psfyname].unit = 'pix'

        # run SExtractor on psfimg; match SExtractor output to PSF catalog
        # create "psf_out" catalog
	sew = sewpy.SEW(sexpath=sexpath, params=params, config=config, workdir=workdir, nice=19)
	psf_out = sew(psfimg, assoc_cat=psf_catalog, assoc_xname=psfxname, assoc_yname=psfyname, prefix=prefix)
		
        # transfer PSF catalog info into the original catalog
        # incorporate "psf_out" into "catalog"
        psf_tags = ['FLAGS_WIN', 'FLAGS']
        for tag in psf_tags:
            catalog.add_columns([Column(name='psf_'+tag, dtype=int, length=len(catalog)),])
        psf_tags = ['FWHM_IMAGE', 'AWIN_IMAGE', 'BWIN_IMAGE', 'THETAWIN_IMAGE', 'FLUX_AUTO',]
        for tag in psf_tags:
            catalog.add_columns([Column(name='psf_'+tag, dtype=float, length=len(catalog)),])
                    
        for obj in catalog:
            if len(psf_out["table"]) == 1:
                index = 0
            else:
                psf_coord = (obj[psfxname], obj[psfyname])
                index = np.where(all_psf_coords==psf_coord)
            for tag in psf_tags:
                obj['psf_'+tag] = psf_out['table'][index]['psf_'+tag]

        ## DEBUG BLOCK
        print catalog
        print catalog.colnames

	return catalog

	
	

"""
def measfct(img, catalog, psfimg=None, workdir=None, stampsize=None, psfstampsize=None):
        '''
	This function is custom-made for the MegaLUT GREAT3 wrapper, and it accepts those
	keywords that great3.meas_obs() and great3.meas_sim() will pass to it.
	All other keyword arguments can directly be set in the function calls below.
        '''
	
	# Run SExtractor on gals
	sexpath = "sex"
	outcat = megalut.meas.sewfunc.measure(img, outcat, workdir=workdir, sexpath=sexpath)

	# Run SExtractor on PSFs
	outcat = megalut.meas.sewfunc_psf.measure(img, outcat, workdir=workdir, sexpath=sexpath)

	# Run FDNT:
	outcat = megalut.meas.fdntfunc.measure(img, catalog, psfimg, 
		psfxname="psfx", psfyname="psfy", stampsize=stampsize, psfstampsize=psfstampsize)
	
	return outcat


"""
