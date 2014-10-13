"""
load fits images, get stamps...

"""

import os
import galsim

import numpy as np
import logging
logger = logging.getLogger(__name__)


def loadimg(imgfilepath):
    """
    Uses GalSim to load and image from a FITS file, enforcing that the GalSim origin is (0, 0).
    
    :param imgfilepath: path to FITS image
    :returns: galsim image
    """
    
    logger.info("Loading FITS image %s..." % (os.path.basename(imgfilepath)))
    img = galsim.fits.read(imgfilepath)
    img.setOrigin(0,0)
    logger.info("Done with loading %s, shape is %s" % (os.path.basename(imgfilepath), img.array.shape))
    
    logger.warning("The origin and stampsize conventions are new and should be tested !")
    
    img.origimgfilepath = imgfilepath # Just to keep this somewhere
    
    return img

def getstamp(x, y, img, stampsize, getfrom=None):
    """
    I prepare a image stamp "centered" at position (x, y) of your input image.
    You can use the array attribute of the stamp if you want to get the actual pixels.
    
    :param x: x position of the stamp "center" (i.e., the object), in pixels.
    :param y: 
    :param img: input numpy or galsim image. Automatically type detection.
    :param stampsize: width = height of the stamp, in pixels. Has to be even. 
    :param getfrom: force the detection "gs" for galsim and "np" for numpy.
    
    :returns: a tuple(stamp, flag). Flag is 1 if the stamp could not be extracted, 0 otherwise.
    """
    if getfrom==None:
        if type(img)==galsim.image.Image:
            logger.debug("Found image type galsim")
            getfrom="gs"
        elif type(img)==np.ndarray:
            logger.debug("Found image type numpy")
            getfrom="np"
        else:
            raise TypeError("Image type not understood.")
    else:
        logger.debug("getfrom is forced to %s" % getfrom)
        
    try:
        assert int(stampsize)%2 == 0 # checking that it's even
    except:
        raise AssertionError("stampsize must be even")
    
    error=False
    
    # If the stamp is from galsim:
    if getfrom=="gs":
        assert img.origin().x == 0 and img.origin().y == 0
        assert img.xmin == 0 and img.ymin == 0
        
        xmin = int(np.round(x - 0.5)) - int(stampsize)/2
        xmax = int(np.round(x - 0.5)) + int(stampsize)/2 - 1
        ymin = int(np.round(y - 0.5)) - int(stampsize)/2
        ymax = int(np.round(y - 0.5)) + int(stampsize)/2 - 1
                
        assert ymax - ymin == stampsize - 1 # This is the GalSim convention, both extermas are "included" in the bounds.
        assert xmax - xmin == stampsize - 1
        
        # We check that these bounds are fully within the image
        if xmin < img.getXMin() or xmax > img.getXMax() or ymin < img.getYMin() or ymax > img.getYMax():
            error=True
        else:            
            # We prepare the stamp
            bounds = galsim.BoundsI(xmin, xmax, ymin, ymax)
            stamp = img[bounds] # galaxy postage stamp
            assert stamp.array.shape == (stampsize, stampsize)
    # if from numpy:
    elif getfrom=="np":
        # By MegaLUT's definition, a pixel is centered at 0.5,0.5
        dd=+.5
        xmin=int(round(x-dd-stampsize/2.))
        xmax=int(round(x-dd+stampsize/2.))
        ymin=int(round(y-dd-stampsize/2.))
        ymax=int(round(y-dd+stampsize/2.))
        
        # We check that these bounds are fully within the image
        if xmin < 0 or xmax > np.shape(img)[0] or ymin < 0 or ymax > np.shape(img)[1]:
            error=True
        else:
            # We prepare the stamp
            stamp=img[xmin:xmax,ymin:ymax]
            assert np.shape(stamp) == (stampsize, stampsize)
        
    if error:
        return (None, 1)
    else: 
        return (stamp, 0)