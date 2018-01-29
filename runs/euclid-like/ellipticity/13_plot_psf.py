import megalut
import matplotlib.pyplot as plt 
import numpy as np
import subprocess
import os
import f2n

filepath = "psf_stamp/psf.fits"

psf = megalut.tools.io.fromfits(filepath)

print psf

psf = psf[9:-9,9:-9]

print psf.shape

plt.matshow(np.log10(psf), cmap=plt.get_cmap("gray"))

myimage = f2n.fromfits(filepath)
crop = 12
myimage.crop(crop, -crop, crop, -crop)
    
myimage.setzscale(0.0, 0.07)
myimage.makepilimage("log", negative = False)
#myimage.setzscale(-0.3, 1.0)
#myimage.makepilimage("lin", negative = False)
    
    
myimage.upsample(10)
pngimgpath = os.path.join("psf.png")
myimage.tonet(pngimgpath)

plt.show()