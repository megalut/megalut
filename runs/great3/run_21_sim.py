"""
Simulates a dedicated training or validation set for each subfield.
This scirpt takes an argument, run it with -h to get help.
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



def run(simtype=None):
	
	simname = config.datasets[simtype]
	
	logger.info("Drawing simtype {} => {}...".format(simtype, simname))
	
	
	############## First, the fiducial sets, as small and fast as possible, to give a baseline.
	
	if simname == "ts-ell-nn-train-rea10":
		
		# The fiducial train-shear: **** ellipticity training, without noise **** (yes, that's a big compromise, for GREAT3).
		# The "nn" stands for "no noise"
		sp = simparams.G3Sersics(
			name = simname,
			snc_type = 1,
			shear = 0,
			noise_level = 0,
			obstype = config.great3.obstype,
			distmode = "train"
		)
		# 1000 cases with 10 rea
		drawconf = {
			"n":1000,
			"nc":10,
			"nrea":10,
			"ncat":1,
			"ncpu":10,
			"groupmode":"g"			
		}

	elif simname == "vs-shear-n-G3-snc1000":
	
		# The fiducial valid-shear. Heavy !
		sp = simparams.G3Sersics(
			name = simname,
			snc_type = 1000, # A lot, but this also covers noise and sub-pixel alignment. Hard to get more.
			shear = 0.1,
			noise_level = 1,
			obstype = config.great3.obstype,
			distmode = "G3"
		)
		# 1000 cases (different galaxies and shears), 1000 snc realizations
		drawconf = {
			"n": 20, # Don't put this to one, otherwise only one sersicn is used...
			"nc":1,
			"nrea":1,
			"ncat":50,
			"ncpu":25,
			"groupmode":"s"				
		}
	
	
	elif simname == "tw-200c-1000r":
	
		# The ficducial train-weight. Heavy, but can't make this smaller. Cases have different shear, but mix galaxies
		sp = simparams.G3Sersics_statshear(
			name = simname,
			snc_type = 4,
			shear = 0.1,
			noise_level = 1,
			obstype = config.great3.obstype,
			distmode = "G3"
		)
		# 200 cases, 1000 realizations with small snc
		drawconf = {
			"n":250,
			"nc":10,
			"nrea":1,
			"ncat":200,
			"ncpu":10,
			"groupmode":"s"				
		}

	
	elif simname == "vo-200c-8000r":

		# For overall validation, we almost mimick a full GREAT3 branch, huge!
		sp = simparams.G3Sersics_statshear(
			name = simname,
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


	elif simname == "simobscompa-G3":

		# Drawing 10'000 galaxies to compare their feature distribs with those of the "observations". Just for plots and tests.
		sp = simparams.G3Sersics_statshear(
			name = simname,
			snc_type = 1,
			shear = 0.0, # Would be OK to put a little shear, in fact, as the observations have some.
			noise_level = 1,
			obstype = config.great3.obstype,
			distmode = "G3"
		)
		# 10'000 galaxies, single realization
		drawconf = {
			"n":1000,
			"nc":5,  # To get a good samplign of sersicn (n / nc)
			"nrea":1,
			"ncat":10,
			"ncpu":10,
			"groupmode":None
		}

	elif simname == "simobscompa-train":
		
		# As above, but with "train" distributions (instead of G3). Just for plots and tests.
		sp = simparams.G3Sersics_statshear(
			name = simname,
			snc_type = 1,
			shear = 0.0, # Would be OK to put a little shear, in fact, as the observations have some.
			noise_level = 1,
			obstype = config.great3.obstype,
			distmode = "train"
		)
		# 10'000 galaxies, single realization
		drawconf = {
			"n":1000,
			"nc":5,  # To get a good samplign of sersicn (n / nc)
			"nrea":1,
			"ncat":10,
			"ncpu":10,
			"groupmode":None
		}

	########### Mimicing GREAT3 subfields

	elif simname == "sersicG3subfield":
		
		# We mimic a GREAT3 subfield. Single static shear, 10'000 gals, with SNC 2
		# Run this for every "subfield".
		sp = simparams.G3Sersics_statshear(
			name = simname,
			snc_type = 2,
			shear = 0.05,
			noise_level = 1,
			obstype = config.great3.obstype,
			distmode = "G3"
		)
		# 10'000 galaxies, single realization
		drawconf = {
			"n":5000, # 2x, with SNC
			"nc":50,  # To get a good samplign of sersicn (n / nc)
			"nrea":1,
			"ncat":1, # To get a single shear value
			"ncpu":1,
			"groupmode":None
		}

	elif simname == "sersicG3subfield_nosnc":
		
		# Idem, but without SNC, to check for differences
		sp = simparams.G3Sersics_statshear(
			name = simname,
			snc_type = 1,
			shear = 0.05,
			noise_level = 1,
			obstype = config.great3.obstype,
			distmode = "G3"
		)
		# 10'000 galaxies, single realization
		drawconf = {
			"n":10000,
			"nc":100,  # To get a good samplign of sersicn (n / nc)
			"nrea":1,
			"ncat":1, # To get a single shear value
			"ncpu":1,
			"groupmode":None
		}
	
	########## Now, some alternative datasets, to test out other approaches.
	
	elif simname == "ts-shear-nn-train-snc20":
		
		# For train-shear
		# Really train for shear, not for ellipticity. Still without noise here.
		# A bit close to what you ideally want to do.
		# Cases have different shear and different galaxies (one per case). Train distribs.
		sp = simparams.G3Sersics(
			name = simname,
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

	
	elif simname == "ts-ell-n-train-rea100":		
		
		# Something we can afford, with noise, to see if noise-bias gets reduced: 
		sp = simparams.G3Sersics(
			name = simname,
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
	
	
	elif simname == "tw-100c-10000r":
		
		# A huge weight training set
		# Cases have different shear, but mix galaxies
		# Experimenting with much more realizations, to see if bias on vo persists...
		# Seems to work, but expensive, and overall improvement is not interesting for GREAT3.
		
		sp = simparams.G3Sersics_statshear(
			name = simname,
			snc_type = 4,
			shear = 0.1,
			noise_level = 1,
			obstype = config.great3.obstype,
			distmode = "G3"
		)
		# 100 cases, 10000 realizations with small snc
		drawconf = {
			"n":2500,
			"nc":50,
			"nrea":1,
			"ncat":100,
			"ncpu":10,
			"groupmode":"s"				
		}
		
		
	else:
		raise RuntimeError("Unknown simname, see code for defined names.")

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

	possible_simtypes = ["train-shear", "valid-shear", "train-weight", "valid-overall", "simobscompa", "mimic-great3"]

	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('simtype', help='Type of dataset to simulate, must be in {}'.format(possible_simtypes))
	args = parser.parse_args()
	
	if args.simtype not in possible_simtypes:
		raise RuntimeError("Unknown simtype, must be in {}".format(possible_simtypes))
	
	run(simtype=args.simtype)

