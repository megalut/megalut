import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import megalut.plot
from megalut.plot.feature import Feature

import logging
logger = logging.getLogger(__name__)







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

