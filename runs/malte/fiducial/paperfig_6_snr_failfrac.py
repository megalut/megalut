import config
import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.colors
import matplotlib

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt
plt.rc('text', usetex=True)

import logging
logger = logging.getLogger(__name__)


megalut.plot.figures.set_fancy(14)


valcat = os.path.join(config.simmeasdir, config.datasets["vs"], "groupmeascat.pkl")
cat = megalut.tools.io.readpickle(valcat)

#print megalut.tools.table.info(cat)

megalut.tools.table.addstats(cat, "snr")

cat["adamom_goodfrac"] = 1.0 - cat["adamom_failfrac"]


tru_sb = Feature("tru_sb", 0, 16, nicename=r"Surface brightness $S$ [pix$^{-2}$]")
tru_rad = Feature("tru_rad", 1, 9, nicename=r"Half-light radius $R$ [pix]")

snr_mean = Feature("snr_mean", nicename="$\\langle \mathrm{S}/\mathrm{N}\\rangle$")

successfrac = Feature("adamom_goodfrac", nicename="Measurement success fraction")

for comp in ["1"]:

	
	fig = plt.figure(figsize=(5, 9))

	ax = fig.add_subplot(2, 1, 1)
	cb = megalut.plot.scatter.scatter(ax, cat, tru_sb, tru_rad, featc=snr_mean, cmap="plasma_r", norm=matplotlib.colors.PowerNorm(gamma=1./2.))
	
	cb.set_ticks([2, 5, 10, 20, 30, 40, 50, 60])
	
	ax = fig.add_subplot(2, 1, 2)
	megalut.plot.scatter.scatter(ax, cat, tru_sb,  tru_rad, featc=successfrac, cmap="plasma_r")
	ax.axhline()
	

	
	plt.tight_layout()


	megalut.plot.figures.savefig(os.path.join(config.valdir, config.datasets["vs"] + "_snr"), fig, fancy=True, pdf_transparence=True)
	plt.show()

