import matplotlib
matplotlib.use("AGG")

import os
import megalut
import config
import argparse

import simparams
import measfcts
import numpy as np

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def define_parser():
	"""Defines the command line arguments
	"""
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('code', type=str, help='what dataset should be simulated?')
	
	return parser


def configure(args):
	"""Configures settings for the different datasets
	"""
	
	code = args.code
	
	if code == "si-1": # Just to quickly draw 1000 galaxies probing the distributions.
		sp = simparams.Fiducial(
			name = code,
			snc_type = 0,
			shear = 0,
			noise_level = 1.0
		)
		drawconf = {
			"n":1000,
			"nc":10,
			"nrea":1,
			"ncat":1,
			"ncpu":1,
			"groupmode":None,
			"skipdone":False	
		}
	
	elif code == "vo-1": # As a first test, no SNC: 100 cases with 10'000 gals (1 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":10000,
			"nc":100,
			"nrea":1,
			"ncat":100,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "vo-2": # With 2-fold SNC, 1000 cases, 10'000 gals (20 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 2,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":10000,
			"nc":100,
			"nrea":1,
			"ncat":1000,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "vo-3-faint": # Intermediate size, with 2-fold SNC, 200 cases, 10'000 gals (4 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 2,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0
		)
		drawconf = {
			"n":10000,
			"nc":100,
			"nrea":1,
			"ncat":200,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "vo-3-faint-nosnc": # No SNC, 200 cases, 50'000 gals (20 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0
		)
		drawconf = {
			"n":50000,
			"nc":100,
			"nrea":1,
			"ncat":200,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}
	
	elif code == "ts-1": # 500 cases, 500-SNC rotations per case (0.25 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 500,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":500,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}


	elif code == "ts-2": # 2000 cases, 2000-SNC rotations per case (4 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 2000,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":2000,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "ts-2-minrad3": # Same as ts-2, but with tru_rad 3 to 8 instead of 2 to 8
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 2000,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_rad = 3.0
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":2000,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "ts-2-easy": # Same as ts-2, but with tru_rad 3 to 8 instead of 2 to 8
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 2000,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_rad = 4.0,
			min_tru_sb = 7.5,
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":2000,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "ts-2-faint": # Similar to ts-2, but with all the space, for later SNR selection (8 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 2000,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0,
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":4000,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "ts-2-faint-ln": # 0.8 M, just with lower noise (again for later selection, which will take much smaller galaxies)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 200,
			shear = 0.1,
			noise_level = 0.1,
			min_tru_sb = 1.0,
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":4000,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}


	elif code == "ts-3-ln": # 10 times smaller then ts-2, but with 10 times lower noise
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 200,
			shear = 0.1,
			noise_level = 0.1,
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":2000,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "ts-3-faint-ln": # 10 times smaller then ts-2, but with 10 times lower noise
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 200,
			shear = 0.1,
			noise_level = 0.1,
			min_tru_sb = 1.0
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":2000,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}


	elif code == "ts-e-1": # Target value is ellipticity, full noise, 100 rea per gal, (1 M)
		sp = simparams.Fiducial(
			name = code,
			snc_type = 0,
			shear = -1, # We don't want shear in this
			noise_level = 1.0
		)
		drawconf = {
			"n":10000,
			"nc":100,
			"nrea":100,
			"ncat":1,
			"ncpu":20,
			"groupmode":"ellipticity",
			"skipdone":False	
		}


	elif code == "vs-1-faint": # Small, to test SNR and failfrac in the full parameter space
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 2000,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":1000,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}


	elif code == "vs-1": # Same settings as ts-1, just another realization of the set.
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 500,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":500,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}
	
	
	elif code == "vs-2": # 1000 cases, 10'000 SNC rotations each (10 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 10000,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":1000,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "vs-2-easy": # 1000 cases, 10'000 SNC rotations each (10 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 10000,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_rad = 4.0,
			min_tru_sb = 7.5,

		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":1000,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}



	elif code == "vs-3-faint": # 5000 cases, 10'000 SNC rotations each (50 M) HUGE, same as Thibault's set.
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 10000,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0,
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":5000,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}


	
	elif code == "vs-3": # 50 M down to S = 1.
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 10000,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":5000,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}
	
	
	elif code == "tw-1": # Training weights, no SNC (!), 500 cases, 2000 gals (1 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":2000,
			"nc":50,
			"nrea":1,
			"ncat":500,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}


	elif code == "tw-2": # Thibaults set size, 100 cases, 100'000 gals (no SNC) (10 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":100000,
			"nc":1000,
			"nrea":1,
			"ncat":100,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "tw-3-faint": # Intermediate size, 100 cases, 10'000 gals (no SNC) (1 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0
		)
		drawconf = {
			"n":10000,
			"nc":1000,
			"nrea":1,
			"ncat":100,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}
	elif code == "tw-4-faint": # Intermediate size, 500 cases, 10'000 gals (no SNC) (5 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0
		)
		drawconf = {
			"n":10000,
			"nc":1000,
			"nrea":1,
			"ncat":500,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}
	elif code == "tw-4-faint-snc": # Intermediate size, 100 cases, 4'000 gals (with 4-fold SNC) (0.4 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 4,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0
		)
		drawconf = {
			"n":1000,
			"nc":100,
			"nrea":1,
			"ncat":100,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "tw-5-faint": # Huge size, 200 cases, 100'000 gals (no SNC) (20 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0
		)
		drawconf = {
			"n":100000,
			"nc":1000,
			"nrea":1,
			"ncat":200,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}
	
	else:
		
		logger.info("Unknown code")
		return
		
	
	return (sp, drawconf)








