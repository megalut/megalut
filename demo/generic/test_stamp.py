"""
This file is intended to test the stamp extraction and its centering.
It is linked to issue https://github.com/megalut/megalut/issues/63 
At some point, this should be considered as an "unit-test".  
"""
import logging
logging.basicConfig(level=logging.INFO)

import megalut.tools.image
import megalut.sim
import numpy as np
import galsim
import pylab as plt
###################################################################################################
# Parameters
simgalimgfilepath = "test/single_stamp.fits"
stampsize = 16
n = 100

class Flux(megalut.sim.params.Params):
	def get_flux(self):
		return 200.0
		
params = Flux()

###################################################################################################
def get_centroids(img, n, stampsize, simcat):
	# Initialisation
	x = np.arange(stampsize)
	x, y = np.meshgrid(x, x)
	moments = np.zeros([n*n, 2])
	adamom = np.zeros_like(moments)
	catpos = np.zeros_like(moments)

	# Load and extract stamp
	for ii, line in enumerate(simcat):
		stamp, flag = megalut.tools.image.getstamp(line["x"], line["y"], img, stampsize)
		
		if flag == 1 : 
			raise ValueError("Could not extract stamp at %1.1f, %1.1f", (line["x"], line["y"]))
	
		try:
			res = galsim.hsm.FindAdaptiveMom(stamp)
			
			gx = res.moments_centroid.x - stamp.origin().x
			gy = res.moments_centroid.y - stamp.origin().y
		except :
			gx = np.nan 
			gy = np.nan
			
		adamom[ii] = [gx, gy]
	
		den = np.sum(stamp.array)
		Ix = np.sum(stamp.array * x) / den
		Iy = np.sum(stamp.array * y) / den
		if np.abs(Ix - stampsize / 2.) > 2 or np.abs(Iy - stampsize / 2.) > 2 :
			Ix = np.nan
			Iy = np.nan
		moments[ii] = [Ix, Iy]
	
		sx = line["x"] - stamp.origin().x
		sy = line["y"] - stamp.origin().y
		catpos[ii] = [sx, sy]
		
	return moments, adamom, catpos

if __name__ == "__main__":
	# Simulation of the stamp
	simcat = megalut.sim.stampgrid.drawcat(params, n, stampsize)
	megalut.sim.stampgrid.drawimg(simcat,simgalimgfilepath=simgalimgfilepath)
	
	# Loads the image
	img = megalut.tools.image.loadimg(simgalimgfilepath)
	
	# Computes the centroids
	moments, adamom, catpos = get_centroids(img, n, stampsize, simcat)
	
	# Removes nans from array
	nbnans = np.logical_not(np.isnan(adamom[:,0]))
	print '%d out of %d adamom failures were removed' % (np.size(nbnans[nbnans==False]), n*n)
	adamom = adamom[nbnans]
	
	# Removes nans from array
	nbnans = np.logical_not(np.isnan(moments[:,0]))
	print '%d out of %d moments failures were removed' % (np.size(nbnans[nbnans==False]), n*n)
	moments = moments[nbnans]


	print 'Moments       :', np.mean(moments, axis=0), '+/-', np.std(moments, axis=0),
	print '==> ', np.mean(moments, axis=0) - np.mean(catpos, axis=0)
	print 'Adaptative mom:', np.mean(adamom, axis=0), '+/-', np.std(adamom, axis=0),
	print '==> ', np.mean(adamom, axis=0) - np.mean(catpos, axis=0)
	print 'Catalog value :', np.mean(catpos, axis=0)
	
	f, axarr = plt.subplots(2, 2)
	axarr[0, 0].hist(moments[:,0])
	axarr[0, 0].axvline(x=np.mean(moments, axis=0)[0], lw=2, c="k")
	axarr[0, 0].axvline(x=np.mean(catpos, axis=0)[0], lw=2, c="r")
	axarr[0, 0].set_xlabel("x, Moments")
	
	axarr[0, 1].hist(moments[:,1])
	axarr[0, 1].axvline(x=np.mean(moments, axis=0)[1], lw=2, c="k")
	axarr[0, 1].axvline(x=np.mean(catpos, axis=0)[1], lw=2, c="r")
	axarr[0, 1].set_xlabel("y, Moments")

	axarr[1, 0].hist(adamom[:,0])
	axarr[1, 0].axvline(x=np.mean(adamom, axis=0)[0], lw=2, c="k")
	axarr[1, 0].axvline(x=np.mean(catpos, axis=0)[0], lw=2, c="r")
	axarr[1, 0].set_xlabel("x, adamom")
	
	axarr[1, 1].hist(adamom[:,1])
	axarr[1, 1].axvline(x=np.mean(adamom, axis=0)[1], lw=2, c="k")
	axarr[1, 1].axvline(x=np.mean(catpos, axis=0)[1], lw=2, c="r")
	axarr[1, 1].set_xlabel("y, adamom")
	plt.show()