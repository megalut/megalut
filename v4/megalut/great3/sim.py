"""
Use galsim to draw simulated stamps into a FITS image
"""

import numpy as np
import galsim
import math
import random
import os
import sys
from datetime import datetime

import megalut



def measuresky(fitsfilepath):
	"""
	Quick and dirty measurement of sky level and sky sigma for GREAT3 data.
	"""
	
	array = megalut.utils.fromfits(fitsfilepath)
	#print array.shape
	
	sky = np.median(array[0,:])
	sig1 = np.std(array[0,:])
	sig2 = np.std(array[-1,:])
	sig3 = np.std(array[:,0])
	sig4 = np.std(array[:,-1])
	sig = np.mean(np.array([sig1, sig2, sig3, sig4]))
	
	return (sky, sig)



def measurestamp(stamp, s=96):
	"""
	Give me a stamp (galsim.InterpolatedImage), I measure some moment-stuff on it.
	"""
	
		
	try:
		stamp_image = galsim.ImageF(s, s)
		stamp_image.setScale(1.0)
		stamp.draw(stamp_image)
		res = galsim.hsm.FindAdaptiveMom(stamp_image)
		
		flux = res.moments_amp
		sigma = res.moments_sigma
		g1 = res.observed_shape.g1
		g2 = res.observed_shape.g2
		x = res.moments_centroid.x
		y = res.moments_centroid.y
		rho4 = res.moments_rho4

	except:
		flux = -1.0
		sigma = 0.0
		g1 = 0.0
		g2 = 0.0
		x = 0.0
		y = 0.0
		rho4 = 0.0
	
	
	out = {"flux":flux, "sigma":sigma, "g1":g1, "g2":g2, "x":x, "y":y, "rho4":rho4}
	#print out
	return out

	
		
def drawsim(simparams,
	s, n, nimg,
	obspsfimgfilepath,
	simgalimgfilepath,
	simgalfilepath,
	is_psfvar,
	current_subfield,
	stars=None,
	random_psf=False,
	simtrugalimgfilepath = None,
	simpsfimgfilepath = None,
	measurepsf = False
	):
	"""
	Function to draw simulations in the scope of GREAT3 data.
	
	simparams is a megalut.simparams.SimParams object containing all the serious stuff.
	
	s = the stamp size
	n**2 = nbr of stamps per image
	nimg = how many images with n**2 stamps to draw
	
	obspsfimgfilepath : the input PSF file
	simgalimgfilepath : where I write my output image
	simtrugalimgfilepath : where I write the image without convolution and noise
	simpsfimgfilepath : where I write the PSFs
	
	I write all these images to disk, and
	return a list of simulated Galaxy objects.
	

	"""
	
	starttime = datetime.now()	
	total_count=0
	
	# Attempt to speed up the convolutions
	fast_GSParams = None #galsim.GSParams()
	# OK this makes no sense, leave it to None.
	
	"""
	things I tried to see if they influence :
	alias_threshold = 0.1 # Higher should be faster ?
	maxk_threshold = 0.01 # Higher is faster
	
	xvalue_accuracy : no influence !?
	
	kvalue_accuracy = 1.e-2 # higher is faster
	
	Default values for these GSParams, from the .h file :
	
	GSParams() :
  152             minimum_fft_size(128),
  153             maximum_fft_size(4096),
  154             alias_threshold(5.e-3),
  155             stepk_minimum_hlr(5.),
  156             maxk_threshold(1.e-3),
  157 
  158             kvalue_accuracy(1.e-5),
  159             xvalue_accuracy(1.e-5),
  160             table_spacing(1.),
  161 
  162             realspace_relerr(1.e-3),
  163             realspace_abserr(1.e-6),
  164             integration_relerr(1.e-5),
  165             integration_abserr(1.e-7),
  166 
  167             shoot_accuracy(1.e-5),
  168             shoot_relerr(1.e-6),
  169             shoot_abserr(1.e-8),
  170             allowed_flux_variation(0.81),
  171             range_division_for_extrema(32),
  172             small_fraction_of_flux(1.e-4)
  173             {}
  174
	
	
	example :
	big_fft_params = galsim.GSParams(maximum_fft_size = 10240)
    >>> conv = galsim.Convolve([gal,psf,pix],gsparams=big_fft_params)
	
	"""

	if is_psfvar:
		if stars==None: raise IOError("It's variable PSF branch, you need to give a list of stars for the PSF!")

		psf_field_xy_pos = []
		psf_field_tru_pos = []

		psf_tile_xy_pos = []
		psf_tile_tru_pos = []

		
		get_fname = stars[0]
		shear_type = stars[1]
		min_snr=simparams.get_star_min_snr()

