"""
Classic simobscompa plot
"""

import megalut
import megalutgreat3
import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt
import numpy as np

import config

import os
import logging
logging.basicConfig(format=config.loggerformat, level=logging.INFO)



def main():

	great3 = config.load_run()

	spname = "G3CGCSersics_simobscompa"
	
	for subfield in config.subfields:
		
		measdir = great3.path("simmeas","%03i" % subfield)

		simcat = megalut.tools.io.readpickle(os.path.join(measdir, spname, "groupmeascat.pkl"))
		#print megalut.tools.table.info(simcat)

		#bestsub = megalut.tools.table.Selector("bestsub", [("is", "subfield", subfield)])
		#simcat = bestsub.select(simcat)
		#print megalut.tools.table.info(simcat)


		obscat = megalut.tools.io.readpickle(great3.path("obs", "img_%i_meascat.pkl"%(subfield)))
		#print megalut.tools.table.info(obscat)
	
		plotpath = great3.path("simmeas","%03i" % subfield, spname, "simobscompa.png")

		plot(simcat, obscat, filepath=plotpath)




def plot(simcat, obscat, filepath=None):

	# Some computations
	simcat["aperphot_sbr1"] = simcat["aperphot_sb2"] / simcat["aperphot_sb5"]
	obscat["aperphot_sbr1"] = obscat["aperphot_sb2"] / obscat["aperphot_sb5"]

	simcat["aperphot_sbr2"] = simcat["aperphot_sb3"] / simcat["aperphot_sb8"]
	obscat["aperphot_sbr2"] = obscat["aperphot_sb3"] / obscat["aperphot_sb8"]

	simcat["adamom_log_flux"] = np.log10(simcat["adamom_flux"])
	obscat["adamom_log_flux"] = np.log10(obscat["adamom_flux"])

	
	rea = None

	adamom_flux = Feature("adamom_flux", rea=rea)
	adamom_sigma = Feature("adamom_sigma", 0, 10, rea=rea)
	adamom_rho4 = Feature("adamom_rho4", 1.3, 2.6, rea=rea)
	adamom_g1 = Feature("adamom_g1", -0.7, 0.7, rea=rea)
	adamom_g2 = Feature("adamom_g2", -0.7, 0.7, rea=rea)
	adamom_log_flux = Feature("adamom_log_flux", rea=rea)
	aperphot_sbr1 = Feature("aperphot_sbr1", rea=rea)
	aperphot_sbr2 = Feature("aperphot_sbr2", rea=rea)
	snr = Feature("snr", -3, 30, rea=rea)
	aperphot_sb2 = Feature("aperphot_sb2", 0, 5, rea=rea)
	aperphot_sb3 = Feature("aperphot_sb3", 0, 5, rea=rea)
	aperphot_sb5 = Feature("aperphot_sb5", 0, 5, rea=rea)
	aperphot_sb8 = Feature("aperphot_sb8", 0, 5, rea=rea)
	skymad = Feature("skymad", rea=rea)
	skystd = Feature("skystd", rea=rea)
	skymed = Feature("skymed", rea=rea)
	skymean = Feature("skymean", rea=rea)

	#psf_adamom_g1 = Feature("psf_adamom_g1", -0.06, 0.06, rea=rea)
	#psf_adamom_g2 = Feature("psf_adamom_g2", -0.06, 0.06, rea=rea)
	#psf_adamom_sigma = Feature("psf_adamom_sigma", rea=rea)





	fig = plt.figure(figsize=(18, 12))
	#fig = plt.figure(figsize=(8, 8))

	ax = fig.add_subplot(3, 4, 1)

	megalut.plot.contour.simobs(ax, simcat, obscat, adamom_g1, adamom_g2, plotpoints=False, nlines=2)
	#megalut.plot.hist.hist(ax, simcat, snr, color="red", label="Training", normed=True)
	#megalut.plot.hist.hist(ax, obscat, snr, color="blue", label="GREAT3", normed=True)

	
	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.scatter.simobs(ax, simcat, obscat, snr, adamom_sigma, legend=True)

	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.scatter.simobs(ax, simcat, obscat, adamom_g1, adamom_g2)

	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.scatter.simobs(ax, simcat, obscat, adamom_rho4, adamom_sigma)


	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.scatter.simobs(ax, simcat, obscat, aperphot_sb2, aperphot_sb3)

	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.scatter.simobs(ax, simcat, obscat, aperphot_sb5, aperphot_sb8)

	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.scatter.simobs(ax, simcat, obscat, aperphot_sbr1, aperphot_sbr2)

	ax = fig.add_subplot(3, 4, 8)
	megalut.plot.scatter.simobs(ax, simcat, obscat, adamom_log_flux, adamom_rho4)
	#ax.set_xscale("log", nonposx='clip')


	ax = fig.add_subplot(3, 4, 9)
	megalut.plot.contour.simobs(ax, simcat, obscat, skymad, skymean, plotpoints=False)

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
	
