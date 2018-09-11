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
	
	if code == "si-1": # Just to quickly draw 10'000 galaxies probing the distributions.
		sp = simparams.FromCat(
			name = code,
			snc_type = 0,
			shear = 0
		)
		drawconf = {
			"n":500,
			"nc":100,
			"nrea":1,
			"ncat":20,
			"ncpu":20,
			"groupmode":None,
			"skipdone":False	
		}

	elif code == "si-1-uni": # Uniform distributions for the point estimator training.
		sp = simparams.FromCat(
			name = code,
			snc_type = 0,
			shear = 0,
			dist_type="uni"
		)
		drawconf = {
			"n":500,
			"nc":100,
			"nrea":1,
			"ncat":20,
			"ncpu":20,
			"groupmode":None,
			"skipdone":False	
		}

	elif code == "si-1-uni2": # Uniform distributions for the point estimator training.
		sp = simparams.FromCat(
			name = code,
			snc_type = 0,
			shear = 0,
			dist_type="uni2"
		)
		drawconf = {
			"n":500,
			"nc":100,
			"nrea":1,
			"ncat":20,
			"ncpu":20,
			"groupmode":None,
			"skipdone":False	
		}

	elif code == "si-1-uni2-etype2": # Uniform distributions for the point estimator training.
		sp = simparams.FromCat(
			name = code,
			snc_type = 0,
			shear = 0,
			dist_type="uni2",
			e_type = 2
		)
		drawconf = {
			"n":10000,
			"nc":100,
			"nrea":1,
			"ncat":1,
			"ncpu":1,
			"groupmode":None,
			"skipdone":False	
		}

	elif code == "si-1-cat-etype2": # Uniform distributions for the point estimator training.
		sp = simparams.FromCat(
			name = code,
			snc_type = 0,
			shear = 0,
			dist_type="cat",
			e_type = 2
		)
		drawconf = {
			"n":10000,
			"nc":100,
			"nrea":1,
			"ncat":1,
			"ncpu":1,
			"groupmode":None,
			"skipdone":False	
		}
	elif code == "si-1-cat-etype2-emaxamp7": # Uniform distributions for the point estimator training.
		sp = simparams.FromCat(
			name = code,
			snc_type = 0,
			shear = 0,
			dist_type="cat",
			e_type = 2,
			e_maxamp = 0.7
		)
		drawconf = {
			"n":10000,
			"nc":100,
			"nrea":1,
			"ncat":1,
			"ncpu":1,
			"groupmode":None,
			"skipdone":False	
		}


	elif code == "tp-1": # (8 M)
		sp = simparams.FromCat_statshear(
			name = code,
			snc_type = 2000,
			shear = 0.1,
			dist_type="uni"
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":4000,
			"ncpu":40,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "tp-1-uni2": # (8 M)
		sp = simparams.FromCat_statshear(
			name = code,
			snc_type = 2000,
			shear = 0.1,
			dist_type="uni2"
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":4000,
			"ncpu":40,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "tp-1-uni2-etype2": # (8 M)
		sp = simparams.FromCat_statshear(
			name = code,
			snc_type = 2000,
			shear = 0.1,
			dist_type="uni2",
			e_type = 2
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":4000,
			"ncpu":40,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "tp-1-e-uni2": # (1 M)
		sp = simparams.FromCat(
			name = code,
			snc_type = 0,
			shear = -1, # no shear
			dist_type="uni2"
		)
		drawconf = {
			"n":5000,
			"nc":100,
			"nrea":200,
			"ncat":1,
			"ncpu":100,
			"groupmode":"ellipticity",
			"skipdone":False	
		}

	elif code == "tp-1-e-ln-uni2-etype2": # (0.5 M)
		sp = simparams.FromCat(
			name = code,
			snc_type = 0,
			shear = -1, # no shear
			dist_type="uni2",
			e_type=2,
			noise_level = 0.1,
		)
		drawconf = {
			"n":5000,
			"nc":100,
			"nrea":100,
			"ncat":1,
			"ncpu":25,
			"groupmode":"ellipticity",
			"skipdone":False	
		}


	elif code == "tp-1-e-uni2-etype2": # (1 M)
		sp = simparams.FromCat(
			name = code,
			snc_type = 0,
			shear = -1, # no shear
			dist_type="uni2",
			e_type=2,
		)
		drawconf = {
			"n":5000,
			"nc":100,
			"nrea":200,
			"ncat":1,
			"ncpu":25,
			"groupmode":"ellipticity",
			"skipdone":False	
		}



	elif code == "tp-1-e": # ellipticity pre-training (1M)
		sp = simparams.FromCat(
			name = code,
			snc_type = 0,
			shear = -1, # no shear
			dist_type="uni"
		)
		drawconf = {
			"n":10000,
			"nc":100,
			"nrea":100,
			"ncat":1,
			"ncpu":100,
			"groupmode":"ellipticity",
			"skipdone":False	
		}

	elif code == "tp-1-ln": # (0.8 M)
		sp = simparams.FromCat_statshear(
			name = code,
			snc_type = 200,
			shear = 0.1,
			noise_level = 0.1,
			dist_type="uni"
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

	elif code == "vp-1": # (40 M, huge!)
		sp = simparams.FromCat_statshear(
			name = code,
			snc_type = 10000,
			shear = 0.1,
			dist_type="uni"
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":4000,
			"ncpu":40,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "vp-1-uni2": # (40 M, huge!)
		sp = simparams.FromCat_statshear(
			name = code,
			snc_type = 10000,
			shear = 0.1,
			dist_type="uni2"
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":4000,
			"ncpu":40,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "vp-2": # (8 M) same as tp-1, but for "cat" distributions, to check on these.
		sp = simparams.FromCat_statshear(
			name = code,
			snc_type = 2000,
			shear = 0.1,
			dist_type="cat"
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":4000,
			"ncpu":40,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "tw-1": # (no SNC) (20 M)
		sp = simparams.FromCat_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			dist_type="cat"
		)
		drawconf = {
			"n":100000,
			"nc":1000,
			"nrea":1,
			"ncat":200,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "tw-1-etype2": # (no SNC) (20 M)
		sp = simparams.FromCat_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			dist_type="cat",
			e_type = 2
		)
		drawconf = {
			"n":100000,
			"nc":1000,
			"nrea":1,
			"ncat":200,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "tw-1-etype2-emaxamp7": # (no SNC) (20 M)
		sp = simparams.FromCat_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			dist_type="cat",
			e_type = 2,
			e_maxamp = 0.7
		)
		drawconf = {
			"n":100000,
			"nc":1000,
			"nrea":1,
			"ncat":200,
			"ncpu":100,
			"groupmode":"shear",
			"skipdone":False	
		}


	elif code == "vo-1": # (20 M, no SNC)
		sp = simparams.FromCat_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			dist_type="cat"
		)
		drawconf = {
			"n":100000,
			"nc":100,
			"nrea":1,
			"ncat":200,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "vo-1-etype2": # (20 M, no SNC)
		sp = simparams.FromCat_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			dist_type="cat",
			e_type = 2
		)
		drawconf = {
			"n":100000,
			"nc":100,
			"nrea":1,
			"ncat":200,
			#"ncpu":50,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "vo-1-etype2-emaxamp7": # (20 M, no SNC)
		sp = simparams.FromCat_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			dist_type="cat",
			e_type = 2,
			e_maxamp = 0.7
		)
		drawconf = {
			"n":100000,
			"nc":100,
			"nrea":1,
			"ncat":200,
			#"ncpu":50,
			"ncpu":25,
			"groupmode":"shear",
			"skipdone":False	
		}



	else:
		
		logger.info("Unknown code '{}'".format(code))
		exit()
		
	
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
		drawcatkwargs={"n":drawconf["n"], "nc":drawconf["nc"], "stampsize":config.drawstampsize, "metadict":{"hack":"nicobackgals"}},
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

