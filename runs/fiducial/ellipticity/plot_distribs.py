import megalut
import includes
import measfcts
import glob
import os
import numpy as np
import astropy

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)


simdir = os.path.join(includes.simdir, "Ellipticity")
simvaldir = os.path.join(includes.simvaldir, "Ellipticity")

component = "1"
main_pred = "s{}".format(component)
main_feat = Feature("tru_{}".format(main_pred))

	
for idir in [simdir, simvaldir]:
	outdirplots = os.path.join(idir, "plots")
	
	if not os.path.exists(outdirplots):
		os.mkdir(outdirplots)
	
	valprecatpath = os.path.join(idir, "groupmeascat.pkl")
	
	
	cat = megalut.tools.io.readpickle(valprecatpath)
	print megalut.tools.table.info(cat)
	
	reat = "All"
	
	adamom_flux = Feature("adamom_flux", rea=reat)
	adamom_sigma = Feature("adamom_sigma", rea=reat)
	adamom_rho4 = Feature("adamom_rho4", 1.3, 3.0, rea=reat)
	adamom_g1 = Feature("adamom_g1", -0.7, 0.7, rea=reat)
	adamom_g2 = Feature("adamom_g2", -0.7, 0.7, rea=reat)
	trradius = Feature("tru_rad", rea=reat)
	trsb = Feature("tru_sb", rea=reat)
	snr = Feature("snr", rea=reat)
	
	fig = plt.figure()
	ax = fig.add_subplot(1,1,1)
	megalut.plot.hist.hist(ax, cat, snr)
	fig.savefig(os.path.join(outdirplots, "distrib_snr"))
	
	fig = plt.figure()
	ax = fig.add_subplot(1,1,1)
	megalut.plot.scatter.scatter(ax, cat, adamom_g1, adamom_g2, snr)
	fig.savefig(os.path.join(outdirplots, "distrib_g1_g2"))
	
	
	fig = plt.figure()
	ax = fig.add_subplot(1,1,1)
	megalut.plot.hexbin.hexbin(ax, cat, adamom_g1, adamom_g2, gridsize=50)
	fig.savefig(os.path.join(outdirplots, "distrib_g1_g2_hexbin"))
	
	fig = plt.figure()
	ax = fig.add_subplot(1,1,1)
	megalut.plot.scatter.scatter(ax, cat, adamom_sigma, adamom_flux, snr)
	fig.savefig(os.path.join(outdirplots, "distrib_sigma_flux"))
	
	fig = plt.figure()
	ax = fig.add_subplot(1,1,1)
	megalut.plot.scatter.scatter(ax, cat, trradius, trsb, snr)
	fig.savefig(os.path.join(outdirplots, "distrib_radius_sb"))
	
	fig = plt.figure()
	ax = fig.add_subplot(1,1,1)
	megalut.plot.scatter.scatter(ax, cat, adamom_rho4, adamom_flux, snr)
	fig.savefig(os.path.join(outdirplots, "distrib_rho4_flux"))
	
	fig = plt.figure()
	ax = fig.add_subplot(1,1,1)
	megalut.plot.scatter.scatter(ax, cat, adamom_rho4, adamom_sigma, snr)
	fig.savefig(os.path.join(outdirplots, "distrib_rho4_sigma"))
	
	plt.show()
