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





cat = megalut.tools.io.readpickle("/vol/fohlen11/fohlen11_1/mtewes/backgals-megalut/sim/Nico4nn/groupmeascat.pkl")
print megalut.tools.table.info(cat)


rea = "all"
rea = 0

fig = plt.figure(figsize=(16, 10))
#fig = plt.figure(figsize=(8, 8))


ax = fig.add_subplot(2, 3, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("adamom_g1", rea=rea), Feature("fourierhann_adamom_g1", rea=rea), Feature("adamom_rho4", rea=rea))
ax = fig.add_subplot(2, 3, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("adamom_g2", rea=rea), Feature("fourierhann_adamom_g2", rea=rea), Feature("adamom_sigma", rea=rea))
ax = fig.add_subplot(2, 3, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("adamom_sigma", rea=rea), Feature("fourierhann_adamom_sigma", rea=rea), Feature("adamom_rho4", rea=rea))

"""
ax = fig.add_subplot(2, 3, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_sersicn"), Feature("fourierhann_adamom_rho4", rea=rea), Feature("adamom_sigma", rea=rea))
ax = fig.add_subplot(2, 3, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_sersicn"), Feature("fourier_adamom_rho4", rea=rea), Feature("adamom_sigma", rea=rea))
ax = fig.add_subplot(2, 3, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_sersicn"), Feature("adamom_rho4", rea=rea), Feature("adamom_sigma", rea=rea))
"""


ax = fig.add_subplot(2, 3, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("adamom_rho4", rea=rea), Feature("fourierhann_adamom_rho4", rea=rea), Feature("adamom_sigma", rea=rea))
ax = fig.add_subplot(2, 3, 5)
megalut.plot.scatter.scatter(ax, cat, Feature("adamom_rho4", rea=rea), Feature("fourierhann_adamom_rho4", rea=rea), Feature("tru_sersicn"))
ax = fig.add_subplot(2, 3, 6)
megalut.plot.scatter.scatter(ax, cat, Feature("fourierhann_adamom_sigma", rea=rea), Feature("fourierhann_adamom_rho4", rea=rea), Feature("tru_sersicn"))


plt.tight_layout()

#if filepath:
#	plt.savefig(filepath)
#else:

plt.show()



exit()

rea = None

adamom_flux = Feature("adamom_flux", rea=rea)
adamom_sigma = Feature("adamom_sigma", rea=rea)
adamom_rho4 = Feature("adamom_rho4", 1.3, 3.0, rea=rea)
adamom_g1 = Feature("adamom_g1", -0.7, 0.7, rea=rea)
adamom_g2 = Feature("adamom_g2", -0.7, 0.7, rea=rea)
snr = Feature("snr", rea=rea)
adamom_x = Feature("adamom_x", rea=rea)
adamom_y = Feature("adamom_y", rea=rea)

mom_x = Feature("mom_x", rea=rea)
mom_y = Feature("mom_y", rea=rea)

mom_e23 = Feature("mom_e23", rea=rea)
mom_e25 = Feature("mom_e25", rea=rea)
mom_e210 = Feature("mom_e210", rea=rea)

mom_e13 = Feature("mom_e13", rea=rea)
mom_e15 = Feature("mom_e15", rea=rea)
mom_e18 = Feature("mom_e18", rea=rea)
mom_e110 = Feature("mom_e110", rea=rea)

fourierhann_adamom_g1 = Feature("fourierhann_adamom_g1", rea=rea)
fourier_adamom_g1 = Feature("fourier_adamom_g1", rea=rea)
fourier_adamom_sigma = Feature("fourier_adamom_sigma", rea=rea)
fourierhann_adamom_sigma = Feature("fourierhann_adamom_sigma", rea=rea)



mom_r3 = Feature("mom_r3", rea=rea)
mom_r5 = Feature("mom_r5", rea=rea)
mom_r10 = Feature("mom_r10", rea=rea)

tru_g1 = Feature("tru_g1", rea=rea)
tru_g2 = Feature("tru_g2", rea=rea)
tru_rad = Feature("tru_rad", rea=rea)
tru_sersicn = Feature("tru_sersicn", rea=rea)

#aperphot_sb2 = Feature("aperphot_sb2", rea=rea)
#aperphot_sb3 = Feature("aperphot_sb3", rea=rea)
#aperphot_sb5 = Feature("aperphot_sb5", rea=rea)
#aperphot_sb8 = Feature("aperphot_sb8", rea=rea)

skymad = Feature("skymad", rea=rea)
skystd = Feature("skystd", rea=rea)
skymed = Feature("skymed", rea=rea)
skymean = Feature("skymean", rea=rea)



#simcat["aperphot_sbr1"] = simcat["aperphot_sb2"] / simcat["aperphot_sb5"]
#obscat["aperphot_sbr1"] = obscat["aperphot_sb2"] / obscat["aperphot_sb5"]
#simcat["aperphot_sbr2"] = simcat["aperphot_sb3"] / simcat["aperphot_sb8"]
#obscat["aperphot_sbr2"] = obscat["aperphot_sb3"] / obscat["aperphot_sb8"]
#aperphot_sbr1 = Feature("aperphot_sbr1", rea=rea)
#aperphot_sbr2 = Feature("aperphot_sbr2", rea=rea)

obscat["adamom_log_flux"] = np.log10(obscat["adamom_flux"])
adamom_log_flux = Feature("adamom_log_flux", rea=rea)


fig = plt.figure(figsize=(16, 10))
#fig = plt.figure(figsize=(8, 8))

ax = fig.add_subplot(2, 3, 1)
megalut.plot.scatter.scatter(ax, obscat, adamom_g1, fourierhann_adamom_g1)

ax = fig.add_subplot(2, 3, 2)
megalut.plot.scatter.scatter(ax, obscat, adamom_g1, mom_e13, showidline=True)

ax = fig.add_subplot(2, 3, 3)
megalut.plot.scatter.scatter(ax, obscat, adamom_sigma, fourier_adamom_sigma, adamom_rho4)


ax = fig.add_subplot(2, 3, 4)
megalut.plot.scatter.scatter(ax, obscat, adamom_g1, mom_e15, showidline=True)

ax = fig.add_subplot(2, 3, 5)
megalut.plot.scatter.scatter(ax, obscat, adamom_g1, mom_e18, showidline=True)

ax = fig.add_subplot(2, 3, 6)
megalut.plot.scatter.scatter(ax, obscat, adamom_g1, mom_e110, showidline=True)


plt.tight_layout()

#if filepath:
#	plt.savefig(filepath)
#else:

plt.show()
#plt.close(fig) # Helps releasing memory when calling in large loops.

