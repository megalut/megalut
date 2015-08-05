import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import megalut.plot
from megalut.tools.feature import Feature

import logging
logger = logging.getLogger(__name__)


def simobscompa(run, simparams, prefix="adamom_", filepath=None, rea="full"):
	"""
	Classic comparision between obs and sims
	"""
	
	#simcatpath = megalut.meas.utils.simmeasdict(run.worksimdir, simparams).values()[0][0]
	simcatpath = "groupmeascat.pkl"
	
	simcat = megalut.tools.io.readpickle(os.path.join(run.worksimdir, simparams.name, simcatpath))
	
	# And a bunch of the obs
	obscat = megalut.tools.io.readpickle(run.groupobspath)
			
	simcat = megalut.tools.table.shuffle(simcat)
	obscat = megalut.tools.table.shuffle(obscat)
		
	flux = Feature(prefix+"flux", 0, 3200, rea=rea)
	sigma = Feature(prefix+"sigma", 0, 30, rea=rea)
	rho4 = Feature(prefix+"rho4", 1.3, 2.6, rea=rea)
	g1 = Feature(prefix+"g1", -0.8, 0.8, rea=rea)
	g2 = Feature(prefix+"g2", -0.8, 0.8, rea=rea)
	skymad = Feature("skymad", rea=rea)
	skystd = Feature("skystd", rea=rea)
	skymed = Feature("skymed", rea=rea)
	skymean = Feature("skymean", rea=rea)
	psf_g1 = Feature("tru_psf_g1", -0.06, 0.06, rea=rea)
	psf_g2 = Feature("tru_psf_g2", -0.06, 0.06, rea=rea)
	psf_sigma = Feature("tru_psf_sigma", rea=rea)
	snr =Feature("snr", 0, 70, rea=rea)

	fig = plt.figure(figsize=(23, 11))
		
	ax = fig.add_subplot(2, 4, 1)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, flux, sigma, sidehists=False, legend=False, pale=True)
	megalut.plot.contour.simobs(ax, simcat, obscat, flux, sigma, legend=True)

	ax = fig.add_subplot(2, 4, 2)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, sigma, rho4, sidehists=False, legend=False, pale=True)
	megalut.plot.contour.simobs(ax, simcat, obscat, sigma, rho4)

	ax = fig.add_subplot(2, 4, 3)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, g1, g2, sidehists=False, legend=False, pale=True)
	megalut.plot.contour.simobs(ax, simcat, obscat, g1, g2)
	
	ax = fig.add_subplot(2, 4, 4)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, flux, snr, sidehists=False, legend=False, pale=True)
	megalut.plot.contour.simobs(ax, simcat, obscat, flux, snr)
		
	ax = fig.add_subplot(2, 4, 5)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, flux, skystd, sidehists=False, legend=False, pale=True)	
	megalut.plot.contour.simobs(ax, simcat, obscat, skymad, skystd)
	
	ax = fig.add_subplot(2, 4, 6)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, skymed, skymean, sidehists=False, legend=False, pale=True)
	megalut.plot.contour.simobs(ax, simcat, obscat, skymed, flux)
	
	ax = fig.add_subplot(2, 4, 7)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, psf_sigma, sigma, sidehists=False, legend=False, pale=True)
	megalut.plot.contour.simobs(ax, simcat, obscat, psf_sigma, sigma)
	
	ax = fig.add_subplot(2, 4, 8)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, psf_g1, psf_g2, sidehists=False, legend=False, pale=True)
	megalut.plot.contour.simobs(ax, simcat, obscat, psf_g1, psf_g2)
	
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.

	
	

def predsims(run, filepath=None, rea="full"):
	"""
	Simple comparision between predictions and truth, based on the training data.
	"""
	cat = megalut.tools.io.readpickle(os.path.join(run.workmldir, "selfprecat.pkl"))
	
	rg = 0.8
	
	tru_g1 = Feature("tru_g1", -rg, rg)
	tru_g2 = Feature("tru_g2", -rg, rg)
	tru_sigma = Feature("tru_sigma")
	tru_flux = Feature("tru_flux")
	
	
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
	
	



def simbias(run, filepath=None, rea="full"):

	
	#cat =  megalut.tools.io.readpickle(os.path.join(run.workmldir, "obsprecat.pkl"))
	cat =  megalut.tools.io.readpickle(os.path.join(run.workmldir, "selfprecat.pkl"))
	
	print cat.colnames
	#print len(cat)
	
	gridsize = 15
	mincnt = 100
	gerrrad = 0.02
	sigmaerrrad = 0.2
	
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
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, **counthexbinkwargs)
	#megalut.plot.scatter.scatter(ax, cat, snr, sigma, sidehists=True, ms=2)
	
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




