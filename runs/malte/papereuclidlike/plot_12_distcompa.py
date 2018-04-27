import megalut
import os
import config
import numpy as np

from megalut.tools.feature import Feature

import matplotlib
import matplotlib.pyplot as plt


#####

catgems = megalut.tools.io.readpickle(os.path.join(config.simmeasdir, "si-1-gems", "groupmeascat.pkl"))
catuni = megalut.tools.io.readpickle(os.path.join(config.simmeasdir, "si-1-uni", "groupmeascat.pkl"))



#####


fig = plt.figure(figsize=(12, 12))


snr = Feature("snr", 0, 50, nicename="Measured S/N")
tru_rad = Feature("tru_rad", nicename="True half-light radius [pixel]")
tru_mag = Feature("tru_mag", 20, 25, nicename="Magnitude")
tru_sersicn = Feature("tru_sersicn", 0, 7, nicename="True Sersic index")

skystd = Feature("skystd")
skymed = Feature("skymed")
adamom_flux = Feature("adamom_flux")
adamom_logflux = Feature("adamom_logflux")
adamom_sigma = Feature("adamom_sigma")
adamom_g1 = Feature("adamom_g1")
adamom_g2 = Feature("adamom_g2")
adamom_g = Feature("adamom_g")
adamom_rho4 = Feature("adamom_rho4")



#snr = Feature("snr", nicename="Measured S/N")
#tru_rad = Feature("tru_rad", nicename="True half-light radius [pixel]")
#tru_mag = Feature("tru_mag", nicename="Magnitude")
#tru_sersicn = Feature("tru_sersicn", nicename="True Sersic index")


ax = fig.add_subplot(3, 3, 1)
megalut.plot.contour.simobs(ax, catgems, catuni, snr, adamom_logflux)

ax = fig.add_subplot(3, 3, 2)
megalut.plot.contour.simobs(ax, catgems, catuni, skystd, skymed)

ax = fig.add_subplot(3, 3, 3)
megalut.plot.contour.simobs(ax, catgems, catuni, adamom_logflux, adamom_sigma)

ax = fig.add_subplot(3, 3, 4)
megalut.plot.contour.simobs(ax, catgems, catuni, adamom_g, adamom_rho4)

ax = fig.add_subplot(3, 3, 5)
megalut.plot.contour.simobs(ax, catgems, catuni, adamom_g1, adamom_g2)


ax = fig.add_subplot(3, 3, 7)
megalut.plot.hist.hist(ax, catgems, tru_rad)
megalut.plot.hist.hist(ax, catuni, tru_rad, color="green")

ax = fig.add_subplot(3, 3, 8)
megalut.plot.hist.hist(ax, catgems, adamom_sigma)
megalut.plot.hist.hist(ax, catuni, adamom_sigma, color="green")


plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.


