import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import megalut.plot
from megalut.tools.feature import Feature

import logging
logger = logging.getLogger(__name__)


def simobscompa(run, simparams, prefix="adamom_", filepath=None):
	"""
	Classic comparision between obs and sims
	"""
	
	#simcatpath = megalut.meas.utils.simmeasdict(run.worksimdir, simparams).values()[0][0]
	simcatpath = "groupmeascat.pkl"
	
	simcat = megalut.tools.io.readpickle(os.path.join(run.worksimdir, simparams.name, simcatpath))
	
	#print simcat
	
	#exit()
	
	# And a bunch of the obs
	obscat = megalut.tools.io.readpickle(run.groupobspath)
			
	
	simcat = megalut.tools.table.shuffle(simcat)
	obscat = megalut.tools.table.shuffle(obscat)
	
	fig = plt.figure(figsize=(23, 11))
		
	flux = Feature(prefix+"flux", rea=0)
	sigma = Feature(prefix+"sigma", 0, 25, rea=0)
	
	try:
		rho4 = Feature(prefix+"rho4", 1.5, 2.5, rea=0)
	except:
		pass
	g1 = Feature(prefix+"g1", -0.7, 0.7, rea=0)
	g2 = Feature(prefix+"g2", -0.7, 0.7, rea=0)
	skymad = Feature("skymad", rea=0)
	skystd = Feature("skystd", rea=0)
	skymed = Feature("skymed", rea=0)
	skymean = Feature("skymean", rea=0)
	
	psf_g1 = Feature("tru_psf_g1", -0.06, 0.06, rea=0)
	psf_g2 = Feature("tru_psf_g2", -0.06, 0.06, rea=0)
	psf_sigma = Feature("tru_psf_sigma", rea=0)
	
	
	snr =Feature("snr", rea=0)
	#a = megalut.plot.feature.Feature("sewpy_AWIN_IMAGE", 1.0, 4.0)
	#fwhm = megalut.plot.feature.Feature("sewpy_FWHM_IMAGE", 1.0, 6.0)
	#sewpyflags = megalut.plot.feature.Feature("sewpy_FLAGS")
	#flags = megalut.plot.feature.Feature("Flag")
	
		
	ax = fig.add_subplot(2, 4, 1)
	megalut.plot.scatter.simobs(ax, simcat, obscat, flux, sigma, legend=True)

	ax = fig.add_subplot(2, 4, 2)
	try:
		megalut.plot.scatter.simobs(ax, simcat, obscat, sigma, rho4)
	except:
		pass

	ax = fig.add_subplot(2, 4, 3)
	megalut.plot.scatter.simobs(ax, simcat, obscat, g1, g2)
	
	ax = fig.add_subplot(2, 4, 4)
	megalut.plot.scatter.simobs(ax, simcat, obscat, flux, snr)
		
	ax = fig.add_subplot(2, 4, 5)
	megalut.plot.scatter.simobs(ax, simcat, obscat, flux, skystd)
	
	ax = fig.add_subplot(2, 4, 6)
	megalut.plot.scatter.simobs(ax, simcat, obscat, skymed, skymean)
	
	ax = fig.add_subplot(2, 4, 7)
	megalut.plot.scatter.simobs(ax, simcat, obscat, psf_sigma, sigma)
	
	ax = fig.add_subplot(2, 4, 8)
	megalut.plot.scatter.simobs(ax, simcat, obscat, psf_g1, psf_g2)
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.

	
	

