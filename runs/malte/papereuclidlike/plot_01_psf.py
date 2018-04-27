import megalut
import matplotlib.pyplot as plt 
import numpy as np
import config
import os
import f2n


filepath = os.path.join(config.workdir, "psf.fits")

psf = megalut.tools.io.fromfits(filepath)


print psf.shape

#plt.matshow(np.log10(psf), cmap=plt.get_cmap("gray"))
#plt.show()


myimage = f2n.fromfits(filepath)

#crop = 1
#myimage.crop(crop, -crop, crop, -crop)
    
myimage.setzscale(1.0e-5, 0.001)
myimage.makepilimage("log", negative = False)
#myimage.setzscale(-0.3, 1.0)
#myimage.makepilimage("lin", negative = False)
    
    
myimage.upsample(5)
pngimgpath = os.path.join(config.workdir, "psf.png")
myimage.tonet(pngimgpath)


