"""
Simulates a dedicated training set for each subfield.
"""

import argparse

import megalut
import megalut.meas
import config
import numpy as np
import os


import logging
logging.basicConfig(format=config.loggerformat, level=logging.INFO)
logger = logging.getLogger(__name__)

import simparams
import measfcts


def define_parser():
	"""Defines the command line arguments
	"""
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--set', required=True, help="Name of dataset to generate")
	#parser.add_argument('--nside', type=int, default=100, help='Size of stampgrid, in stamps')
	
	return parser


def run(simtype=None):
	
	logger.info("Drawing simtype {}...".format(simtype))
	
	if simtype == "train-shear":
		
		"""
		sp = simparams.G3Sersics(
			name = "ts-shear-nn-G3-snc20", # Cases have different shear, but mix galaxies. G3 as best guess.
			snc_type = 20,
			shear = 0.1,
			noise_level = 0,
			obstype = config.great3.obstype,
			distmode = "G3"
		)
		# 1000 cases with 20 snc rea
		drawconf = {
			"n":40, # Don't put this to zero, otherwise only one sersicn is used.
			"nc":1,
			"nrea":1,
			"ncat":25,
			"ncpu":25,
			"groupmode":"s"			
		}
		"""
		
		"""
		sp = simparams.G3Sersics(
			name = "ts-shear-nn-train-snc20", # Cases have different shear, but mix galaxies. G3 as useless to add others
			snc_type = 20,
			shear = 0.1,
			noise_level = 0,
			obstype = config.great3.obstype,
			distmode = "train"
		)
		# 1000 cases with 20 snc rea
		drawconf = {
			"n":40, # Don't put this to zero, otherwise only one sersicn is used.
			"nc":1,
			"nrea":1,
			"ncat":25,
			"ncpu":25,
			"groupmode":"s"			
		}
		"""
		
		sp = simparams.G3Sersics(
			name = "ts-ell-nn-train-rea20", # Ellipticity training, without noise
			snc_type = 1,
			shear = 0,
			noise_level = 0,
			obstype = config.great3.obstype,
			distmode = "train"
		)
		# 1000 cases with 20 rea
		drawconf = {
			"n":1000,
			"nc":10,
			"nrea":20,
			"ncat":1,
			"ncpu":20,
			"groupmode":"g"			
		}
		"""
		
		sp = simparams.G3Sersics(
			name = "ts-ell-n-train-rea100", # Ellipticity training, with noise
			snc_type = 1,
			shear = 0,
			noise_level = 1,
			obstype = config.great3.obstype,
			distmode = "train"
		)
		# 1000 cases with 100 rea
		drawconf = {
			"n":1000,
			"nc":10,
			"nrea":100,
			"ncat":1,
			"ncpu":20,
			"groupmode":"g"			
		}
		
		"""
		"""
		sp = simparams.G3Sersics(
			name = "ts-ell-n-train-rea500", # Ellipticity training, with noise
			snc_type = 1,
			shear = 0,
			noise_level = 1,
			obstype = config.great3.obstype,
			distmode = "train"
		)
		# 1000 cases with 500 rea
		drawconf = {
			"n":1000,
			"nc":10,
			"nrea":500,
			"ncat":1,
			"ncpu":20,
			"groupmode":"g"			
		}
		"""
		
		
		
	
	elif simtype == "valid-shear":
	
		sp = simparams.G3Sersics(
			name = "vs-shear-n-G3-snc1000",
			snc_type = 1000, # A lot, but this also covers noise and sub-pixel alignment. Hard to get more.
			shear = 0.1,
			noise_level = 1,
			obstype = config.great3.obstype,
			distmode = "G3"
		)
		# 1000 cases (different galaxies and shears), 1000 snc realizations
		drawconf = {
			"n": 20, # Don't put this to zero, otherwise only one sersicn is used.
			"nc":1,
			"nrea":1,
			"ncat":50,
			"ncpu":25,
			"groupmode":"s"				
		}
	
	
	elif simtype == "train-weight":
		
		sp = simparams.G3Sersics_statshear(
			name = "tw-200c-8000r", # Cases have different shear, but mix galaxies
			snc_type = 4,
			shear = 0.1,
			noise_level = 1,
			obstype = config.great3.obstype,
			distmode = "G3"
		)
		# 200 cases, 8000 realizations. Need to explore if less is ok as well.
		drawconf = {
			"n":2000,
			"nc":50,
			"nrea":1,
			"ncat":200,
			"ncpu":25,
			"groupmode":"s"				
		}
	
	elif simtype == "valid-overall":

		sp = simparams.G3Sersics_statshear(
			name = "vo-200c-8000r", # For overall validation, we almost mimick a full GREAT3 branch
			snc_type = 4,
			shear = 0.1,
			noise_level = 1,
			obstype = config.great3.obstype,
			distmode = "G3"
		)
		# 200 cases, 8000 realizations.
		drawconf = {
			"n":2000,
			"nc":50,
			"nrea":1,
			"ncat":200,
			"ncpu":25,
			"groupmode":"s"				
		}


	elif simtype == "simobscompa":

		sp = simparams.G3Sersics_statshear(
			name = "simobscompa-G3", # Drawing a few galaxies to compare their feature distribs with those of the "observations"
			snc_type = 1,
			shear = 0.0, # Would be OK to put a little shear, in fact, as the observations have some.
			noise_level = 1,
			obstype = config.great3.obstype,
			distmode = "G3"
		)
		# 1000 galaxies, single realization
		drawconf = {
			"n":100,
			"nc":5,  # To get a good samplign of sersicn (n / nc)
			"nrea":1,
			"ncat":10,
			"ncpu":10,
			"groupmode":None
		}
		
	else:
		raise RuntimeError("Unknown simtype, see code for defined names.")
	
	
	for subfield in config.great3.subfields:
		runsub(subfield, sp, drawconf)


