
import megalut.plot
from megalut.plot.feature import Feature

import numpy as np
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)


def meascheck(cat, filepath=None):
	
	snr = megalut.plot.feature.Feature("sewpy_snr")
	
	cat["astromerrx"] = cat["x"] - cat["adamom_x"]
	cat["astromerry"] = cat["y"] - cat["adamom_y"]
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
	
	adamom_g1 = Feature("adamom_g1")
	adamom_g2 = Feature("adamom_g2")
	adamom_sigma = Feature("adamom_sigma")
	
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
