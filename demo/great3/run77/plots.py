import numpy as np
import matplotlib.pyplot as plt

import megalut.plot
import megalut.plot.stamps

import numpy as np

import logging
logger = logging.getLogger(__name__)



def compute_snr(cat):
	cat["snr"] = cat["sewpy_FLUX_AUTO"] / cat["sewpy_FLUXERR_AUTO"]


def measfrac_adamom(cat):
	"""
	Measurement success fraction
	"""
	return float(np.sum(cat["adamom_flag"] == 0)) / float(len(cat))


def simobscompa(run, simparams):
	"""
	In feature space
	"""
			
	flux = megalut.plot.feature.Feature("adamom_flux", 0.1, 150, "Some flux")
	tru_flux = megalut.plot.feature.Feature("tru_flux", 0.1, 150, "True flux")
	
	
	sigma = megalut.plot.feature.Feature("adamom_sigma", 0.1, 11, "Some measured width")
	rho4 = megalut.plot.feature.Feature("adamom_rho4", 1.6, 2.8, "Some measured concentration")
	g1 = megalut.plot.feature.Feature("adamom_g1", -0.6, 0.6, "HSM g1")
	g2 = megalut.plot.feature.Feature("adamom_g2", -0.6, 0.6, "HSM g2")
	skymad = megalut.plot.feature.Feature("adamom_skymad", 0.01, 0.07)
	skystd = megalut.plot.feature.Feature("adamom_skystd", 0.01, 0.07)
	skymed = megalut.plot.feature.Feature("adamom_skymed", -0.05, 0.05)
	skymean = megalut.plot.feature.Feature("adamom_skymean", -0.05, 0.05)
	
	snr = megalut.plot.feature.Feature("snr", 0.1, 150, "SExtractor SNR")
	snr_narrow = megalut.plot.feature.Feature("snr", 0.1, 60, "SExtractor SNR")
	
	for subfield in run.subfields:
	
		simcat = megalut.tools.io.readpickle(run._get_path("simmeas", "%03i" % subfield, simparams.name, "rea0cat.pkl"))
		obscat = megalut.tools.io.readpickle(run._get_path("obs", "img_%i_meascat.pkl" % subfield))
		
		compute_snr(simcat)
		compute_snr(obscat)
	
		# measurement sucess fraction:
		txt = "Subfield %i, simparams '%s', measfrac_adamom_sim = %.3f, measfrac_adamom_obs = %.3f"\
			 % (subfield, simparams.name, measfrac_adamom(simcat), measfrac_adamom(obscat))
	
		fig = plt.figure(figsize=(18, 12))
		fig.subplots_adjust(bottom=0.07, top=0.92, left=0.05, right=0.95, wspace=0.2)

		fig.text(0.05, 0.95, txt, {"fontsize":15})
		
		ax1 = fig.add_subplot(231)
		megalut.plot.scatter.simobs(ax1, simcat, obscat, snr, sigma, legend=True)

		ax2 = fig.add_subplot(232)
		megalut.plot.scatter.simobs(ax2, simcat, obscat, sigma, rho4)

		ax3 = fig.add_subplot(233)
		megalut.plot.scatter.simobs(ax3, simcat, obscat, g1, g2)
		
		
		ax4 = fig.add_subplot(234)
		megalut.plot.scatter.simobs(ax4, simcat, obscat, snr_narrow, rho4)
	
		
		ax5 = fig.add_subplot(235)
		megalut.plot.scatter.simobs(ax5, simcat, obscat, skymad, skystd)
	
		#ax5 = fig.add_subplot(235)
		#megalut.plot.scatter.simobs(ax5, simcat, obscat, skymed, skymean)
		
		#ax6 = fig.add_subplot(236)
		#megalut.plot.scatter.scatter(ax6, simcat, tru_flux, flux_, sidehists=True, text="Simulations")
		
		#plt.tight_layout()
		plt.show()	
		plt.close(fig) # Helps releasing memory when calling in large loops.