def runsub(subfield, sp, drawconf):
	
	
	# We have to read in the obs catalog of this subfield to get the noise of the sky:
	if sp.noise_level != 0:
		obscat = megalut.tools.io.readpickle(config.great3.subpath(subfield, "obs", "img_meascat.pkl"))
		sp.noise_level = np.ma.mean(obscat["skymad"])
		logger.info("Noise level set to {}".format(sp.noise_level))
	
	# Getting the path to the correct directories
	simdir = config.great3.subpath(subfield, "sim")
	measdir = config.great3.subpath(subfield, "simmeas")
	
	# Loading the PSF for the subfield
	psfcat = megalut.tools.io.readpickle(config.great3.subpath(subfield, "obs", "star_meascat.pkl"))
	
	
	# Simulating images
	megalut.sim.run.multi(
		simdir=simdir,
		simparams=sp,
		drawcatkwargs={"n":drawconf["n"], "nc":drawconf["nc"], "stampsize":config.great3.stampsize()},
		drawimgkwargs={}, 
		psfcat=psfcat, psfselect="random",
		ncat=drawconf["ncat"], nrea=drawconf["nrea"], ncpu=drawconf["ncpu"],
		savepsfimg=False, savetrugalimg=False
	)


	# Measuring the newly drawn images
	megalut.meas.run.onsims(
		simdir=simdir,
		simparams=sp,
		measdir=measdir,
		measfct=measfcts.gal,
		measfctkwargs={"branch":config.great3},
		ncpu=drawconf["ncpu"],
		skipdone=config.great3.skipdone
	)
	

	cat = megalut.meas.avg.onsims(
		measdir=measdir, 
		simparams=sp,
		task="group",
		groupcols=measfcts.groupcols, 
		removecols=measfcts.removecols
	)

	megalut.tools.table.keepunique(cat)
	megalut.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl"))
	
	#cat = megalut.tools.io.readpickle(os.path.join(measdir, sp.name, "groupmeascat.pkl"))
	#print megalut.tools.table.info(cat)
	#exit()

	# For shear sims, we group the results in cases of same true shears
	if drawconf["groupmode"] == "s":
			
		cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])
		megalut.tools.table.keepunique(cat)
		
	if drawconf["groupmode"] in ["s", "g"]:
	
		# For each case, we add the fraction of failed measurements
		nrea = cat["adamom_g1"].shape[1]
		logger.info("We have {} realizations".format(nrea))
		cat["adamom_failfrac"] = np.sum(cat["adamom_g1"].mask, axis=1) / float(nrea)
		#print cat["adamom_failfrac"]

		#print megalut.tools.table.info(cat)
		megalut.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl")) # Just overwrite, don't need the other one

	
	
	
	
	"""
	# For statell sims, we group by ellipticity
	if "statell" in sp.name:
		
		cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_g1", "tru_g2"])
		megalut.tools.table.keepunique(cat)
		#print megalut.tools.table.info(cat)
		megalut.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl")) # Just overwrite, don't need the other one
	"""
	


if __name__ == '__main__':

	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('simtype', help='Type of dataset to simulate')
	args = parser.parse_args()
	#print args
	#exit()
	
	run(simtype=args.simtype)

