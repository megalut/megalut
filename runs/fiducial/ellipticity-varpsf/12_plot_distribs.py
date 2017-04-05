import megalut
import includes
import measfcts
import glob
import os
import numpy as np
import astropy
	
from matplotlib.patches import Ellipse
import psf 
	
import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)


simdir = os.path.join(includes.simdir, "EllipticityVarPSF")
simvaldir = os.path.join(includes.simvaldir, "EllipticityVarPSF")

component = "1"
main_pred = "s{}".format(component)
main_feat = Feature("tru_{}".format(main_pred))

	
for idir in [simdir]:#, simvaldir]:
	outdirplots = os.path.join(idir, "plots")
	
	if not os.path.exists(outdirplots):
		os.mkdir(outdirplots)
		
	if not os.path.exists(outdirplots):
		os.mkdir(outdirplots)
	
	catpath = os.path.join(idir, "groupmeascat_cases.pkl")
	
	
	cat = megalut.tools.io.readpickle(catpath)
	cat["adamom_frac"] = np.sum(cat["adamom_g1"].mask, axis=1)/float(cat["adamom_g1"].shape[1])
	s = megalut.tools.table.Selector("ok", [
		#("min", "adamom_flux", 0.),
		("max", "adamom_frac", 0.005),
		]
		)

	cat = s.select(cat)

	print megalut.tools.table.info(cat)
	
	reat = "All"
	
	adamom_flux = Feature("adamom_flux", rea=reat)
	adamom_sigma = Feature("adamom_sigma", rea=reat)
	adamom_rho4 = Feature("adamom_rho4", 1.3, 3.0, rea=reat)
	adamom_g1 = Feature("adamom_g1", -0.7, 0.7, rea=reat)
	adamom_g2 = Feature("adamom_g2", -0.7, 0.7, rea=reat)
	tru_s1 = Feature("tru_s1", -0.7, 0.7, rea=reat)
	tru_s2 = Feature("tru_s2", -0.7, 0.7, rea=reat)
	trradius = Feature("tru_rad", rea=reat)
	trsb = Feature("tru_sb", rea=reat)
	snr = Feature("snr", rea=reat)

	# Now changing to the geometrical description of the PSF (and doing some rescaling)
	e1 = cat["tru_psf_g1"][::10]
	e2 = cat["tru_psf_g2"][::10]
	r = cat["tru_psf_sigma"][::10]/2.35
	x = cat["tru_gal_x_chip"][::10]
	y = cat["tru_gal_y_chip"][::10]
	
	# Plotting the e1, e2 space as a quiver plot
	fig = plt.figure(figsize=(22,6))
	ax = plt.subplot(131)
	plt.quiver(x, y, e1, e2)
	plt.xlabel("X image")
	plt.ylabel("Y image")
	plt.title("e1 - e2 space")
	plt.xlim(-0.05,1.05)
	plt.ylim(-0.05,1.05)
	
	a, b, theta = psf.complex2geometrical(e1, e2, r * 0.5, fact=20)

	# We can plot what the PSF will look like in the pixel space
	ax = plt.subplot(132, aspect='equal')
	
	for x_, y_, a_, b_, t_ in zip(x, y, a * 0.1, b * 0.1, theta):
		e = Ellipse((x_, y_), a_ , b_ , np.rad2deg(t_))
		e.set_clip_box(ax.bbox)
		e.set_alpha(0.4)
		ax.add_artist(e)
	plt.xlim(-0.05,1.05)
	plt.ylim(-0.05,1.05)
	plt.xlabel("X image")
	plt.ylabel("Y image")
	plt.title("image space (exaggerated)")
	
	# Plotting the FWHM
	ax = plt.subplot(133, aspect='equal')
	plt.scatter(x, y, s=r*200., c=r, edgecolors="None")
	cb = plt.colorbar()
	plt.xlabel("X image")
	plt.ylabel("Y image")
	cb.set_label('FWHM ["]')
	ax.set_xlim([-0.05, 1.05])
	ax.set_ylim([-0.05, 1.05])
	megalut.plot.hist.hist(ax, cat, snr)
	fig.savefig(os.path.join(outdirplots, "psf_field"))

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
	megalut.plot.scatter.scatter(ax, cat, tru_s1, tru_s2, snr)
	fig.savefig(os.path.join(outdirplots, "distrib_s1_s2"))	
	
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