def predsims(run, filepath=None):
	"""
	Simple comparision between predictions and truth, based on the training data.
	"""
	cat = megalut.tools.io.readpickle(os.path.join(run.workmldir, "selfprecat.pkl"))
	
	rg = 0.8
	
	tru_g1 = Feature("tru_g1", -rg, rg)
	tru_g2 = Feature("tru_g2", -rg, rg)
	tru_sigma = Feature("tru_sigma")
	tru_flux = Feature("tru_flux")
	
	rea = "full"
	
	pre_g1 = Feature("pre_g1", -rg, rg, rea=rea)
	pre_g2 = Feature("pre_g2", -rg, rg, rea=rea)
	pre_sigma = Feature("pre_sigma", rea=rea)
	pre_flux = Feature("pre_flux", rea=rea)
	
	snr = Feature("snr", rea=rea)
	
	fig = plt.figure(figsize=(22, 13))
	
	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_g1, pre_g1, showidline=True, idlinekwargs={"color":"red", "lw":2}, sidehists=True, ms=3)
	#megalut.plot.hexbin.hexbin(ax, cat, tru_g1, pre_g1)
	
	ax = fig.add_subplot(3, 4, 2)	
	megalut.plot.scatter.scatter(ax, cat, tru_g2, pre_g2, showidline=True, idlinekwargs={"color":"red", "lw":2}, sidehists=True, ms=3)
		
	ax = fig.add_subplot(3, 4, 3)	
	megalut.plot.scatter.scatter(ax, cat, tru_sigma, pre_sigma, showidline=True, idlinekwargs={"color":"red", "lw":2}, sidehists=True, ms=3)
	
	#ax = fig.add_subplot(3, 4, 4)	
	#megalut.plot.scatter.scatter(ax, cat, tru_flux, pre_flux, showidline=True, idlinekwargs={"color":"red", "lw":2}, sidehists=True, ms=3)

	ax = fig.add_subplot(3, 4, 5)	
	megalut.plot.scatter.scatter(ax, cat, tru_g1, pre_g1, snr, s=5, metrics=True)
		
	ax = fig.add_subplot(3, 4, 6)	
	megalut.plot.scatter.scatter(ax, cat, tru_g2, pre_g2, snr, s=5, metrics=True)
		
	ax = fig.add_subplot(3, 4, 7)	
	megalut.plot.scatter.scatter(ax, cat, tru_sigma, pre_sigma, snr, s=5, metrics=True)

	#ax = fig.add_subplot(3, 4, 8)	
	#megalut.plot.scatter.scatter(ax, cat, tru_flux, pre_flux, snr, s=5, metrics=True)

	#ax = fig.add_subplot(3, 4, 9)	
	#megalut.plot.scatter.scatter(ax, cat, tru_flux, pre_flux, showidline=True, idlinekwargs={"color":"red", "lw":2}, sidehists=True, ms=3)
	
	#ax = fig.add_subplot(3, 4, 10)	
	#megalut.plot.scatter.scatter(ax, cat, tru_flux, pre_flux, snr_narrow, s=5, metrics=False)
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	
	plt.close(fig) # Helps releasing memory when calling in large loops.
	
	



