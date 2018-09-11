import megalut
import os
import config
import numpy as np

from megalut.tools.feature import Feature

import matplotlib
import matplotlib.pyplot as plt



cat = megalut.tools.io.readpickle(os.path.join(config.simmeasdir, config.datasets["si"], "groupmeascat.pkl"))

compadir = os.path.join(config.workdir, "compa_with_nico")

nicocat = megalut.tools.io.readpickle(os.path.join(compadir, "meascat_sim_2001001_24.5_a0_m_polypsf_l3.0_bk0_0.7.pkl"))
#print megalut.tools.table.info(nicocat)
#exit()

fig = plt.figure(figsize=(20, 13))


snr = Feature("snr", 0, 50, nicename="Measured S/N")
tru_rad = Feature("tru_rad", nicename="True half-light radius [pixel]")
tru_mag = Feature("tru_mag", 20, 25, nicename="Magnitude")
tru_sersicn = Feature("tru_sersicn", 0, 7, nicename="True Sersic index")

skystd = Feature("skystd")
skymed = Feature("skymed")
skymad = Feature("skymad")

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


ax = fig.add_subplot(2, 3, 1)
megalut.plot.contour.simobs(ax, cat, nicocat, snr, adamom_flux)

ax = fig.add_subplot(2, 3, 2)
megalut.plot.contour.simobs(ax, cat, nicocat, skymad, skymed)

ax = fig.add_subplot(2, 3, 3)
megalut.plot.contour.simobs(ax, cat, nicocat, adamom_logflux, adamom_sigma)

ax = fig.add_subplot(2, 3, 4)
megalut.plot.contour.simobs(ax, cat, nicocat, adamom_g, adamom_rho4)

ax = fig.add_subplot(2, 3, 5)
megalut.plot.contour.simobs(ax, cat, nicocat, adamom_g1, adamom_g2)

ax = fig.add_subplot(2, 3, 6)

cat["x_res"] = cat["adamom_x"] - cat["x"] 
cat["y_res"] = cat["adamom_y"] - cat["y"] 
nicocat["x_res"] = nicocat["adamom_x"] - nicocat["x"] 
nicocat["y_res"] = nicocat["adamom_y"] - nicocat["y"] 
megalut.plot.contour.simobs(ax, cat, nicocat, Feature("x_res"), Feature("y_res"))


"""
ax = fig.add_subplot(2, 3, 2)
megalut.plot.scatter.scatter(ax, cat, tru_mag,  tru_rad, sidehists=True, sidehistkwargs={"bins":20})
ax = fig.add_subplot(2, 3, 3)
megalut.plot.scatter.scatter(ax, cat, tru_mag,  tru_rad, snr)


ax = fig.add_subplot(2, 3, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g1"), Feature("tru_e1"), Feature("tru_e2"))
ax.grid()
ax = fig.add_subplot(2, 3, 5)
megalut.plot.scatter.scatter(ax, cat, snr, tru_mag)
ax.grid()
ax = fig.add_subplot(2, 3, 6)
megalut.plot.hist.hist(ax, cat, snr)
"""


plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.


