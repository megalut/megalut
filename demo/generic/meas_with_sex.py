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



params = ["X_IMAGE", "Y_IMAGE", "FWHM_IMAGE", "BACKGROUND", "FLUX_RADIUS(3)", "FLAGS"]
# Note that if you give an unknown param, I will run anyway, but you will get a nice 
# warning with a list of all common params.

config = {"BACK_TYPE":"MANUAL", "BACK_VALUE":0.0, "PHOT_FLUXFRAC":"0.3, 0.5, 0.8"}

se = SExtractor(params=params, config=config, workdir="test")
#print se.get_version()

cat = se.run("psfs/psfgrid.fits")

print cat

