import numpy as np
import utils
import sys, os
from datetime import datetime
import galaxy

import galsim

# use this in front of your code...
#starfield_im.setOrigin(0,0)


def measure(imgfilepath, galaxies, s):
	"""
	I use the positions of your galaxies to extract postage stamps from the image and measure their shapes.
	I add my measurements to your galaxy objects.
	Every galaxy gets them. When I fail, I put its mes_gs_flux to -1.0
	
	s is the stamp size I should extract
	
	"""
	
	# We read in the imgfile
	bigimg = galsim.fits.read(imgfilepath)
	bigimgnp = utils.fromfits(imgfilepath)
	
	shape = bigimgnp.shape
	#print shape
	starttime = datetime.now()
	print "Measuring shapes with galsim AdaptativeMom on %s..." % (os.path.basename(imgfilepath))
	
	failed = 0
	n = len(galaxies)
	
	for (i, gal) in enumerate(galaxies):
		
		sys.stdout.write("\rProgress %i / %i" % (i, n))
		sys.stdout.flush()
	
		# We cut out the postage stamp
		xmin = int(np.clip(int(np.floor(gal.x)) - s/2 + 1, 1, shape[0]-1))
		xmax = int(np.clip(int(np.floor(gal.x)) + s/2 + 1, 1, shape[0]-1))
		ymin = int(np.clip(int(np.floor(gal.y)) - s/2 + 1, 1, shape[1]-1))
		ymax = int(np.clip(int(np.floor(gal.y)) + s/2 + 1, 1, shape[1]-1))
		
		bounds = galsim.BoundsI(xmin, xmax, ymin, ymax)
		gps = bigimg[bounds]
		
		# We measure the moments...
		try:
			
			# Important : we measure only good galaxies, as sometimes the galsim C++ code fails
			# without raising an exception...
			if not gal.isgood():
				raise RuntimeError("We'll skip this one...")
				
			res = galsim.hsm.FindAdaptiveMom(gps)
			
			gal.mes_gs_flux = res.moments_amp
			gal.mes_gs_sigma = res.moments_sigma
			gal.mes_gs_g1 = res.observed_shape.g1
			gal.mes_gs_g2 = res.observed_shape.g2
			gal.mes_gs_x = res.moments_centroid.x
			gal.mes_gs_y = res.moments_centroid.y
			gal.mes_gs_rho4 = res.moments_rho4


		except:
		
			failed += 1
			gal.mes_gs_flux = -1.0
			gal.mes_gs_sigma = 0.0
			gal.mes_gs_g1 = 0.0
			gal.mes_gs_g2 = 0.0
			gal.mes_gs_x = 0.0
			gal.mes_gs_y = 0.0
			gal.mes_gs_rho4 = 0.0
			
	endtime = datetime.now()	
	print "\rDone.                        "
	print "I failed on %i out of %i galaxies (%.1f percent)" % (failed, n, 100.0*float(failed)/float(n))
	print "This measurement took %s" % (str(endtime - starttime))
	

		
	
