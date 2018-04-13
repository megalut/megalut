import galsim
import numpy as np
import os
import astropy
import os
import config
import matplotlib.pyplot as plt


"""
The resulting PSF has a FWHM of about 10 pixels (measured with skycat or fv) -> 1 VIS pixel -> 0.1 arcsec
This is smaller than what can be found in Cropper 2016, but the pixel convolution is missing here!
"""


oversampling = config.psfoversampling # means that PSF will be drawn with pixels N times smaller than VIS pixels.

stamp_size = config.stampsize * oversampling

filterband_min = 550. 
filterband_max = 900.


spectrum = astropy.table.Table.read(config.spectrumpath)

# We compute some new columns:

spectrum["lam"] = spectrum["WAVELENGTH"] * 0.1 # in nm

# To weight the PSFs, we want something prop to number of photons
# The column "FLUX" is in ergs/s/cm/A
# The energy of a photon is in 1/lam
# -> We divide the flux by energy per photon

spectrum["nphot"] = spectrum["FLUX"] * spectrum["WAVELENGTH"]
spectrum["nphot"] = spectrum["nphot"] / np.max(spectrum["nphot"])

# We define the indices of the table over which we sum
mask = np.logical_and(spectrum["lam"] >= filterband_min, spectrum["lam"] <= filterband_max)
indices = np.where(mask)[0]

indices = indices[::50] # Reduce the number of indices
print "Number of indices to sum over: ", len(indices)
 

plt.plot(spectrum["lam"], spectrum["nphot"])
plt.plot(spectrum["lam"][indices], spectrum["nphot"][indices], "o")
plt.show()

images = []

for i, index in enumerate(indices):
	
	lam = spectrum["lam"][index] 
	nphot = spectrum["nphot"][index] 
	
	print index, lam, nphot
	
	psf = galsim.OpticalPSF(lam=lam,
		diam=1.2,
		obscuration=0.29,
		nstruts=6,		
		flux = 1.0
		)
		
	image = galsim.ImageF(stamp_size, stamp_size)
	psf.drawImage(image=image, scale=0.1/oversampling)
	
	image *= nphot
	
	images.append(image)

image = sum(images)

totflux = np.sum(image.array)
image /= totflux

print "Output image flux:", np.sum(image.array)


image.write(os.path.join(config.workdir, "psf.fits"))

