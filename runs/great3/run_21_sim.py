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

# Choose a model for the simulations

"""
sp = simparams.G3CGCSersics(
	name="G3CGCSersics_train_nn",
	snc_type=1,
	shear=0,
	noise_level=0.0,
	obstype=config.great3.obstype,
	distmode="uni",
	)

n = 400
nc = 20
nrea = 10 # Even without noise, there is still the position jitter and pixelization
ncat = 5
ncpu = 5 # config.great3.ncpu
"""

"""
sp = simparams.G3CGCSersics(
	name="G3CGCSersics_train_nn_20rea",
	snc_type=1,
	shear=0,
	noise_level=0.0,
	obstype=config.great3.obstype,
	distmode="uni",
	)

n = 400
nc = 20
nrea = 20 # Even without noise, there is still the position jitter and pixelization
ncat = 5
ncpu = 5 # config.great3.ncpu
"""

"""
sp = simparams.G3CGCSersics()
sp.name = "G3CGCSersics_train_shear_snc100" # For shear training, with SNC, 500 cases per call
sp.snc_type = 100
sp.shear = 0.1
sp.noise_level = 1
sp.obstype = config.great3.obstype
sp.distmode = "uni"
n = 20 # Don't put this to zero, otherwise only one sersicn is used.
nc = 1
nrea = 1
ncat = 25
ncpu = 25
"""

"""
sp = simparams.G3CGCSersics()
sp.name = "G3CGCSersics_train_shear_snc100_nn" # For shear training, with SNC, 1000 cases per call
sp.snc_type = 100
sp.shear = 0.1
sp.noise_level = 0
sp.obstype = config.great3.obstype
sp.distmode = "uni"
n = 40 # Don't put this to zero, otherwise only one sersicn is used.
nc = 1
nrea = 1
ncat = 25
ncpu = 25
"""

"""
sp = simparams.G3CGCSersics()
sp.name = "G3CGCSersics_train_shear_snc100_nn_G3" # For shear training, with SNC, 1000 cases per call
sp.snc_type = 100
sp.shear = 0.1
sp.noise_level = 0
sp.obstype = config.great3.obstype
sp.distmode = "G3"
n = 40 # Don't put this to zero, otherwise only one sersicn is used.
nc = 1
nrea = 1
ncat = 25
ncpu = 25
"""

"""
sp = simparams.G3CGCSersics()
sp.name = "G3CGCSersics_valid_shear_snc100_G3" # For shear valid, with SNC, 1000 cases per call
sp.snc_type = 100
sp.shear = 0.1
sp.noise_level = 1
sp.obstype = config.great3.obstype
sp.distmode = "G3"
n = 40 # Don't put this to zero, otherwise only one sersicn is used.
nc = 1
nrea = 1
ncat = 25
ncpu = 25
"""
"""
sp = simparams.G3CGCSersics()
sp.name = "G3CGCSersics_valid_shear_snc1000_G3" # For shear valid, with SNC, 500 cases per call
sp.snc_type = 1000
sp.shear = 0.1
sp.noise_level = 1
sp.obstype = config.great3.obstype
sp.distmode = "G3"
n = 20 # Don't put this to zero, otherwise only one sersicn is used.
nc = 1
nrea = 1
ncat = 25
ncpu = 25
"""

"""
sp = simparams.G3CGCSersics()
sp.name = "G3CGCSersics_train_shear_snc10000" # For shear training, with SNC, 500 cases per call
sp.snc_type = 10000
sp.shear = 0.1
sp.noise_level = 1
sp.obstype = config.great3.obstype
sp.distmode = "uni"
n = 20 # Don't put this to zero, otherwise only one sersicn is used.
nc = 1
nrea = 1
ncat = 25
ncpu = 25

"""
"""
sp = simparams.G3CGCSersics(
	name="G3CGCSersics_train",
	snc_type=1,
	shear=0,
	noise_level=1.0, # Will get set to the correct level for each subfield.
	obstype=config.great3.obstype,
	distmode="uni",
	)

n = 400
nc = 20
nrea = 100 
ncat = 5
ncpu = 5 # config.great3.ncpu
"""

"""
sp = simparams.G3CGCSersics(
	name="G3CGCSersics_train_100rea",
	snc_type=1,
	shear=0,
	noise_level=1.0, # Will get set to the correct level for each subfield.
	obstype=config.great3.obstype,
	distmode="uni",
	)

n = 400
nc = 20
nrea = 100 
ncat = 5
ncpu = 25 # config.great3.ncpu
"""

"""
sp = simparams.G3CGCSersics(
	name="G3CGCSersics_simobscompa",
	snc_type=1,
	shear=0,
	noise_level=1,
	obstype=config.great3.obstype,
	#distmode="G3",
	distmode="uni",
	)

n = 1000
nc = 10
nrea = 1
ncat = 1
ncpu = 1
"""