def predsbe(run, filepath=None):
	
	cat =  megalut.tools.io.readpickle(os.path.join(run.workmldir, "obsprecat.pkl"))
		
	print cat.colnames
	#print len(cat)
	
	cat = megalut.tools.table.shuffle(cat)#[:100000]
	
	
	cat["tru_e"] = np.hypot(cat["Galaxy_e1"], cat["Galaxy_e2"])
	cat["tru_g"] = np.hypot(cat["Galaxy_g1"], cat["Galaxy_g2"])
	cat["psf_g"] = np.hypot(cat["tru_psf_g1"], cat["tru_psf_g2"])
	
	cat["g1res"] = cat["pre_g1"] - cat["Galaxy_g1"]
	cat["g2res"] = cat["pre_g2"] - cat["Galaxy_g2"]


	cmap = matplotlib.cm.get_cmap("rainbow")

	gresrad = 1.0		
	
	pre_g1 = Feature("pre_g1", -1, 1.5)
	pre_g2 = Feature("pre_g2", -1, 1.5)
	
	tru_g = Feature("tru_g")
	tru_e = Feature("tru_e")
	psf_g = Feature("psf_g")
	g1res = Feature("g1res", -gresrad, gresrad)
	g2res = Feature("g2res", -gresrad, gresrad)
	
	gal_e1 =  Feature("Galaxy_e1")
	gal_e2 =  Feature("Galaxy_e2")
	gal_g1 =  Feature("Galaxy_g1", -0.033, 0.033)
	gal_g2 =  Feature("Galaxy_g2")
	gal_size =  Feature("Galaxy_sigma_arcsec")
	psf_size =  Feature("tru_psf_sigma")
	
	gal_sn = Feature("Galaxy_SN")
	
	fig = plt.figure(figsize=(21, 12))
	"""
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, gal_e1, pre_g1, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)
	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.scatter.scatter(ax, cat, gal_e2, pre_g2, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)
	"""
	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.scatter.scatter(ax, cat, gal_g1, pre_g1, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)
	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.scatter.scatter(ax, cat, gal_g2, pre_g2, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)
	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.hist.hist(ax, cat, psf_g)
	
	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.hist.hist(ax, cat, psf_size)
	
	"""
	hexbinkwargs = {"mincnt":50}
	
	ax = fig.add_subplot(3, 4, 1)
	#megalut.plot.scatter.scatter(ax, cat, gal_e1, pre_g1, tru_e)
	megalut.plot.hexbin.hexbin(ax, cat, gal_e1, pre_g1, tru_e, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 2)
	#megalut.plot.scatter.scatter(ax, cat, gal_e2, pre_g2, tru_e)
	megalut.plot.hexbin.hexbin(ax, cat, gal_e2, pre_g2, tru_e, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 3)
	#megalut.plot.scatter.scatter(ax, cat, gal_g1, pre_g1, tru_e)
	megalut.plot.hexbin.hexbin(ax, cat, gal_g1, pre_g1, tru_e, **hexbinkwargs)
	
	
	ax = fig.add_subplot(3, 4, 4)
	#megalut.plot.scatter.scatter(ax, cat, gal_g2, pre_g2, tru_e)
	megalut.plot.hexbin.hexbin(ax, cat, gal_g2, pre_g2, tru_e, **hexbinkwargs)
	"""
	"""	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.hexbin.hexbin(ax, cat, gal_g1, g1res)

	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.hexbin.hexbin(ax, cat, gal_g1, g1res, gal_size, cmap=cmap)
	
	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.hexbin.hexbin(ax, cat, gal_g1, g1res, psf_size, cmap=cmap)
	"""
	
	#("in", "Galaxy_sigma_arcsec", 0.2, 0.4)("in", "Galaxy_SN", 1500, 3000)
	
	#("in", "tru_psf_sigma", 1.69, 1.71)
	s = megalut.tools.table.Selector("test",[
		("in", "psf_g", 0.0, 0.01)
		]) 
	
	selcat = s.select(cat)
	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.hist.hist(ax, selcat, psf_g)
	
	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.hist.hist(ax, selcat, psf_size)
	

	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.scatter.scatter(ax, selcat, gal_g1, pre_g1, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)
	ax = fig.add_subplot(3, 4, 8)
	megalut.plot.scatter.scatter(ax, selcat, gal_g2, pre_g2, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)
	
	
	
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

