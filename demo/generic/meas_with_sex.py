"""
Standalone demo illustrating the use of the sextractor wrapper.
"""
import logging
logging.basicConfig(level=logging.DEBUG)

from megalut.meas.sextractor import SExtractor



# Minimal example :

"""
se = SExtractor()

# Any FITS image would be fine for this minimal example, let's use this one:
cat = se.run("psfs/psfgrid.fits")

print cat
"""



# An example with some custom configuration :


params = ["X_IMAGE", "Y_IMAGE", "FWHM_IMAGE", "FLUX_AUTO", "BACKGROUND", "FLAGS"]
# Note that if you give an unknown param, I will run anyway, but you will get a nice 
# warning with a list of all common params.

config = {"BACK_TYPE":"MANUAL", "BACK_VALUE":0.0}

se = SExtractor(params=params, config=config, workdir = "test")
#print se.get_version()

cat = se.run("psfs/psfgrid.fits")

print cat



