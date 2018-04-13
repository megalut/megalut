import galsim
import numpy as np
import os
import astropy
import os
import config
import matplotlib.pyplot as plt



oversampling = 1 # means that PSF will be drawn with pixels N times smaller than VIS pixels.

stamp_size = 64 * oversampling

	
psf = galsim.OpticalPSF(lam=800.0,
	diam=1.2,
	obscuration=0.29,
	nstruts=6,		
	flux = 1.0
	)
		
image = galsim.ImageF(stamp_size, stamp_size)
psf.drawImage(image=image, scale=0.1/oversampling)


print "Output image flux:", np.sum(image.array)


image.write(os.path.join(config.workdir, "psf_800.fits"))

