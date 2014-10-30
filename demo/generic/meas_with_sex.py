"""
Standalone demo illustrating the use of the sextractor wrapper

THIS IS OUTDATED, the SExctractor wrapper is now outsourced to sewpy
"""
import logging
logging.basicConfig(level=logging.INFO)

import megalut
from megalut.meas.sextractor import SExtractor



# Minimal example

"""
se = SExtractor()

# Any FITS image would be fine for this minimal example, let's use this one:
out = se.run("psfs/psfgrid.fits")

print out["table"]

"""



# An example with some custom configuration

"""

params = ["X_IMAGE", "Y_IMAGE", "FWHM_IMAGE", "BACKGROUND", "FLUX_RADIUS(3)", "FLAGS"]
# Note that if you give an unknown param, I will run anyway, but you will get a nice 
# warning with a list of all common params.

config = {"BACK_TYPE":"MANUAL", "BACK_VALUE":0.0, "PHOT_FLUXFRAC":"0.3, 0.5, 0.8"}

se = SExtractor(params=params, config=config, workdir="test")
#print se.get_version()

out = se.run("psfs/psfgrid.fits")

print out["table"]
"""


# An example using ASSOC

# For this we need an existing catalog and a FITS image.

inputcat = megalut.tools.io.readpickle("psfs/cat_psfgrid.pkl")
print inputcat[:5]

params = ["VECTOR_ASSOC(3)", "X_IMAGE", "Y_IMAGE", "FWHM_IMAGE", "BACKGROUND", "FLAGS"]
config = {"BACK_TYPE":"MANUAL", "BACK_VALUE":0.0, "DETECT_MINAREA":10}
se = SExtractor(params=params, config=config, workdir="test")

out = se.run("psfs/psfgrid.fits", assoc_cat = inputcat, assoc_xname="psfgridx", assoc_yname="psfgridy")


print out["table"][:5]


