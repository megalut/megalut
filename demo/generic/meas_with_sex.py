"""
Standalone demo illustrating the use of the sextractor wrapper.
"""
import logging
logging.basicConfig(level=logging.INFO)

from megalut.meas.sextractor import SExtractor



se = SExtractor()

#print se.get_version()

cat = se.run("simgalimg.fits")

print cat


