import matplotlib
#matplotlib.use('Agg')

import megalut.plot
from megalut.plot.feature import Feature

import numpy as np
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)


def meascheck(cat, filepath=None, prefix="adamom_", g12_low=None, g12_high=None):
	"""
	Plots measured things against the SBE truth, to get a first idea and check conventions.
	"""
	snr = Feature("sewpy_snr")
	
	cat["astromerrx"] = cat["x"] - cat[prefix+"x"]
	cat["astromerry"] = cat["y"] - cat[prefix+"y"]
	cat["sewpyastromerrx"] = cat["x"] - cat["sewpy_XWIN_IMAGE"]
	cat["sewpyastromerry"] = cat["y"] - cat["sewpy_YWIN_IMAGE"]

	r_astromerr = 0.5
	astromerrx = Feature("astromerrx", -r_astromerr, r_astromerr, "X adamom astrom error [pix]")
	astromerry = Feature("astromerry", -r_astromerr, r_astromerr, "Y adamom astrom error [pix]")
	sewpyastromerrx = Feature("sewpyastromerrx", -r_astromerr, r_astromerr, "X sewpy astrom error [pix]")
	sewpyastromerry = Feature("sewpyastromerry", -r_astromerr, r_astromerr, "Y sewpy astrom error [pix]")
	
	skystd = Feature("skystd", 0, 10)
	skymed = Feature("skymed", -2.0, 2.0)
	
	
	PSF_sigma_arcsec = Feature("PSF_sigma_arcsec")
	PSF_e1 = Feature("PSF_e1", -0.1, 0.1)
	PSF_e2 = Feature("PSF_e2", -0.1, 0.1)
	
	Galaxy_sigma_arcsec = Feature("Galaxy_sigma_arcsec")
	Galaxy_SN = Feature("Galaxy_SN")
	cat["Galaxy_SN_k"] = cat["Galaxy_SN"] / 1000.0
	Galaxy_SN_k = Feature("Galaxy_SN_k", None, None, "Galaxy_SN / 1000")
	
	Galaxy_e1 = Feature("Galaxy_e1")
	Galaxy_e2 = Feature("Galaxy_e2")
	Galaxy_g1 = Feature("Galaxy_g1")
	Galaxy_g2 = Feature("Galaxy_g2")
	
	adamom_g1 = Feature(prefix+"g1", g12_low, g12_high)
	adamom_g2 = Feature(prefix+"g2", g12_low, g12_high)
	adamom_sigma = Feature(prefix+"sigma")
	
	Sky_level_subtracted = Feature("Sky_level_subtracted")
	Read_noise = Feature("Read_noise")
	Gain = Feature("Gain")
	
	#print cat.colnames
	
	fig = plt.figure(figsize=(20, 13))

	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, astromerrx, astromerry, snr)

	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.scatter.scatter(ax, cat, sewpyastromerrx, sewpyastromerry, snr)

	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.scatter.scatter(ax, cat, skymed, skystd, sidehists=True)
	
	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.scatter.scatter(ax, cat, PSF_e1, PSF_e2, sidehists=True)
	
	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.hist.hist(ax, cat, PSF_sigma_arcsec)
	
	
	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.scatter.scatter(ax, cat, Galaxy_sigma_arcsec, adamom_sigma, sidehists=True)
	
	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.scatter.scatter(ax, cat, Galaxy_e1, adamom_g1, sidehists=True, show_id_line=True, idlinekwargs={"color":"red"})
	
	ax = fig.add_subplot(3, 4, 8)
	megalut.plot.scatter.scatter(ax, cat, Galaxy_e2, adamom_g2, sidehists=True, show_id_line=True, idlinekwargs={"color":"red"})
	
	ax = fig.add_subplot(3, 4, 9)
	megalut.plot.scatter.scatter(ax, cat, Galaxy_SN_k, snr, sidehists=True)
	
	ax = fig.add_subplot(3, 4, 10)
	megalut.plot.hist.hist(ax, cat, Sky_level_subtracted)
	
	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.scatter.scatter(ax, cat, Galaxy_g1, Galaxy_g2, sidehists=True)

	ax = fig.add_subplot(3, 4, 12)
	megalut.plot.scatter.scatter(ax, cat, Read_noise, Gain, sidehists=True)
	
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.