#		else:
		import time
		message = 'Preparing the PSFs. This could take a while...\nSubfields: '
		sys.stdout.write(message)
		sys.stdout.flush()
		if shear_type == "constant": nsub = 1
		else: nsub = 20
		for subfield in range(current_subfield,current_subfield+nsub):
			sys.stdout.write('%03i, ' % subfield)
			sys.stdout.flush()
			im = galsim.fits.read(obspsfimgfilepath(subfield))

			substars = megalut.utils.readpickle(get_fname(subfield))
			for iik, st in enumerate(substars):
				if st.isbrighter(min_snr): 
					psf_field_xy_pos.append([subfield,st.x,st.y])
					psf_field_tru_pos.append(st.get_xy_field_deg())

					psf_tile_xy_pos.append(st.get_xy_tile())
					psf_tile_tru_pos.append(st.get_xy_tile_deg())


			del substars, im

		im = []
		subfield=None
		message = 'Done.\n'
		sys.stdout.write(message)
		sys.stdout.flush()

		psf_field_xy_pos=np.asarray(psf_field_xy_pos)
		psf_field_tru_pos=np.asarray(psf_field_tru_pos)
		psf_tile_xy_pos=np.asarray(psf_tile_xy_pos)
		psf_tile_tru_pos=np.asarray(psf_tile_tru_pos)
#		psf_usage=np.zeros(len(psf_field_xy_pos))

		if len(psf_field_tru_pos)==0: raise ValueError("Sorry, no stars with SNR >= %i found... Try again with a lower value!" % min_snr)

		print "%i stars with a SNR >= %i were selected for the simulation" % (len(psf_field_tru_pos), min_snr)
		
		random_psf=True
	elif random_psf:
		nsub=1
		psf_field_xy_pos = []
		psf_field_tru_pos = []
		im = []
		for ix in range(3):
			for iy in range(3):
				psf_field_xy_pos.append([current_subfield,ix*s+s/2-1,iy*s+s/2-1])

		psf_field_xy_pos=np.asarray(psf_field_xy_pos)
