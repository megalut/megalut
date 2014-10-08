"""
A demo that runs on the CGV branch (fields 005-9)

.. note:: this demo is valid for branches C**, R**.
"""

import megalut.great3
import megalut.meas

# Optional: set the logging level. If omited, only warnings (and worse) will be shown.
import logging
logging.basicConfig(level=logging.INFO)

# Create an instance of the GREAT3 class
cgv=megalut.great3.great3.Run("control", "ground", "variable",
	datadir="/home/kuntzer/workspace/MegaLUT/great3_data_part",
	subfields=range(5,10))

# Now run the measurements on input images
cgv.meas("obs")

exit()

# First, we create a Branch object:
branch = megalut.great3.utils.Branch("control", "ground", "variable",
	datadir="/home/kuntzer/workspace/MegaLUT/great3_data_part")

# Then, get the input catalog, that will be served as an astropy table.
subfield=5
input_cat = megalut.great3.io.readgalcat(branch, subfield)

# Measure the features on the input image.
img = megalut.gsutils.loadimg(branch.galimgfilepath(subfield))
meas_cat = megalut.meas.galsim_adamom.measure(img, input_cat, stampsize=branch.stampsize())

# Save the measured catalog