"""
Standalone demo illustrating the use of the sextractor wrapper.
"""
import logging
logging.basicConfig(level=logging.INFO)

from megalut.meas.sextractor import SExtractor



se = SExtractor()

#print se.get_version()

# Any FITS image would be fine for this minimal example, let's use this one:
cat = se.run("psfs/psfgrid.fits")

print cat


