import megalut
import config
import measfcts
import glob
import os
import numpy as np
import astropy

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)


#traindir = os.path.join(config.workdir, "train_Nico4nn_Sum55")
#traindir = os.path.join(config.workdir, "train_Nico4nn_2feat-multreallyfix55")
#traindir = os.path.join(config.workdir, "train_Nico4nn_3feat-sum55")
#traindir = os.path.join(config.workdir, "train_Nico4nn_2feat-sum55")
traindir = os.path.join(config.workdir, "train_Nico4nn_3feat-sum55_norm-11")


valprecatpath = os.path.join(traindir, "valprecat.pkl")






cat = megalut.tools.io.readpickle(valprecatpath)
print megalut.tools.table.info(cat)

cat["pre_g1"] = cat["pre_g1_adamom"]
megalut.tools.table.addstats(cat, "pre_g1")
megalut.tools.table.addrmsd(cat, "pre_g1", "tru_s1")
megalut.tools.table.addstats(cat, "snr")
#cat["tru_g"] = np.hypot(cat["tru_g1"], cat["tru_g2"])


# Keep only good-enough SNR ones
print min(cat["snr_mean"]), max(cat["snr_mean"]), np.median(cat["snr_mean"])

cat["adamom_frac"] = np.sum(cat["adamom_g1"].mask, axis=1)/float(cat["adamom_g1"].shape[1])

print min(cat["adamom_frac"]), max(cat["adamom_frac"]), np.median(cat["adamom_frac"])

s = megalut.tools.table.Selector("ok", [
	#("in", "snr_mean", 7, 15),
	("in", "tru_rad", 0, 11),
	("max", "adamom_frac", 0.01)]
	)

cat = s.select(cat)

print min(cat["snr_mean"]), max(cat["snr_mean"]), np.median(cat["snr_mean"])


rea = "All"
ebarmode = "scatter"

fig = plt.figure(figsize=(24, 12))



ax = fig.add_subplot(3, 5, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"),  Feature("pre_g1_mean"), featc=Feature("snr_mean"), showidline=True, metrics=True)
ax = fig.add_subplot(3, 5, 2)
#megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_g1_mean"), ebarmode=ebarmode)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("snr_mean"), Feature("pre_g1_bias"))
ax = fig.add_subplot(3, 5, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("tru_rad"), Feature("pre_g1_bias"))
ax = fig.add_subplot(3, 5, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("tru_sersicn"), Feature("pre_g1_bias"))
ax = fig.add_subplot(3, 5, 5)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("tru_g"), Feature("pre_g1_bias"))


ax = fig.add_subplot(3, 5, 6)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"),  Feature("pre_g1_bias"), featc=Feature("snr_mean"))
ax = fig.add_subplot(3, 5, 7)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"),  Feature("pre_g1_bias"), featc=Feature("adamom_frac"))
ax = fig.add_subplot(3, 5, 8)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"),  Feature("pre_g1_bias"), featc=Feature("tru_rad"))
ax = fig.add_subplot(3, 5, 9)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"),  Feature("pre_g1_bias"), featc=Feature("tru_sersicn"))
ax = fig.add_subplot(3, 5, 10)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"),  Feature("pre_g1_bias"), featc=Feature("tru_g"))


ax = fig.add_subplot(3, 5, 11)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_g1_mean"), Feature("snr_mean"), ncbins=3, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 12)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_g1_mean"), Feature("tru_flux"), ncbins=3, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 13)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_g1_mean"), Feature("tru_rad"), ncbins=3, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 14)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_g1_mean"), Feature("tru_sersicn"), ncbins=3, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 15)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_g1_mean"), Feature("tru_g"), ncbins=3, equalcount=True, ebarmode=ebarmode)


plt.tight_layout()

#if filepath:
#	plt.savefig(filepath)
#else:

plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.