"""
sp = simparams.G3CGCSersics()
sp.name = "G3CGCSersics_valid" # To check the training, with shear and SNC, 500 cases
sp.snc_type = 10000
sp.shear = 0.1
sp.noise_level = 1
sp.obstype = config.great3.obstype
sp.distmode = "uni"
n = 20 # Don't put this to zero, otherwise only one sersicn is used.
nc = 1
nrea = 1
ncat = 25
ncpu = 25
"""

"""
sp = simparams.G3CGCSersics_statell()
sp.name = "G3CGCSersics_statell" # For weight training to predict ellipticites (not for shear)
sp.snc_type = 1
sp.shear = 0.0
sp.noise_level = 1
sp.obstype = config.great3.obstype
sp.distmode = "G3"
n = 100
nc = 10
nrea = 1
ncat = 200
ncpu = 25
"""

"""
sp = simparams.G3CGCSersics_statshear()
sp.name = "G3CGCSersics_statshear" # For weight training for shear
sp.snc_type = 4
sp.shear = 0.1
sp.noise_level = 1
sp.obstype = config.great3.obstype
sp.distmode = "G3"
n = 2000
nc = 50
nrea = 1
ncat = 200
ncpu = 25
"""
"""
sp = simparams.G3CGCSersics_statshear()
sp.name = "G3CGCSersics_valid_overall" # For overall validation with weights
sp.snc_type = 4
sp.shear = 0.1
sp.noise_level = 1
sp.obstype = config.great3.obstype
sp.distmode = "G3"
n = 2000
nc = 50
nrea = 1
ncat = 200
ncpu = 25
"""


def main(args):
	
	logger.info("Drawing sims for {}...".format(args.set))
	
	if args.set == "train-shear":
		
	
	elif args.set == "overall-valid":

		sp = simparams.G3Sersics_statshear(
			name = "overall-valid", # For overall validation, we mimick a GREAT3 branch
			snc_type = 4,
			shear = 0.1,
			noise_level = 1,
			obstype = config.great3.obstype,
			distmode = "G3"
		)
		drawconf = {
			"n":2000,
			"nc":50,
			"nrea":1,
			"ncat":200,
			"ncpu":25			
		}

		
	else:
		raise RuntimeError("Unknown set, see code for defined names.")
	
	
	for subfield in config.great3.subfields:
		run(subfield)


def run(subfield, sp, drawconf):
	
	
	# We have to read in the obs catalog of this subfield to get the noise of the sky:
	if sp.noise_level != 0:
		obscat = megalut.tools.io.readpickle(config.great3.path("obs", "img_%i_meascat.pkl" % subfield))
		sp.noise_level = np.ma.mean(obscat["skymad"])
		logger.info("Noise level set to {}".format(sp.noise_level))
	
	# Getting the path to the correct directories
	simdir = config.great3.path("sim","%03i" % subfield)
	measdir = config.great3.path("simmeas","%03i" % subfield)
	
	# Loading the PSF for the subfield
	psfcat = megalut.tools.io.readpickle(config.great3.path("obs", "star_%i_meascat.pkl" % subfield))
	

	# Simulating images
	megalut.sim.run.multi(
		simdir=simdir,
		simparams=sp,
		drawcatkwargs={"n":n, "nc":nc, "stampsize":config.great3.stampsize()},
		drawimgkwargs={}, 
		psfcat=psfcat, psfselect="random",
		ncat=ncat, nrea=nrea, ncpu=ncpu,
		savepsfimg=False, savetrugalimg=False
	)


	# Measuring the newly drawn images
	megalut.meas.run.onsims(
		simdir=simdir,
		simparams=sp,
		measdir=measdir,
		measfct=measfcts.gal,
		measfctkwargs={"branch":config.great3},
		ncpu=ncpu,
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

	
	# For shear sims, we group the results in cases of same true shears
	if sp.shear > 0:
		
		#measdir = config.great3.path("simmeas","%03i" % subfield)
		#cat = megalut.tools.io.readpickle(os.path.join(measdir, sp.name, "groupmeascat.pkl"))
		
		cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])
		megalut.tools.table.keepunique(cat)
		#print megalut.tools.table.info(cat)
		megalut.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl")) # Just overwrite, don't need the other one

	
	# For statell sims, we group by ellipticity
	if "statell" in sp.name:
		
		cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_g1", "tru_g2"])
		megalut.tools.table.keepunique(cat)
		#print megalut.tools.table.info(cat)
		megalut.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl")) # Just overwrite, don't need the other one

	


parser = define_parser()
args = parser.parse_args()
#print args
main(args)

