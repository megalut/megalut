import f2n
import numpy as np
import os

import logging

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s',level=logging.INFO)





fitsimgpath = "/vol/fohlen11/fohlen11_1/mtewes/snr_fig/v1/img.fits"

pngimgpath = fitsimgpath + ".png"

myimage = f2n.fromfits(fitsimgpath)
myimage.setzscale(-2.0, 10.0)
myimage.makepilimage("lin", negative = False)
	
	
myimage.upsample(5)
myimage.tonet(pngimgpath)