#		psf_usage=np.zeros(len(psf_field_xy_pos))
		
	
	for iimg in range(nimg):

		gal_image = galsim.ImageF(s * n , s * n)
		trugal_image = galsim.ImageF(s * n , s * n)
		psf_image = galsim.ImageF(s * n , s * n)

		gal_image.setScale(1.0)
		trugal_image.setScale(1.0)
		psf_image.setScale(1.0)

		if not random_psf:
			# Reading the PSF with galsim :
			im = galsim.fits.read(obspsfimgfilepath(current_subfield))
			#bounds = galsim.BoundsI(1,s,1,s)
			bounds = galsim.BoundsI(0,s-1,0,s-1)
			# WARNING WARNING WARNING this is only true because we read in some GREAT3 images with those GS keywords !!!
		
			psf = galsim.InterpolatedImage(im[bounds], flux=1.0, dx=1.0, gsparams=fast_GSParams)
			
			if measurepsf:
				psfmeasures = measurestamp(psf)
	
	
	
		#print dir(psf)
		#psf._gsparams.viewvalues()
		#exit()
 
		rng = galsim.BaseDeviate()
		ud = galsim.UniformDeviate() # This gives a random float in [0, 1)

		#sig = 0.06 + 0.02*ud()

		# The database in which we save the "true" e1 and e2 in form of galaxy objects.
		galaxies = []

		print "Drawing %i galaxies for %s ..." % (n*n, simgalimgfilepath(current_subfield,iimg))
		count=0
		old=-1
		msg=""
	
		if random_psf:subfieldrange=range(current_subfield,current_subfield+nsub)
		for iy in range(n):
			if len(msg)>0: 
				msg = len(msg)*' '
				sys.stdout.write("\r%s" % msg)
			sys.stdout.write("\rProgress %i / %i" % (iy, n))
			sys.stdout.flush()
	
			for ix in range(n):
	
				if random_psf:

					# pseudo random on the the subfield in order to avoid memory issues
					current = int(count*nsub / float(n*n))+current_subfield
					if current > old: 
						msg = "Loading a new set of PSF for subfield %03i from %s..." % (current, obspsfimgfilepath(current))
						sys.stdout.write("\r%s" % msg)
						sys.stdout.flush()
						del im
						im = galsim.fits.read(obspsfimgfilepath(current))
						current_list=psf_field_xy_pos[:,0]==current
						old=current
						current_stars = psf_field_xy_pos[current_list]
						current_psf_field_tru_pos = psf_field_tru_pos[current_list]

						current_psf_tile_xy_pos=psf_tile_xy_pos[current_list]
						current_psf_tile_tru_pos=psf_tile_tru_pos[current_list]
	

					psf_id=random.randint(0,np.shape(current_stars)[0]-1)
					psf_xy=current_stars[psf_id,1:]

					#psf_usage[psf_id]+=1
					#print current,np.shape(current_stars)[0], psf_id
	
					bounds_xi = int(psf_xy[0]) - s/2+1
					bounds_xf = int(psf_xy[0]) + s/2
					bounds_yi = int(psf_xy[1]) - s/2+1
					bounds_yf = int(psf_xy[1]) + s/2
				
					bounds = galsim.BoundsI(bounds_xi,bounds_xf,bounds_yi,bounds_yf)
					psf = galsim.InterpolatedImage(im[bounds], flux=1.0, dx=1.0, gsparams=fast_GSParams)
					
					if measurepsf:
						psfmeasures = measurestamp(psf)

					
				count+=1
				# The galaxy object to store the params of the simulated galaxy :
				simgalaxy = megalut.galaxy.Galaxy()
				simgalaxy.ID = iy*n + ix + 1
			
				# We will draw this galaxy in a postage stamp :
				bounds = galsim.BoundsI(ix*s+1 , (ix+1)*s, iy*s+1 , (iy+1)*s) # Default Galsim convention, index starts at 1.
				
				gal_stamp = gal_image[bounds]
				trugal_stamp = trugal_image[bounds]
				psf_stamp = psf_image[bounds]
	

				# The drawing of the Galaxy, according to the simparams :
			
				pars = simparams.get(ix, iy, n)	
			
				gal = galsim.Sersic(n=pars["sersicn"], half_light_radius=pars["rad"], flux=pars["flux"])
				gal.applyShear(g1=pars["g1"], g2=pars["g2"]) # This is both shear AND the ellipticity of the galaxy !
		
			
				"""
				About speed :
				http://galsim-developers.github.io/GalSim/classgalsim_1_1base_1_1_sersic.html
				so if you specify trunc, better express the scale radius
				But scale radius is crazy dependent on n, so I keep half-light-radius
				"""
				
				# We apply some jitter to the position of this galaxy.
				xjitter = ud() - 0.5 # This is the minimum amount -- should we do more, as real galaxies are not that well centered in their stamps ?
				yjitter = ud() - 0.5
				gal.applyShift(xjitter,yjitter)
				
				trugal_final = gal
				trugal_final.draw(trugal_stamp)

				gal_final = galsim.Convolve([gal,psf], gsparams=fast_GSParams, real_space=False)
				psf_final = psf #galsim.Convolve([psf, pix])
	
				gal_final.draw(gal_stamp)
				psf_final.draw(psf_stamp)
	
				gal_stamp.addNoise(galsim.GaussianNoise(rng, sigma=pars["sig"]))
		
				# We save all the relevant info for this galaxy :
				simgalaxy.x = bounds.center().x - 2 + xjitter # Funny convention ... this might be wrong actually, given the bounds issue.
				simgalaxy.y = bounds.center().y - 2 + yjitter
				simgalaxy.tru_g1 = pars["g1"]
				simgalaxy.tru_g2 = pars["g2"]
				simgalaxy.tru_flux = pars["flux"]
				simgalaxy.tru_rad = pars["rad"]
				simgalaxy.tru_sersicn = pars["sersicn"]
				simgalaxy.tru_nimg = nimg # WTF ???
				simgalaxy.tru_sig = pars["sig"]
				if is_psfvar: 
					# xjitter,yjitter are in pixel !!!
					simgalaxy.x_field_true_deg=current_psf_field_tru_pos[psf_id][0]
					simgalaxy.y_field_true_deg=current_psf_field_tru_pos[psf_id][1]

					simgalaxy.x_tile_true_deg=current_psf_tile_tru_pos[psf_id][0]
					simgalaxy.y_tile_true_deg=current_psf_tile_tru_pos[psf_id][1]

					simgalaxy.x_tile_index=current_psf_tile_xy_pos[psf_id][0]
					simgalaxy.y_tile_index=current_psf_tile_xy_pos[psf_id][1]

					simgalaxy.x=current_stars[psf_id][1] + xjitter
					simgalaxy.y=current_stars[psf_id][2] + yjitter

				galaxies.append(simgalaxy)
				
				
				if measurepsf:
					simgalaxy.mes_gs_psf_flux = psfmeasures["flux"]
					simgalaxy.mes_gs_psf_sigma = psfmeasures["sigma"]
					simgalaxy.mes_gs_psf_g1 = psfmeasures["g1"]
					simgalaxy.mes_gs_psf_g2 = psfmeasures["g2"]
					simgalaxy.mes_gs_psf_x = psfmeasures["x"]
					simgalaxy.mes_gs_psf_y = psfmeasures["y"]
					simgalaxy.mes_gs_psf_rho4 = psfmeasures["rho4"]
				
				
		"""import pylab as plt
		plt.figure()
		plt.plot(np.arange(len(psf_usage)),psf_usage, 'o')
		plt.xlim([0,len(psf_usage)-1])
		plt.ylim([0,np.amax(psf_usage)*1.02])
		plt.grid()
		print psf_usage
		print 'tot', np.sum(psf_usage)
		plt.show()
		exit()"""

		print "\rDone.                        "
	
		print "Writing output FITS files ..."		

		gal_image.write(simgalimgfilepath(current_subfield,iimg))
	
		if simtrugalimgfilepath != None:
			trugal_image.write(simtrugalimgfilepath(current_subfield,iimg))
	
		if simpsfimgfilepath != None:
			psf_image.write(simpsfimgfilepath(current_subfield,iimg))
	
		endtime = datetime.now()
		print "This drawing took %s" % (str(endtime - starttime))

		#return galaxies
		megalut.utils.writepickle(galaxies, simgalfilepath(current_subfield,iimg))
	
		total_count += count
		print '%i/%i galaxies drawn.' % (total_count,n*n*nimg)


