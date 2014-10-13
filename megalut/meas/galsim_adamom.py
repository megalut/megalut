"""
Shape measurement with GalSim's adaptive moments (from its "hsm" module).
"""

import numpy as np
import sys, os
import copy
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

import astropy.table
import galsim

from .. import gsutils



def measure(img, catalog, xname="x", yname="y", stampsize=100, prefix="adamom_"):
	"""
	I use the pixel positions provided via the input table to extract postage stamps from the image and measure their shape parameters.
	I return a copy of your input catalog with the new columns appended. One of these colums is the flag:
	
	* 0: OK
	* 1: stamp is not fully within image
	* 2: galsim centroid failed (distance > 10 pixels...)
	* 3: galsim failed
	
	:param img: galsim image
	:param catalog: astropy table of objects that I should measure
	:param xname: column name containing the x coordinates in pixels
	:param yname: idem for y
	:param stampsize: width = height of stamps, has to be even
	:type stampsize: int
	:param prefix: a string to prefix the field names that I'll write
		
	:returns: astropy table
	
	"""
	
	assert int(stampsize)%2 == 0 # checking that it's even
	
	starttime = datetime.now()
	logger.info("Starting shape measurements on %ix%i stamps" % (stampsize, stampsize))
	
	# We prepare an output table with all the required columns
	output = copy.deepcopy(catalog)
	output.add_columns([
		astropy.table.Column(name=prefix+"flag", data=np.zeros(len(output), dtype=int)),
		astropy.table.Column(name=prefix+"flux", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"x", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"y", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"g1", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"g2", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"sigma", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"rho4", dtype=float, length=len(output))
	])
	
	# We could have boolean columns:
	#astropy.table.Column(name=prefix+"ok", data=np.zeros(len(output), dtype=bool))
	# One could use MaskedColumn here !
	#astropy.table.MaskedColumn(name="mes_adamom_flux", dtype=float, length=len(output), fill_value=-1)
	
	# Let's save something useful to the meta dict
	output.meta[prefix + "xname"] = xname
	output.meta[prefix + "yname"] = yname
	
	# We do not store this long string here, as it leads to problems when saving the cat to FITS
	#output.meta[prefix + "imgfilepath"] = img.origimgfilepath
	
	n = len(output)
	
	# And loop
	for gal in output:
		
		# Some simplistic progress indication:
		if gal.index%5000 == 0:
			logger.info("%6.2f%% done (%i/%i) " % (100.0*float(gal.index)/float(n), gal.index, n))
		
		(x, y) = (gal[xname], gal[yname])
		(gps, flag) = gsutils.getstamp(x, y, img, stampsize)
		
		if flag != 0:
			logger.debug("Galaxy not fully within image:\n %s" % (str(gal)))
			gal[prefix+"flag"] = flag
			continue
		
		# We measure the moments... galsim may fail from time to time, hence the try:
		try:
			res = galsim.hsm.FindAdaptiveMom(gps)
			
		except:
			# This is awesome, but clutters the output 
			#logger.exception("GalSim failed on: %s" % (str(gal)))
			# So insted of logging this as an exception, we use debug, but include the tarceback :
			logger.debug("GalSim failed on:\n %s" % (str(gal)), exc_info = True)	
			gal[prefix + "flag"] = 3	
			continue
		
		gal[prefix+"flux"] = res.moments_amp
		gal[prefix+"x"] = res.moments_centroid.x + 1.0 # Not fully clear why this +1 is needed. Maybe it's the setOrigin(0, 0).
		gal[prefix+"y"] = res.moments_centroid.y + 1.0 # But I would expect that GalSim would internally keep track of these origin issues.
		gal[prefix+"g1"] = res.observed_shape.g1
		gal[prefix+"g2"] = res.observed_shape.g2
		gal[prefix+"sigma"] = res.moments_sigma
		gal[prefix+"rho4"] = res.moments_rho4

		# If we made it so far, we check that the centroid is roughly ok:
		if np.hypot(x - gal[prefix+"x"], y - gal[prefix+"y"]) > 10.0:
			gal[prefix + "flag"] = 2
	
	endtime = datetime.now()	
	logger.info("All done")

	nfailed = np.sum(output[prefix+"flag"] > 0)
	
	logger.info("I failed on %i out of %i sources (%.1f percent)" % (nfailed, n, 100.0*float(nfailed)/float(n)))
	logger.info("This measurement took %.3f ms per galaxy" % (1e3*(endtime - starttime).total_seconds() / float(n)))
	
	return output

	
#def npstampgrid(img, catalog, xname="x", yname="y", stampsize=100):
#	"""
#	I build a numpy array with stamps, intended for visualization
#	"""
#
#	#n = len(catalog)
#	#nrows = int(np.ceil(n/10))
#	#big = np.zeros((10*stampsize, nrows*stampsize))
#	#print n, nrows
#	
#	stamplist = []
#	for gal in catalog:
#		(x, y) = (gal[xname], gal[yname])
#		(gps, flag) = getstamp(x, y, img, stampsize)
#		if flag != 0:
#			stamplist.append(np.zeros(stampsize, stampsize))
#		else:
#			stamplist.append(gps.array)
#	
#	big = np.vstack(stamplist)
#	return big



def pngstampgrid(pngfilepath, img, catalog, xname="x", yname="y", stampsize=100, ncols=5, upsample=4, z1="auto", z2="auto"):
	"""
	I write a grid of stamps corresponding to your catalog in a png image, so that you can visualize those galaxies...
	For this I need f2n, but anyway I'm just a little helper.
	"""
	
	try:
		import f2n
	except:
		logger.exception("Could not import f2n, will skip this...")
		return
		
	n = len(catalog)
	nrows = int(np.ceil(float(n)/float(ncols)))
		
	stamprows = []
	for nrow in range(nrows):
		stamprow = []
		for ncol in range(ncols):
			
			index = ncol + ncols*nrow
			if index < n: # Then we have a galaxy to show
				gal = catalog[index]
				(x, y) = (gal[xname], gal[yname])
				(gps, flag) = gsutils.getstamp(x, y, img, stampsize)
				npstamp = gps.array
				
				f2nstamp = f2n.f2nimage(numpyarray=npstamp, verbose=False)

				f2nstamp.setzscale(z1, z2)
				f2nstamp.makepilimage("log", negative = False)
				f2nstamp.upsample(upsample)
			
				txt = [
					"%i (%i, %i)" % (gal.index, x, y),
				]
				f2nstamp.writeinfo(txt, colour=(255, 255, 100))
				
			else: # No more galaxies, we just fill the splot with a grey empty stamp.
				npstamp = np.zeros((stampsize, stampsize))
				f2nstamp = f2n.f2nimage(numpyarray=npstamp, verbose=False)
				f2nstamp.setzscale(-1.0, 1.0)
				f2nstamp.makepilimage("lin", negative = False)
				f2nstamp.upsample(4)
			
			
			stamprow.append(f2nstamp)
		stamprows.append(stamprow)
	f2n.compose(stamprows, pngfilepath)
	logger.info("Wrote %s" % (pngfilepath))
	
	
	
	

