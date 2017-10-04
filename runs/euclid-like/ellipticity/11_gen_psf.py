import galsim
import pylab as plt
import numpy as np
import os
import astropy.io.fits as fits
import datetime
import os
import config

###################################################################################################
# Defining variables
# Pixel scale in arcsec / pixel
pixelscale = config.pixelscale
image_size = config.stampsize

# GalSim paramters
psf_obsc = 0.29	   # (0.35m / 1.2m) = 0.29 [D(M2) / D(M1)]
psf_nstruts = 6
psf_strut_thick = 0.015
psf_strut_angle = 105 * galsim.degrees

psf_defocus = .0
psf_astig1 = -0.07
psf_astig2 = -0.06
psf_coma1 = 0.
psf_coma2 = 0.
psf_trefoil1 = -0.02
psf_trefoil2 = +0.008

show = True
jitter = True

spectra_id = 27 # 27 = G5V

spectra_dir = "thrid_party_data"

# 'STEP_04750x09000', # Step bandpass for euclid-like; in Angstrom
filterband_min = 4750. 
filterband_max = 9000.

outdir = "psf_stamp"

###################################################################################################

if not os.path.exists(outdir):
	os.mkdir(outdir)

psf_imgi = None

spectrum = fits.getdata(os.path.join(spectra_dir, "pickles_uk_%d.fits" % spectra_id), view=np.ndarray)
spectrum = spectrum.astype([('WAVELENGTH', '>f4'), ('FLUX', '>f4')]).view('>f4').reshape(len(spectrum), -1)

ids = np.where(spectrum[:,0] >= filterband_min)[0]
ids2 = np.where(spectrum[ids,0] <= filterband_max)[0]
ids = ids[ids2][::5]

if jitter:
	ud = galsim.UniformDeviate() # This gives a random float in [0, 1)
	# We apply some jitter to the position of this psf
	xjitter = ud() - 0.5 # This is the minimum amount -- should we do more, as real stars are not that well centered in their stamps ?
	yjitter = ud() - 0.5
	xjitter *= pixelscale
	yjitter *= pixelscale

for ii, ilam in enumerate(ids):

	lam = spectrum[ilam,0] # unit: angstrom
	flux = spectrum[ilam,1] # unit: flam

	psf = galsim.OpticalPSF(
		lam=lam * 0.1, # we need nm units 
		diam=1.2,
		obscuration=psf_obsc,
		nstruts=psf_nstruts, 
		strut_thick=psf_strut_thick, 
		strut_angle=psf_strut_angle,
		defocus=psf_defocus, 
		astig1=psf_astig1, 
		astig2=psf_astig2,
		coma1=psf_coma1, 
		coma2=psf_coma2, 
		trefoil1=psf_trefoil1, 
		trefoil2=psf_trefoil2)
	
	image = galsim.ImageF(image_size, image_size)
	psf.drawImage(image=image, scale=pixelscale)
	
	if jitter:
		psf = psf.shift(xjitter,yjitter)	
		
	slicei = image.array * flux 
	if psf_imgi is None:
		psf_imgi = slicei
	else:
		psf_imgi += slicei
		
	print lam
	
psf_imgi /= np.sum(spectrum[ids,1])
	
h = fits.Header()
h['ditherx'] = xjitter
h['dithery'] = yjitter
h['PICKLES'] = "G5V"

imfn = "psf.fits"
fits.writeto(os.path.join(outdir, imfn), psf_imgi, clobber=True, header=h)

if show:
	plt.matshow(np.log10(psf_imgi), cmap=plt.get_cmap("gray"))
	plt.show()
		
