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



def loadimg(imgfilepath):
	"""
	Uses GalSim to load and image from a FITS file, enforcing that the GalSim origin is (0, 0).
	
	:param imgfilepath: path to FITS image
	:returns: galsim image
	"""
	
	logger.info("Loading FITS image %s..." % (os.path.basename(imgfilepath)))
	bigimg = galsim.fits.read(imgfilepath)
	bigimg.setOrigin(0,0)
	logger.info("Done with loading %s, shape is %s" % (os.path.basename(imgfilepath), bigimg.array.shape))
	
	logger.warning("The origin and stampsize conventions are new and should be tested !")
	
	bigimg.origimgfilepath = imgfilepath # Just to keep this somewhere
	
	return bigimg



def measure(bigimg, catalog, xname="x", yname="y", stampsize=100, prefix="mes_adamom"):
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
		astropy.table.Column(name=prefix+"_flag", data=np.zeros(len(output), dtype=int)),
		astropy.table.Column(name=prefix+"_flux", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"_x", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"_y", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"_g1", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"_g2", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"_sigma", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"_rho4", dtype=float, length=len(output))
	])
	
	# We could have boolean columns:
	#astropy.table.Column(name=prefix+"_ok", data=np.zeros(len(output), dtype=bool))
	# One could use MaskedColumn here !
	#astropy.table.MaskedColumn(name="mes_adamom_flux", dtype=float, length=len(output), fill_value=-1)
	
	# Let's save something useful to the meta dict
	output.meta[prefix + "_imgfilepath"] = bigimg.origimgfilepath
	output.meta[prefix + "_xname"] = xname
	output.meta[prefix + "_yname"] = yname
	
	n = len(output)
	
	# And loop
	for gal in output:
		
		# Some simplistic progress indication:
		if gal.index%5000 == 0:
			logger.info("%6.2f%% done (%i/%i) " % (100.0*float(gal.index)/float(n), gal.index, n))
		
		(x, y) = (gal[xname], gal[yname])
		(gps, flag) = getstamp(x, y, bigimg, stampsize)
		
		if flag != 0:
			logger.debug("Galaxy not fully within image:\n %s" % (str(gal)))
			gal[prefix+"_flag"] = flag
			continue
		
		# We measure the moments... galsim may fail from time to time, hence the try:
		try:
			res = galsim.hsm.FindAdaptiveMom(gps)
			
		except:
			# This is awesome, but clutters the output 
			#logger.exception("GalSim failed on: %s" % (str(gal)))
			logger.debug("GalSim failed on:\n %s" % (str(gal)))	
			gal[prefix + "_flag"] = 3	
			continue
		
		gal[prefix+"_flux"] = res.moments_amp
		gal[prefix+"_x"] = res.moments_centroid.x
		gal[prefix+"_y"] = res.moments_centroid.y
		gal[prefix+"_g1"] = res.observed_shape.g1
		gal[prefix+"_g2"] = res.observed_shape.g2
		gal[prefix+"_sigma"] = res.moments_sigma
		gal[prefix+"_rho4"] = res.moments_rho4

		# If we made it so far, we check that the centroid is roughly ok:
		if np.hypot(x - gal[prefix+"_x"], y - gal[prefix+"_y"]) > 10.0:
			gal[prefix + "_flag"] = 2
		
	
	endtime = datetime.now()	
	logger.info("All done")

	nfailed = np.sum(output[prefix+"_flag"] > 0)
	
	logger.info("I failed on %i out of %i sources (%.1f percent)" % (nfailed, n, 100.0*float(nfailed)/float(n)))
	logger.info("This measurement took %.3f ms per galaxy" % (1e3*(endtime - starttime).total_seconds() / float(n)))
	
	return output



		
def getstamp(x, y, bigimg, stampsize):
	"""
	I prepare a bounded galsim image stamp "centered" at position (x, y) of your input galsim image.
	You can use the array attribute of the stamp if you want to get the actual pixels.
	
	:returns: a tuple(stamp, flag)
	"""

	assert int(stampsize)%2 == 0 # checking that it's even

	xmin = int(np.floor(x)) - int(stampsize)/2 + 1
	xmax = int(np.floor(x)) + int(stampsize)/2
	ymin = int(np.floor(y)) - int(stampsize)/2 + 1
	ymax = int(np.floor(y)) + int(stampsize)/2
			
	assert ymax - ymin == stampsize - 1
	assert xmax - xmin == stampsize - 1
	
	# We check that these bounds are fully within the image
	if xmin < bigimg.getXMin() or xmax > bigimg.getXMax()+1 or ymin < bigimg.getYMin() or ymax > bigimg.getYMax()+1:
		return (None, 1)
		
	# We prepare the stamp
	bounds = galsim.BoundsI(xmin, xmax, ymin, ymax)
	stamp = bigimg[bounds] # galaxy postage stamp
	assert stamp.array.shape == (stampsize, stampsize)
	
	return (stamp, 0)
	
	
	
	
	
#def npstampgrid(bigimg, catalog, xname="x", yname="y", stampsize=100):
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
#		(gps, flag) = getstamp(x, y, bigimg, stampsize)
#		if flag != 0:
#			stamplist.append(np.zeros(stampsize, stampsize))
#		else:
#			stamplist.append(gps.array)
#	
#	big = np.vstack(stamplist)
#	return big



def pngstampgrid(pngfilepath, bigimg, catalog, xname="x", yname="y", stampsize=100, ncols=5, upsample=4, z1="auto", z2="auto"):
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
				(gps, flag) = getstamp(x, y, bigimg, stampsize)
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
	
	
	
	
