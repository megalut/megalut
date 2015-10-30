import megalut.sbe
import mymeasfct
import mysimparams_v5 as mysimparams
import mymlparams_v5 as mymlparams
import myplots_v5 as myplots

import logging
import subprocess
import glob
import os
import shutil

logger = logging.getLogger(__name__)


def analyse(run):
	"""
	
	"""

	# Making sure that there are no old shear measurements lying around in the datadir:
	oldstuff = glob.glob(os.path.join(run.sbedatadir, "*shear_measurements.fits"))
	oldstuff.extend(glob.glob(os.path.join(run.sbedatadir, "*/*shear_measurements.fits")))
	oldstuff.extend(glob.glob(os.path.join(run.sbedatadir, "bias_measurements.*")))
	if len(oldstuff) != 0:
		print oldstuff
		raise RuntimeError("Clean {} first!".format(run.sbedatadir))

	# Makign a symlink of the FITS results file into the data directory:
	os.symlink(os.path.join(run.workmldir, "obsprecat.fits"), os.path.join(run.sbedatadir, "MegaLUT_shear_measurements.fits"))

	# Running Bryan's stuff:
	logger.info("Starting Bryan's script...")
	subprocess.call(["python", "/users/mtewes/Euclid/sbe/Example_SBE_code-svn/trunk/process_results.py", run.sbedatadir])

	# Copying the output:
	shutil.copy(os.path.join(run.sbedatadir, "bias_measurements.txt"), run.workmldir)
	shutil.copy(os.path.join(run.sbedatadir, "bias_measurements.fits"), run.workmldir)
	logger.info("Copy of results into the workmldir '{}' done.".format(run.workmldir))
	
	# Cleaning the data directory
	os.remove(os.path.join(run.sbedatadir, "MegaLUT_shear_measurements.fits"))
	os.remove(os.path.join(run.sbedatadir, "bias_measurements.fits"))
	os.remove(os.path.join(run.sbedatadir, "bias_measurements.txt"))
	
