"""
Classic simobscompa plot
"""
import matplotlib
#matplotlib.use("AGG")

import megalut
import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt
import numpy as np

import config

import os
import logging
logger = logging.getLogger(__name__)



def main():

	
	simcat = megalut.tools.io.readpickle(os.path.join(config.simmeasdir, "simobscompa", "groupmeascat.pkl"))
	print megalut.tools.table.info(simcat)


	obscat = megalut.tools.io.readpickle(os.path.join(config.obsproddir, "sensitivity_testing_1_0/meascat_sensitivity_testing_1_0.pkl"))
	print megalut.tools.table.info(obscat)
	#obscat = obscat[:1000]
	
	
	#exit()
	plotpath = None
	plot(simcat, obscat, filepath=plotpath)
	logger.info("Plotted to {}".format(plotpath))




def plot(simcat, obscat, filepath=None):

	# Some computations

	simcat["adamom_log_flux"] = np.log10(simcat["adamom_flux"])
	obscat["adamom_log_flux"] = np.log10(obscat["adamom_flux"])

	
	rea = None

	adamom_flux = Feature("adamom_flux", rea=rea)
	adamom_sigma = Feature("adamom_sigma", 0, 10, rea=rea)
	adamom_rho4 = Feature("adamom_rho4", 1.3, 3.0, rea=rea)
	adamom_g1 = Feature("adamom_g1", -0.7, 0.7, rea=rea)
	adamom_g2 = Feature("adamom_g2", -0.7, 0.7, rea=rea)
	adamom_log_flux = Feature("adamom_log_flux", rea=rea)

	snr = Feature("snr", rea=rea)

	skymad = Feature("skymad", rea=rea)
	skystd = Feature("skystd", rea=rea)
	skymed = Feature("skymed", rea=rea)
	skymean = Feature("skymean", rea=rea)

	#psf_adamom_g1 = Feature("psf_adamom_g1", -0.06, 0.06, rea=rea)
	#psf_adamom_g2 = Feature("psf_adamom_g2", -0.06, 0.06, rea=rea)
	#psf_adamom_sigma = Feature("psf_adamom_sigma", rea=rea)


	fig = plt.figure(figsize=(24, 14))
	#fig = plt.figure(figsize=(8, 8))

	ax = fig.add_subplot(3, 5, 1)

	megalut.plot.contour.simobs(ax, simcat, obscat, adamom_g1, adamom_g2, plotpoints=False, nlines=2)
	#megalut.plot.hist.hist(ax, simcat, snr, color="red", label="Training", normed=True)
	#megalut.plot.hist.hist(ax, obscat, snr, color="blue", label="GREAT3", normed=True)

	ax = fig.add_subplot(3, 5, 2)
	megalut.plot.scatter.simobs(ax, simcat, obscat, adamom_g1, adamom_g2)
	
	
	ax = fig.add_subplot(3, 5, 3)
	megalut.plot.scatter.simobs(ax, simcat, obscat, snr, adamom_sigma, legend=True)

	ax = fig.add_subplot(3, 5, 4)
	megalut.plot.scatter.simobs(ax, simcat, obscat, adamom_flux, adamom_sigma)

	
	ax = fig.add_subplot(3, 5, 5)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, Feature("adamom_flux", 0, 10000, rea=rea), Feature("adamom_sigma", 0, 6, rea=rea))
	megalut.plot.scatter.simobs(ax, simcat, obscat, adamom_log_flux, adamom_sigma)

	# Comparing input values
	ax = fig.add_subplot(3, 5, 6)
	megalut.plot.scatter.simobs(ax, simcat, obscat, Feature("magnitude", rea=rea), Feature("bulge_ellipticity", rea=rea))

	ax = fig.add_subplot(3, 5, 7)
	megalut.plot.scatter.simobs(ax, simcat, obscat, Feature("hlr_bulge_arcsec", rea=rea), Feature("hlr_disk_arcsec", rea=rea))

	ax = fig.add_subplot(3, 5, 8)
	megalut.plot.scatter.simobs(ax, simcat, obscat, Feature("tilt", rea=rea), Feature("bulge_ellipticity", rea=rea))

	#ax = fig.add_subplot(3, 5, 9)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, adamom_log_flux, adamom_sigma)




	ax = fig.add_subplot(3, 5, 11)
	megalut.plot.contour.simobs(ax, simcat, obscat, skymad, skymean, plotpoints=False)

	#ax = fig.add_subplot(3, 5, 12)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, aperphot_log_sb2, aperphot_log_sb5)

	ax = fig.add_subplot(3, 5, 13)
	megalut.plot.scatter.simobs(ax, simcat, obscat, adamom_rho4, adamom_sigma)

	ax = fig.add_subplot(3, 5, 14)
	megalut.plot.scatter.simobs(ax, simcat, obscat, adamom_log_flux, adamom_rho4)
	#ax.set_xscale("log", nonposx='clip')

	
	#ax = fig.add_subplot(3, 4, 12)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, psf_adamom_g1, psf_adamom_g2)

	#ax = fig.add_subplot(3, 4, 2)
	#megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("tru_s2"))
	
	
	
	plt.tight_layout()

	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.


if __name__ == "__main__":
    main()
	