def run(configuration):
	"""Draws the simulations and measures them
	"""
	sp, drawconf = configuration
	
	simdir = config.simdir
	measdir = config.simmeasdir


	# Simulating images
	megalut.sim.run.multi(
		simdir=simdir,
		simparams=sp,
		drawcatkwargs={"n":drawconf["n"], "nc":drawconf["nc"], "stampsize":config.drawstampsize},
		drawimgkwargs={}, 
		psfcat=None, psfselect="random",
		ncat=drawconf["ncat"], nrea=drawconf["nrea"], ncpu=drawconf["ncpu"],
		savepsfimg=False, savetrugalimg=False
	)


	# Measuring the newly drawn images
	megalut.meas.run.onsims(
		simdir=simdir,
		simparams=sp,
		measdir=measdir,
		measfct=measfcts.default,
		measfctkwargs={"stampsize":config.stampsize},
		ncpu=drawconf["ncpu"],
		skipdone=drawconf["skipdone"]
	)
	

	cat = megalut.meas.avg.onsims(
		measdir=measdir, 
		simparams=sp,
		task="group",
		groupcols=measfcts.default_groupcols, 
		removecols=measfcts.default_removecols
	)

	megalut.tools.table.keepunique(cat)
	megalut.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl"))
	
	
	# Now we perform some additional computations on this catalog.
	cat = megalut.tools.io.readpickle(os.path.join(measdir, sp.name, "groupmeascat.pkl"))
	
	if drawconf["groupmode"] == "shear":
	
		#cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])
		cat = megalut.tools.table.fastgroupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])	
	
		megalut.tools.table.keepunique(cat)
	
	if drawconf["groupmode"] in ["shear", "ellipticity"]:
	
		# For each case, we add the fraction of failed measurements
		nrea = cat["adamom_g1"].shape[1]
		logger.info("We have {} realizations".format(nrea))
		cat["adamom_failfrac"] = np.sum(cat["adamom_g1"].mask, axis=1) / float(nrea)		
	
		#print megalut.tools.table.info(cat)
		megalut.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl"))



if __name__ == '__main__':
	parser = define_parser()
	args = parser.parse_args()
	status = run(configure(args))
	exit(status)