def simbias(run, filepath=None):

	
	#cat =  megalut.tools.io.readpickle(os.path.join(run.workmldir, "obsprecat.pkl"))
	cat =  megalut.tools.io.readpickle(os.path.join(run.workmldir, "selfprecat.pkl"))
	
	print cat.colnames
	#print len(cat)
	
	gridsize = 15
	mincnt = 100
	gerrrad = 0.02
	sigmaerrrad = 0.2
	
	rea = -100
	rea = "full"
	
	cmap = matplotlib.cm.get_cmap("rainbow")
	
	hexbinkwargs = {"gridsize":gridsize, "mincnt":mincnt, "cmap":cmap}
	counthexbinkwargs = {"gridsize":gridsize}

	
	
	cat["g1err"] = np.transpose(cat["pre_g1"].T - cat["tru_g1"].T) # those T are the price to pay for having the rea as second index.
	cat["g2err"] = np.transpose(cat["pre_g2"].T - cat["tru_g2"].T)
	cat["sigmaerr"] = np.transpose(cat["pre_sigma"].T - cat["tru_sigma"].T)
	
	cat["adamomg1err"] = np.transpose(cat["adamom_g1"].T - cat["tru_g1"].T)
	cat["adamomg2err"] = np.transpose(cat["adamom_g2"].T - cat["tru_g2"].T)
	
	g1err = Feature("g1err", -gerrrad, gerrrad, nicename="Bias on g1", rea=rea)
	g2err = Feature("g2err",-gerrrad, gerrrad, nicename="Bias on g2", rea=rea)
	sigmaerr = Feature("sigmaerr",-sigmaerrrad, sigmaerrrad, nicename="Bias on sigma", rea=rea)
	
	
	adamomg1err = Feature("adamomg1err", -5.0*gerrrad, 5.0*gerrrad, nicename="Bias on g1 (adamom only)", rea=rea)
	adamomg2err = Feature("adamomg2err", -5.0*gerrrad, 5.0*gerrrad, nicename="Bias on g2 (adamom only)", rea=rea)
	
	g1 = Feature("tru_g1")#, nicename="True galaxy ellipticity g1")
	g2 = Feature("tru_g2")#, nicename="True galaxy ellipticity g2")
	
	psfg1 = Feature("tru_psf_g1")#, nicename="True PSF ellipticity g1")
	psfg2 = Feature("tru_psf_g2")#, nicename="True PSF ellipticity g2")
	
	snr = Feature("snr", rea=rea)
	
	flux = Feature("tru_flux")
	sigma = Feature("tru_sigma")
	
	
	fig = plt.figure(figsize=(21, 12))

	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.hexbin.hexbin(ax, cat, flux, sigma, g1err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.hexbin.hexbin(ax, cat, snr, g1, g1err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.hexbin.hexbin(ax, cat, flux, g1, g1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.hexbin.hexbin(ax, cat, flux, g2, g2err, **hexbinkwargs)
	
	
	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, g1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, g2err, **hexbinkwargs)
	
	
	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.hexbin.hexbin(ax, cat, psfg1, psfg2, g1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 8)
	megalut.plot.hexbin.hexbin(ax, cat, psfg1, psfg2, g2err, **hexbinkwargs)
	
	
	ax = fig.add_subplot(3, 4, 9)
	#megalut.plot.hexbin.hexbin(ax, cat, g1, g2, **counthexbinkwargs)
	megalut.plot.scatter.scatter(ax, cat, snr, sigma, sidehists=True, ms=2)
	
	ax = fig.add_subplot(3, 4, 10)
	megalut.plot.hexbin.hexbin(ax, cat, flux, sigma, **counthexbinkwargs)
	
	
	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, adamomg1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 12)
	megalut.plot.hexbin.hexbin(ax, cat, sigma, snr, sigmaerr, **hexbinkwargs)
	
	"""
	psfselector = megalut.tools.table.Selector("Particular PSF",
		[("in", "tru_psf_g1", 0.00, 0.05), ("in", "tru_psf_g2", -0.01, 0.01)]) 
	psfselcat = psfselector.select(cat)


	ax = fig.add_subplot(3, 4, 9)
	megalut.plot.hexbin.hexbin(ax, psfselcat, g1, g2, g1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 10)
	megalut.plot.hexbin.hexbin(ax, psfselcat , g1, g2, g2err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.hexbin.hexbin(ax, psfselcat, g1, g2, adamomg1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 12)
	megalut.plot.hexbin.hexbin(ax, psfselcat, g1, g2, adamomg2err, **hexbinkwargs)
	"""
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.




def sbebias(run, filepath=None):

	cat =  megalut.tools.io.readpickle(os.path.join(run.workmldir, "obsprecat.pkl"))
		
	print cat.colnames
	print len(cat)
	
	gridsize = 6
	mincnt = 100
	
	gerrrad = 0.01
	relgerrrad = 25.0
	cmap = matplotlib.cm.get_cmap("rainbow")
	
	hexbinkwargs = {"gridsize":gridsize, "mincnt":mincnt, "cmap":cmap}

	
	cat["g1err"] = np.transpose(cat["pre_g1"].T - cat["Galaxy_g1"].T) # those T are the price to pay for having the rea as second index.
	cat["g2err"] = np.transpose(cat["pre_g2"].T - cat["Galaxy_g2"].T)
	
	cat["relg1err"] = 100.0*np.transpose(cat["g1err"].T / cat["Galaxy_g1"].T)
	cat["relg2err"] = 100.0*np.transpose(cat["g2err"].T / cat["Galaxy_g2"].T)
	
	cat["tru_sigma"] = 20.0*cat["Galaxy_sigma_arcsec"]
	
	
	g1err = Feature("g1err", -gerrrad, gerrrad, nicename="Bias on shear g1")
	g2err = Feature("g2err",-gerrrad, gerrrad, nicename="Bias on shear g2")
	relg1err = Feature("relg1err", -relgerrrad, relgerrrad, nicename="Rel. bias on shear g1 in %")
	relg2err = Feature("relg2err",-relgerrrad, relgerrrad, nicename="Rel. bias on shear g2 in %")

	pre_g1 = Feature("pre_g1", -1.0, 1.5, nicename="Predicted g1") # To get room for the metrics display...
	pre_g2 = Feature("pre_g2", -1.0, 1.5, nicename="Predicted g2")
	
	g1 = Feature("Galaxy_g1", nicename="True galaxy shear g1")
	g2 = Feature("Galaxy_g2", nicename="True galaxy shear g2")
	e1 = Feature("Galaxy_e1", nicename="True galaxy ellipticity e1")
	e2 = Feature("Galaxy_e2", nicename="True galaxy ellipticity e2")
	psfe1 = Feature("tru_psf_g1", nicename="True PSF ellipticity g1")
	psfe2 = Feature("tru_psf_g2", nicename="True PSF ellipticity g2")
	
	snr = Feature("snr")
	pre_sigma = Feature("pre_sigma")
	tru_sigma = Feature("tru_sigma")
	
	fig = plt.figure(figsize=(21, 12))
	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, g1, pre_g1, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)

	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.scatter.scatter(ax, cat, g2, pre_g2, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)

	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, relg1err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, relg2err, **hexbinkwargs)


	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.hexbin.hexbin(ax, cat, psfe1, psfe2, relg1err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.hexbin.hexbin(ax, cat, psfe1, psfe2, relg2err, **hexbinkwargs)
	
	
	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.scatter.scatter(ax, cat, tru_sigma, pre_sigma, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)
	
	ax = fig.add_subplot(3, 4, 8)
	megalut.plot.hexbin.hexbin(ax, cat, tru_sigma, pre_sigma, bins="log", cblabel="log(counts)", gridsize=40, showidline=True, idlinekwargs={"color":"red", "lw":2})
	
	
	ax = fig.add_subplot(3, 4, 9)
	megalut.plot.hexbin.hexbin(ax, cat, g1, snr, relg1err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 10)
	megalut.plot.hexbin.hexbin(ax, cat, g2, snr, relg2err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.hexbin.hexbin(ax, cat, g1, tru_sigma, relg1err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 12)
	megalut.plot.hexbin.hexbin(ax, cat, g2, tru_sigma, relg2err, **hexbinkwargs)
	
	
	
	"""
	
	psfselector = megalut.tools.table.Selector("Particular PSF",
		[("in", "tru_psf_g1", 0.00, 0.05), ("in", "tru_psf_g2", -0.01, 0.01)]) 
	psfselcat = psfselector.select(cat)


	ax = fig.add_subplot(3, 4, 9)
	megalut.plot.hexbin.hexbin(ax, psfselcat, g1, g2, g1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 10)
	megalut.plot.hexbin.hexbin(ax, psfselcat , g1, g2, g2err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.hexbin.hexbin(ax, psfselcat, g1, g2, adamomg1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 12)
	megalut.plot.hexbin.hexbin(ax, psfselcat, g1, g2, adamomg2err, **hexbinkwargs)
	"""
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.

