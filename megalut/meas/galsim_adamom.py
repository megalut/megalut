import numpy as np
import sys, os
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

import galsim
from .. import utils
from .. import catalog as megalutcatalog


# use this in front of your code...
#starfield_im.setOrigin(0,0)


def measure(imgfilepath, catalog, stampsize=100):
	"""
	I use the positions "x" and "y" of the input catalog to extract postage stamps from the image and measure their shapes.
	
	:param imgfilepath: FITS image
	:param catalog: Catalog of objects that I should measure
	:param stampsize: width and height of stamps
	
	"""
	
	starttime = datetime.now()
	logger.info("Measuring shapes on %s..." % (os.path.basename(imgfilepath)))
	
	# We read in the imgfile
	bigimg = galsim.fits.read(imgfilepath)
	bigimg.setOrigin(0,0)
	logger.warning("The origin and stamp size conventions of this code should be tested !")
	
	bigimgnp = utils.fromfits(imgfilepath)
	shape = bigimgnp.shape
	
	failed = 0
	n = len(catalog)
	
	measgalaxies = []
	
	for (i, gal) in enumerate(catalog.data.values()): # So we work on copies
	
		x = gal.fields["x"]
		y = gal.fields["y"]
		
		#sys.stdout.write("\rProgress %i / %i" % (i, n))
		#sys.stdout.flush()
	
		# We cut out the postage stamp
		xmin = int(np.clip(int(np.floor(x)) - stampsize/2 + 1, 1, shape[0]-1))
		xmax = int(np.clip(int(np.floor(x)) + stampsize/2 + 1, 1, shape[0]-1))
		ymin = int(np.clip(int(np.floor(y)) - stampsize/2 + 1, 1, shape[1]-1))
		ymax = int(np.clip(int(np.floor(y)) + stampsize/2 + 1, 1, shape[1]-1))
		
		bounds = galsim.BoundsI(xmin, xmax, ymin, ymax)
		gps = bigimg[bounds] # galaxy postage stamp
		
		# We measure the moments...
		
		try:
			res = galsim.hsm.FindAdaptiveMom(gps)
			
			gal.fields["mes_gs_flux"] = res.moments_amp
			gal.fields["mes_gs_sigma"] = res.moments_sigma
			gal.fields["mes_gs_g1"] = res.observed_shape.g1
			gal.fields["mes_gs_g2"] = res.observed_shape.g2
			gal.fields["mes_gs_x"] = res.moments_centroid.x
			gal.fields["mes_gs_y"] = res.moments_centroid.y
			gal.fields["mes_gs_rho4"] = res.moments_rho4

		except:		
			logger.debug("Failed on %s" % (str(gal)))
			failed += 1
			

		measgalaxies.append(gal)
		
		
	endtime = datetime.now()	
	#print "\rDone.                        "
	
	logger.info("I failed on %i out of %i sources (%.1f percent)" % (failed, n, 100.0*float(failed)/float(n)))
	logger.info("This measurement took %.3f ms per galaxy" % (1e3*(endtime - starttime).total_seconds() / float(n)))
	
	return megalutcatalog.Catalog(measgalaxies, meta={"imgfilepath":imgfilepath})

		
	
