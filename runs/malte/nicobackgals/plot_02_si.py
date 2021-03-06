import megalut
import os
import config
import numpy as np

from megalut.tools.feature import Feature

import matplotlib
import matplotlib.pyplot as plt



cat = megalut.tools.io.readpickle(os.path.join(config.simmeasdir, config.datasets["si"], "groupmeascat.pkl"))
#megalut.tools.table.addstats(cat, "snr")

#print megalut.tools.table.info(cat)
#exit()

fig = plt.figure(figsize=(20, 13))

snr_mean = Feature("snr_mean", nicename="$\\langle \mathrm{S}/\mathrm{N}\\rangle$")

snr = Feature("snr", 0, 50, nicename="Measured S/N")
tru_rad = Feature("tru_rad", nicename="True half-light radius [pixel]")
tru_sb = Feature("tru_sb")

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


ax = fig.add_subplot(2, 3, 1)
megalut.plot.scatter.scatter(ax, cat, tru_rad,  tru_sersicn, sidehists=True, sidehistkwargs={"bins":20})

ax = fig.add_subplot(2, 3, 2)
megalut.plot.scatter.scatter(ax, cat, tru_sb,  tru_rad, snr)


plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.