#
#
##s = megalut.tools.table.Selector("LowShear", [("in", "tru_s1", -0.05, 0.05), ("in", "tru_s2", -0.05, 0.05)])
##cat = s.select(cat)
#
#print megalut.tools.table.info(cat)
#
#megalut.tools.table.addstats(cat, "pre_s1_adamom")
#megalut.tools.table.addstats(cat, "pre_s2_adamom")
##megalut.tools.table.addstats(cat, "pre_s1_fourier")
##megalut.tools.table.addstats(cat, "pre_s2_fourier")
#
#megalut.tools.table.addstats(cat, "snr")
#
#print megalut.tools.table.info(cat)
#
#
#rea = "All"
#
#adamom_flux = Feature("adamom_flux", rea=rea)
#adamom_sigma = Feature("adamom_sigma", rea=rea)
#adamom_rho4 = Feature("adamom_rho4", 1.3, 3.0, rea=rea)
#adamom_g1 = Feature("adamom_g1", -0.7, 0.7, rea=rea)
#adamom_g2 = Feature("adamom_g2", -0.7, 0.7, rea=rea)
#snr = Feature("snr", rea=rea)
#adamom_x = Feature("adamom_x", rea=rea)
#adamom_y = Feature("adamom_y", rea=rea)
#
#tru_s1 = Feature("tru_s1", rea=rea)
#tru_s2 = Feature("tru_s2", rea=rea)
#
#tru_g1 = Feature("tru_g1", rea=rea)
#tru_g2 = Feature("tru_g2", rea=rea)
#tru_rad = Feature("tru_rad", rea=rea)
#tru_sersicn = Feature("tru_sersicn", rea=rea)
#tru_flux = Feature("tru_flux", rea=rea)
#
#skymad = Feature("skymad", rea=rea)
#skystd = Feature("skystd", rea=rea)
#skymed = Feature("skymed", rea=rea)
#skymean = Feature("skymean", rea=rea)
#
#
#pre_s1_adamom = Feature("pre_s1_adamom", rea=rea)
#pre_s2_adamom = Feature("pre_s2_adamom", rea=rea)
#pre_s1_fourier = Feature("pre_s1_fourier", rea=rea)
#pre_s2_fourier = Feature("pre_s2_fourier", rea=rea)
#
#pre_s1_mean = Feature("pre_s1_adamom_mean")
#pre_s2_mean = Feature("pre_s2_adamom_mean")
#snr_mean = Feature("snr_mean")
#
#
##simcat["aperphot_sbr1"] = simcat["aperphot_sb2"] / simcat["aperphot_sb5"]
##obscat["aperphot_sbr1"] = obscat["aperphot_sb2"] / obscat["aperphot_sb5"]
##simcat["aperphot_sbr2"] = simcat["aperphot_sb3"] / simcat["aperphot_sb8"]
##obscat["aperphot_sbr2"] = obscat["aperphot_sb3"] / obscat["aperphot_sb8"]
##aperphot_sbr1 = Feature("aperphot_sbr1", rea=rea)
##aperphot_sbr2 = Feature("aperphot_sbr2", rea=rea)
#
#cat["adamom_log_flux"] = np.log10(cat["adamom_flux"])
#adamom_log_flux = Feature("adamom_log_flux", rea=rea)
#
#
#fig = plt.figure(figsize=(16, 10))
##fig = plt.figure(figsize=(8, 8))
#
#
#ax = fig.add_subplot(2, 3, 1)
#megalut.plot.bin.res(ax, cat, tru_s1, pre_s1_adamom, featc=adamom_sigma, nbins=10, ncbins=1, ebarmode="bias", showidline=True, metrics=True, equalcount=True)
#
#ax = fig.add_subplot(2, 3, 4)
#megalut.plot.bin.res(ax, cat, tru_s2, pre_s2_adamom, featc=adamom_sigma, nbins=10, ncbins=1, ebarmode="bias", showidline=True, metrics=True, equalcount=True)
#
#ax = fig.add_subplot(2, 3, 2)
#megalut.plot.bin.res(ax, cat, tru_s1, pre_s1_adamom, featc=tru_sersicn, nbins=10, ncbins=1, ebarmode="bias", showidline=True, metrics=True, equalcount=True)
#
#ax = fig.add_subplot(2, 3, 5)
#megalut.plot.bin.res(ax, cat, tru_s2, pre_s2_adamom, featc=tru_sersicn, nbins=10, ncbins=1, ebarmode="bias", showidline=True, metrics=True, equalcount=True)
#
#"""
#ax = fig.add_subplot(2, 3, 1)
#megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_mean, featc=snr_mean, showidline=True, metrics=True)
#
#ax = fig.add_subplot(2, 3, 4)
#megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_mean, featc=snr_mean, showidline=True, metrics=True)
#
#ax = fig.add_subplot(2, 3, 2)
#megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_mean, featc=tru_sersicn, showidline=True)
#
#ax = fig.add_subplot(2, 3, 5)
#megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_mean, featc=tru_sersicn, showidline=True)
#
#
#ax = fig.add_subplot(2, 3, 3)
#megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_mean, featc=tru_rad, showidline=True)
#
#ax = fig.add_subplot(2, 3, 6)
#megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_mean, featc=tru_rad, showidline=True)
#"""
#
#"""
#ax = fig.add_subplot(2, 3, 2)
#megalut.plot.scatter.scatter(ax, obscat, adamom_g1, mom_e13, showidline=True)
#
#ax = fig.add_subplot(2, 3, 3)
#megalut.plot.scatter.scatter(ax, obscat, adamom_sigma, fourier_adamom_sigma, adamom_rho4)
#
#
#ax = fig.add_subplot(2, 3, 4)
#megalut.plot.scatter.scatter(ax, obscat, adamom_g1, mom_e15, showidline=True)
#
#ax = fig.add_subplot(2, 3, 5)
#megalut.plot.scatter.scatter(ax, obscat, adamom_g1, mom_e18, showidline=True)
#
#ax = fig.add_subplot(2, 3, 6)
#megalut.plot.scatter.scatter(ax, obscat, adamom_g1, mom_e110, showidline=True)
#"""
#
#plt.tight_layout()
#
##if filepath:
##	plt.savefig(filepath)
##else:
#
#plt.show()
##plt.close(fig) # Helps releasing memory when calling in large loops.
#
