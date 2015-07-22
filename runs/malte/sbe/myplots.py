import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import megalut.plot
from megalut.plot.feature import Feature

import logging
logger = logging.getLogger(__name__)


def simobscompa(run, simparams, prefix="adamom_", filepath=None):
	"""
	Classic comparision between obs and sims
	"""
	
	simcatpath = megalut.meas.utils.simmeasdict(run.worksimdir, simparams).values()[0][0]
	simcat = megalut.tools.io.readpickle(os.path.join(run.worksimdir, simparams.name, simcatpath))
				
	# And a bunch of the obs
	obscat = megalut.tools.io.readpickle(run.groupobspath)
			
	
	simcat = megalut.tools.table.shuffle(simcat)
	obscat = megalut.tools.table.shuffle(obscat)
	
	fig = plt.figure(figsize=(23, 11))
		
	flux = Feature(prefix+"flux")
	sigma = Feature(prefix+"sigma", 0, 25)
	
	try:
		rho4 = Feature(prefix+"rho4", 1.5, 2.5)
	except:
		pass
	g1 = Feature(prefix+"g1", -0.7, 0.7)
	g2 = Feature(prefix+"g2", -0.7, 0.7)
	skymad = Feature("skymad")
	skystd = Feature("skystd")
	skymed = Feature("skymed")
	skymean = Feature("skymean")
	
	psf_g1 = Feature("tru_psf_g1", -0.06, 0.06)
	psf_g2 = Feature("tru_psf_g2", -0.06, 0.06)
	psf_sigma = Feature("tru_psf_sigma")
	
	
	snr =Feature("snr")
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
	
	pre_g1 = Feature("pre_g1", -rg, rg, rea=0)
	pre_g2 = Feature("pre_g2", -rg, rg, rea=0)
	pre_sigma = Feature("pre_sigma", rea=0)
	pre_flux = Feature("pre_flux", rea=0)
	
	snr = Feature("snr", rea=0)
	
	fig = plt.figure(figsize=(22, 13))
	
	
	ax = fig.add_subplot(3, 4, 1)	
	megalut.plot.scatter.scatter(ax, cat, tru_g1, pre_g1, show_id_line=True, idlinekwargs={"color":"red", "lw":2}, sidehists=True, ms=3)
	
	ax = fig.add_subplot(3, 4, 2)	
	megalut.plot.scatter.scatter(ax, cat, tru_g2, pre_g2, show_id_line=True, idlinekwargs={"color":"red", "lw":2}, sidehists=True, ms=3)
		
	ax = fig.add_subplot(3, 4, 3)	
	megalut.plot.scatter.scatter(ax, cat, tru_sigma, pre_sigma, show_id_line=True, idlinekwargs={"color":"red", "lw":2}, sidehists=True, ms=3)
	
	#ax = fig.add_subplot(3, 4, 4)	
	#megalut.plot.scatter.scatter(ax, cat, tru_flux, pre_flux, show_id_line=True, idlinekwargs={"color":"red", "lw":2}, sidehists=True, ms=3)

	ax = fig.add_subplot(3, 4, 5)	
	megalut.plot.scatter.scatter(ax, cat, tru_g1, pre_g1, snr, s=5, metrics=True)
		
	ax = fig.add_subplot(3, 4, 6)	
	megalut.plot.scatter.scatter(ax, cat, tru_g2, pre_g2, snr, s=5, metrics=True)
		
	ax = fig.add_subplot(3, 4, 7)	
	megalut.plot.scatter.scatter(ax, cat, tru_sigma, pre_sigma, snr, s=5, metrics=True)

	#ax = fig.add_subplot(3, 4, 8)	
	#megalut.plot.scatter.scatter(ax, cat, tru_flux, pre_flux, snr, s=5, metrics=True)

	#ax = fig.add_subplot(3, 4, 9)	
	#megalut.plot.scatter.scatter(ax, cat, tru_flux, pre_flux, show_id_line=True, idlinekwargs={"color":"red", "lw":2}, sidehists=True, ms=3)
	
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
	print len(cat)
	
	gridsize = 15
	mincnt = 100
	
	gerrrad = 0.02
	cmap = matplotlib.cm.get_cmap("rainbow")
	
	hexbinkwargs = {"gridsize":gridsize, "mincnt":mincnt, "cmap":cmap}

	
	cat["g1err"] = cat["pre_g1"] - cat["tru_g1"]
	cat["g2err"] = cat["pre_g2"] - cat["tru_g2"]
	
	cat["adamomg1err"] = cat["adamom_g1_rea0"] - cat["tru_g1"]
	cat["adamomg2err"] = cat["adamom_g2_rea0"] - cat["tru_g2"]
	
	g1err = Feature("g1err", -gerrrad, gerrrad, nicename="Bias on g1")
	g2err = Feature("g2err",-gerrrad, gerrrad, nicename="Bias on g2")
		
	adamomg1err = Feature("adamomg1err", -5.0*gerrrad, 5.0*gerrrad, nicename="Bias on g1 (adamom only)")
	adamomg2err = Feature("adamomg2err", -5.0*gerrrad, 5.0*gerrrad, nicename="Bias on g2 (adamom only)")
	
	
	g1 = Feature("tru_g1", nicename="True galaxy ellipticity g1")
	g2 = Feature("tru_g2", nicename="True galaxy ellipticity g2")
	
	psfg1 = Feature("tru_psf_g1", nicename="True PSF ellipticity g1")
	psfg2 = Feature("tru_psf_g2", nicename="True PSF ellipticity g2")
	
	
	
	
	flux = Feature("tru_flux")
	sigma = Feature("tru_sigma")
	
	
	fig = plt.figure(figsize=(21, 12))

	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.hexbin.hexbin(ax, cat, flux, sigma, g1err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.hexbin.hexbin(ax, cat, flux, sigma, g2err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.hexbin.hexbin(ax, cat, flux, g1, g1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.hexbin.hexbin(ax, cat, flux, g2, g2err, **hexbinkwargs)
	
	
	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, g1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, g2err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, adamomg1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 8)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, adamomg2err, **hexbinkwargs)
	
	
	
	
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
	
	gridsize = 15
	mincnt = 100
	
	gerrrad = 0.02
	cmap = matplotlib.cm.get_cmap("rainbow")
	
	hexbinkwargs = {"gridsize":gridsize, "mincnt":mincnt, "cmap":cmap}

	
	cat["g1err"] = cat["pre_g1"] - cat["Galaxy_e1"]
	cat["g2err"] = cat["pre_g2"] - cat["Galaxy_e2"]
	
	cat["adamomg1err"] = cat["adamom_g1"] - cat["Galaxy_e1"]
	cat["adamomg2err"] = cat["adamom_g2"] - cat["Galaxy_e2"]
	
	g1err = Feature("g1err", -gerrrad, gerrrad, nicename="Bias on g1")
	g2err = Feature("g2err",-gerrrad, gerrrad, nicename="Bias on g2")
		
	adamomg1err = Feature("adamomg1err", -5.0*gerrrad, 5.0*gerrrad, nicename="Bias on g1 (adamom only)")
	adamomg2err = Feature("adamomg2err", -5.0*gerrrad, 5.0*gerrrad, nicename="Bias on g2 (adamom only)")
	
	
	g1 = Feature("Galaxy_e1", nicename="True galaxy ellipticity e1")
	g2 = Feature("Galaxy_e2", nicename="True galaxy ellipticity e2")
	
	psfg1 = Feature("tru_psf_g1", nicename="True PSF ellipticity g1")
	psfg2 = Feature("tru_psf_g2", nicename="True PSF ellipticity g2")
	
	
	
	
	#flux = Feature("tru_flux")
	#sigma = Feature("tru_sigma")
	
	
	fig = plt.figure(figsize=(21, 12))

	"""
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.hexbin.hexbin(ax, cat, flux, sigma, g1err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.hexbin.hexbin(ax, cat, flux, sigma, g2err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.hexbin.hexbin(ax, cat, flux, g1, g1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.hexbin.hexbin(ax, cat, flux, g2, g2err, **hexbinkwargs)
	"""
	
	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, g1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, g2err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, adamomg1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 8)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, adamomg2err, **hexbinkwargs)
	
	
	
	
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
	
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		print "heelo"
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.

