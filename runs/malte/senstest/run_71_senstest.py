"""
Runs the "wrong" trainings on the sensitivity test data and writes the output files

"""
import megalut.tools
import megalut.learn
import megalut
import astropy

import config
import numpy as np
import os
import glob

from megalut.tools.feature import Feature

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

import SHE_GSM_BiasMeasurement.bias_calculation
import SHE_GSM_BiasMeasurement.bias_measurement_outputting

import run_54_wscale

####### configuration


codestrs = [
	"pp0_ep0_sp0",
	#"pp2_ep0_sp0", "pp1_ep0_sp0", "pm1_ep0_sp0", "pm2_ep0_sp0",
	#"pp0_ep2_sp0", "pp0_ep1_sp0", "pp0_em1_sp0", "pp0_em2_sp0",
	"pp0_ep0_sp2", "pp0_ep0_sp1", "pp0_ep0_sm1", "pp0_ep0_sm2", 
	]

outdir = "s_dbshear_v4"

######


meascatpath = os.path.join(config.obsproddir, "meascat.pkl")
resdir = os.path.join(config.workdir, "megalut", "res", outdir)
if not os.path.isdir(resdir):
	os.makedirs(resdir)

for codestr in codestrs:

	pcode = codestr[0:3]
	ecode = codestr[4:7]
	scode = codestr[8:11]
	bryancodestr = "{}_{}_{}".format(pcode, scode, ecode)

	traindir = os.path.join(config.workdir, "megalut", "train", codestr)

	predcatpath = os.path.join(resdir, "pred_{}.pkl".format(codestr))

	predscatpath = os.path.join(resdir, "pred_scaling_{}.pkl".format(codestr))
	scalepath = os.path.join(resdir, "scales_{}.pkl".format(codestr))	

	fitscatfilepath = os.path.join(resdir, "catalog_MegaLUT_{}.fits".format(bryancodestr))

	metricfilepath = os.path.join(resdir, "bias_measurements_MegaLUT_{}.fits".format(bryancodestr))

	
	# Reading in the catalog
	"""
	# The actual Bryan data:
	cat = megalut.tools.io.readpickle(meascatpath)
	cat["tru_s1"] = cat["shear_magnitude"] * np.cos(2.0 * cat["shear_angle"] * np.pi/180.0)
	cat["tru_s2"] = cat["shear_magnitude"] * np.sin(2.0 * cat["shear_angle"] * np.pi/180.0)
	#print megalut.tools.table.info(cat)
	#exit()
	"""
	
	# My mock data
	"""
	cat = megalut.tools.io.readpickle("/vol/fohlen11/fohlen11_1/mtewes/Euclid/senstest/megalut/simmeas/pp0_ep0_sp0/vo-mimicdata-6/groupmeascat.pkl")
	#cat = cat[0:len(cat)/6]
	cat["ID"] = 1 # Just to fake Bryan's one
	#print megalut.tools.table.info(cat)
	#exit()
	"""
	
	# My mock sheardb data
	
	cat = megalut.tools.io.readpickle("/vol/fohlen11/fohlen11_1/mtewes/Euclid/senstest/megalut/simmeas/pp0_ep0_sp0/vo-mimicdata-dbshear/groupmeascat.pkl")
	cat["ID"] = 1 # Just to fake Bryan's one
	#print megalut.tools.table.info(cat)
	#exit()

	
	
	
	# Predicting				
	sheartraindir = os.path.join(traindir, config.datasets["train-shear"])
	weighttraindir = os.path.join(traindir, config.datasets["train-weight"])

	cat = megalut.learn.tenbilacrun.predict(cat, config.shearconflist , sheartraindir)
	if len(config.weightconflist) > 0:
		cat = megalut.learn.tenbilacrun.predict(cat, config.weightconflist , weighttraindir)
	
	megalut.tools.io.writepickle(cat, predcatpath)
	


	# Scaling the weights of this catalog
	cat = megalut.tools.io.readpickle(predcatpath)
	
	
	#valname = "pred_{}".format(config.datasets["valid-overall"]) # Too messy to add everything here.
	#predcatpath = os.path.join(config.valdir, valname + ".pkl")
	#cat = megalut.tools.io.readpickle(predcatpath)
	#cat = megalut.tools.io.readpickle("/vol/fohlen11/fohlen11_1/mtewes/Euclid/senstest/megalut/val/pp0_ep0_sp0/pred_vo-mimicdata-6.pkl")
	
	
	
	# Catalog to use for scaling weights:
	scatpath = os.path.join(config.workdir, "megalut", "simmeas", codestr, config.datasets["train-weight"], "groupmeascat.pkl")
	
	sheartraindir = os.path.join(config.workdir, "megalut", "train", codestr, config.datasets["train-shear"])
	weighttraindir = os.path.join(config.workdir, "megalut", "train", codestr, config.datasets["train-weight"])

	scat = megalut.tools.io.readpickle(scatpath)
	#scat = scat[0:1]
	scat = megalut.learn.tenbilacrun.predict(scat, config.shearconflist , sheartraindir)
	scat = megalut.learn.tenbilacrun.predict(scat, config.weightconflist , weighttraindir)

	megalut.tools.io.writepickle(scat, predscatpath)
	
	scat = megalut.tools.io.readpickle(predscatpath)

	trufeat = Feature("tru_s1")
	predfeat = Feature("pre_s1", rea="all")
	wfeat = Feature("pre_s1w", rea="all")	
	scale1 = run_54_wscale.wscale(scat, trufeat, predfeat, wfeat)

	trufeat = Feature("tru_s2")
	predfeat = Feature("pre_s2", rea="all")
	wfeat = Feature("pre_s2w", rea="all")	
	scale2 = run_54_wscale.wscale(scat, trufeat, predfeat, wfeat)
	
	
	scales = np.array([scale1, scale2])
	megalut.tools.io.writepickle(scales, scalepath)
	
	
	scales = megalut.tools.io.readpickle(scalepath)

	cat["pre_s1w"] *= scales[0]
	cat["pre_s2w"] *= scales[1]

