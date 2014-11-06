"""
Functions to help visualizing postage stamps of selected sources in large images.
"""

try:
	import f2n
except ImportError:
	logger.debug("Could not import f2n, no problem if you don't use it")


def pngstampgrid(pngfilepath, img, catalog, xname="x", yname="y", stampsize=100, ncols=5, upsample=4, z1="auto", z2="auto"):
	"""
	I write a grid of stamps corresponding to your catalog in a png image, so that you can visualize those galaxies...
	For this I need f2n, but anyway I'm just a little helper.
	"""
			
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
				(gps, flag) = tools.image.getstamp(x, y, img, stampsize)
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