def snr(cat, filepath=None):
	"""
	Quick check of SNR
	"""
	print cat.colnames
	#exit()
	
	tru_flux = Feature("tru_flux")
	snr = Feature("sewpy_snr")
	sewpy_flux_auto = Feature("sewpy_FLUX_AUTO")
	sewpy_flux_win = Feature("sewpy_FLUX_WIN")
	adamom_flux = Feature("adamom_flux")

	sewpy_flux_50 = Feature("sewpy_FLUX_APER_1")
	sewpy_fluxerr_50 = Feature("sewpy_FLUXERR_APER_1")
	
	cat["snr50"] = cat["sewpy_FLUX_APER_1"] / cat["sewpy_FLUXERR_APER_1"]
	snr50 = Feature("snr50")


	Galaxy_SN = Feature("Galaxy_SN")
	Galaxy_shape_1 = Feature("Galaxy_shape_1")
	Galaxy_shape_2 = Feature("Galaxy_shape_2")

	skymed = Feature("skymed")
	skymean = Feature("skymean")
	skystampsum = Feature("skystampsum")

	
	Sky_level_subtracted = Feature("Sky_level_subtracted")
	Read_noise = Feature("Read_noise")
	Gain = Feature("Gain")
	
	#print cat.colnames
	
	fig = plt.figure(figsize=(18, 10))

	ax = fig.add_subplot(2, 3, 1)
	megalut.plot.scatter.scatter(ax, cat, adamom_flux, sewpy_flux_auto, show_id_line=True)

	ax = fig.add_subplot(2, 3, 2)
	megalut.plot.scatter.scatter(ax, cat, adamom_flux, sewpy_flux_50, show_id_line=True)

	ax = fig.add_subplot(2, 3, 3)
	megalut.plot.scatter.scatter(ax, cat, adamom_flux, skystampsum, show_id_line=True)
	
	ax = fig.add_subplot(2, 3, 4)
	megalut.plot.scatter.scatter(ax, cat, adamom_flux, sewpy_flux_win, show_id_line=True)
	
	#ax = fig.add_subplot(2, 3, 5)
	#megalut.plot.scatter.scatter(ax, cat, tru_flux, sewpy_flux_auto , show_id_line=True)
	
	#ax = fig.add_subplot(2, 3, 6)
	#megalut.plot.scatter.scatter(ax, cat, tru_flux, adamom_flux , show_id_line=True)
	
	
	
	#ax = fig.add_subplot(2, 3, 6)
	#megalut.plot.scatter.scatter(ax, cat, skymean, skymed, show_id_line=True)
	
	
	
	
	#ax = fig.add_subplot(2, 3, 4)
	#megalut.plot.scatter.scatter(ax, cat, snr50, snr, show_id_line=True, sidehists=True)
	
	#ax = fig.add_subplot(2, 3, 5)
	#megalut.plot.hexbin.hexbin(ax, cat, Galaxy_SN, snr)

	#ax = fig.add_subplot(2, 3, 6)
	#megalut.plot.scatter.scatter(ax, cat, skymean, skymed, show_id_line=True)
	

	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.




def simobscompa(simcat, obscat, prefix="adamom_", filepath=None):

	"""
	A classic, in feature space
	"""
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
	
	
	snr =Feature("sewpy_snr")
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





def predscatter(cat, filepath=None):
	"""
	First plain old scatter plot of predictions against truth
	"""
	rg = 0.8
	
	tru_g1 = Feature("tru_g1", -rg, rg)
	tru_g2 = Feature("tru_g2", -rg, rg)
	tru_sigma = Feature("tru_sigma")
	tru_flux = Feature("tru_flux")
	
	pre_g1 = Feature("pre_g1", -rg, rg)
	pre_g2 = Feature("pre_g2", -rg, rg)
	pre_sigma = Feature("pre_sigma")
	pre_flux = Feature("pre_flux")
	
	snr =Feature("sewpy_snr_mean")
	
	fig = plt.figure(figsize=(22, 13))
	
	ax = fig.add_subplot(3, 4, 1)	
	megalut.plot.scatter.scatter(ax, cat, tru_g1, pre_g1, show_id_line=True, idlinekwargs={"color":"red", "lw":2}, sidehists=True, ms=3)
		
	ax = fig.add_subplot(3, 4, 2)	
	megalut.plot.scatter.scatter(ax, cat, tru_g2, pre_g2, show_id_line=True, idlinekwargs={"color":"red", "lw":2}, sidehists=True, ms=3)
		
	ax = fig.add_subplot(3, 4, 3)	
	megalut.plot.scatter.scatter(ax, cat, tru_sigma, pre_sigma, show_id_line=True, idlinekwargs={"color":"red", "lw":2}, sidehists=True, ms=3)

	ax = fig.add_subplot(3, 4, 4)	
	megalut.plot.scatter.scatter(ax, cat, tru_flux, pre_flux, show_id_line=True, idlinekwargs={"color":"red", "lw":2}, sidehists=True, ms=3)

	ax = fig.add_subplot(3, 4, 5)	
	megalut.plot.scatter.scatter(ax, cat, tru_g1, pre_g1, snr, s=5, metrics=True)
		
	ax = fig.add_subplot(3, 4, 6)	
	megalut.plot.scatter.scatter(ax, cat, tru_g2, pre_g2, snr, s=5, metrics=True)
		
	ax = fig.add_subplot(3, 4, 7)	
	megalut.plot.scatter.scatter(ax, cat, tru_sigma, pre_sigma, snr, s=5, metrics=True)

	ax = fig.add_subplot(3, 4, 8)	
	megalut.plot.scatter.scatter(ax, cat, tru_flux, pre_flux, snr, s=5, metrics=True)

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















def test(cat, filepath=None):
	
	
	Galaxy_e1 = Feature("Galaxy_e1")
	Galaxy_e2 = Feature("Galaxy_e2")
	
	fig = plt.figure(figsize=(6, 6))

	ax = fig.add_subplot(2, 2, 1)
	megalut.plot.scatter.scatter(ax, cat, Galaxy_e1, Galaxy_e2, sidehists=True)

	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.