#	cat["pre_s1w"] *= 25.0
#	cat["pre_s2w"] *= 25.0
	
	
	# Writing output catalog
	bcat = cat.copy()
	
	bcat["GAL_G1_ERR"] = np.sqrt(1.0/np.clip(bcat["pre_s1w"], 1e-18, 1e18))
	bcat["GAL_G2_ERR"] = np.sqrt(1.0/np.clip(bcat["pre_s2w"], 1e-18, 1e18))

	#bcat["GAL_G1_ERR"] = 0.25
	#bcat["GAL_G2_ERR"] = 0.25


	bcat["GAL_EST_G1"] = bcat["pre_s1"]
	bcat["GAL_EST_G2"] = bcat["pre_s2"]
	bcat["GAL_SIM_G1"] = bcat["tru_s1"]
	bcat["GAL_SIM_G2"] = bcat["tru_s2"]

	rea="all"
	GAL_G1_ERR = Feature("GAL_G1_ERR", rea=rea)
	GAL_G2_ERR = Feature("GAL_G2_ERR", rea=rea)
	GAL_EST_G1 = Feature("GAL_EST_G1", rea=rea)
	GAL_EST_G2 = Feature("GAL_EST_G2", rea=rea)
	GAL_SIM_G1 = Feature("GAL_SIM_G1")
	GAL_SIM_G2 = Feature("GAL_SIM_G2")
	ID = Feature("ID")
	
	# Dealing with the masked measurements
	
	mask = bcat["pre_s1"].mask
	bcat["GAL_G1_ERR"][mask] = 1e18
	bcat["GAL_G2_ERR"][mask] = 1e18
	bcat["GAL_EST_G1"][mask] = 0.0
	bcat["GAL_EST_G2"][mask] = 0.0

	# Get rid of masks
	bcat["GAL_G1_ERR"].mask = np.zeros(len(bcat))
	bcat["GAL_G2_ERR"].mask = np.zeros(len(bcat))
	bcat["GAL_EST_G1"].mask = np.zeros(len(bcat))
	bcat["GAL_EST_G2"].mask = np.zeros(len(bcat))

		
	bcat = megalut.tools.feature.get1Ddata(bcat, [ID, GAL_G1_ERR, GAL_G2_ERR, GAL_EST_G1, GAL_EST_G2, GAL_SIM_G1, GAL_SIM_G2], keepmasked=True)
	
	bcat.write(fitscatfilepath, format="fits", overwrite=True)
	
	#print megalut.tools.table.info(bcat)
	
	
	# Stat-computing with Bryan's code
	
	bcat = astropy.table.Table.read(fitscatfilepath)
	print megalut.tools.table.info(bcat)
		
	ret = SHE_GSM_BiasMeasurement.bias_calculation.calculate_bias(bcat)
	SHE_GSM_BiasMeasurement.bias_measurement_outputting.output_bias_measurement(ret, metricfilepath, output_format="fits")

	

