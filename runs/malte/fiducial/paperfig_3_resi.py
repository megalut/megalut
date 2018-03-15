import config
import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker
import matplotlib

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt
plt.rc('text', usetex=True)

import logging
logger = logging.getLogger(__name__)

#megalut.plot.figures.set_fancy(14)
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)



valcat = os.path.join(config.valdir, config.valname + ".pkl")
cat = megalut.tools.io.readpickle(valcat)

#print megalut.tools.table.info(cat)



cat = megalut.tools.table.shuffle(cat) # otherwise scatter plots look weird as they got sorted by tru s1 s2

megalut.tools.table.addstats(cat, "snr")


select = True
if select:
	
	s = megalut.tools.table.Selector("snr_mean > 10", [
		("min", "snr_mean", 10.0),
	])
	cat = s.select(cat)


tru_sb = Feature("tru_sb", 0, 16, nicename=r"Surface brightness $S$ [pix$^{-2}$]")
tru_rad = Feature("tru_rad", 1.5, 8.5, nicename=r"Half-light radius $R$ [pix]")

snr_mean = Feature("snr_mean", nicename="$\\langle \mathrm{S}/\mathrm{N}\\rangle$")

#for comp in ["1","2"]:
for comp in ["1"]:

	
	megalut.tools.table.addrmsd(cat, "pre_s{}".format(comp), "tru_s{}".format(comp))
	megalut.tools.table.addstats(cat, "pre_s{}".format(comp))
	
	cat["abs_pre_s{}_bias".format(comp)] = np.fabs(cat["pre_s{}_bias".format(comp)])
	cat["log_abs_pre_s{}_bias".format(comp)] = np.log10(np.fabs(cat["pre_s{}_bias".format(comp)]))
	
	max_bias = np.max(cat["abs_pre_s{}_bias".format(comp)])
	hard_coded_max_bias = max_bias # 0.02
	
	# latex and format are ugly to mix, doing it manually:
	if comp == "1":
		tru_s = Feature("tru_s{}".format(comp), -0.12, 0.12, nicename=r"$g_1^{\mathrm{true}}$")
		pre_s_mean = Feature("pre_s{}_mean".format(comp), nicename=r"Estimated $\hat{g}_{1}$ (average over realizations)")
		pre_s_bias = Feature("pre_s{}_bias".format(comp), -hard_coded_max_bias, hard_coded_max_bias, nicename=r"$\langle \hat{g}_{1} \rangle - g_{1}^{\mathrm{true}} $")
		abs_pre_s_bias = Feature("abs_pre_s{}_bias".format(comp), 0, hard_coded_max_bias, nicename=r"$|\langle \hat{g}_{1} \rangle - g_{1}^{\mathrm{true}}|$ ")
		log_abs_pre_s_bias = Feature("log_abs_pre_s{}_bias".format(comp), nicename=r"$\log(|g_1|$ estimation error)")
	if comp == "2":
		tru_s = Feature("tru_s{}".format(comp), -0.12, 0.12, nicename=r"$g_2^{\mathrm{true}}$")
		pre_s_mean = Feature("pre_s{}_mean".format(comp), nicename=r"Estimated $\hat{g}_{2}$ (average over realizations)")
		pre_s_bias = Feature("pre_s{}_bias".format(comp), -hard_coded_max_bias, hard_coded_max_bias, nicename=r"$\langle \hat{g}_{2} \rangle - g_{2}^{\mathrm{true}} $")
		abs_pre_s_bias = Feature("abs_pre_s{}_bias".format(comp), 0, hard_coded_max_bias, nicename=r"$|\langle \hat{g}_{2} \rangle - g_{2}^{\mathrm{true}} |$ ")
		log_abs_pre_s_bias = Feature("log_abs_pre_s{}_bias".format(comp), nicename=r"$\log(|g_2|$ estimation error)")
	
	fig = plt.figure(figsize=(11.5, 3.0))


	
	ax = fig.add_subplot(1, 3, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_s,  pre_s_bias, featc=snr_mean, cmap="plasma_r", s=10)
	ax.axhline(color="black", lw=0.5)
	
	ax = fig.add_subplot(1, 3, 2)
	cnorm = matplotlib.colors.SymLogNorm(linthresh=0.005)
	megalut.plot.scatter.scatter(ax, cat, tru_s, tru_rad, featc=pre_s_bias, cmap="coolwarm", norm=cnorm, s=10)
	
	"""
	ax = fig.add_subplot(1, 3, 3)
	cnorm = matplotlib.colors.SymLogNorm(linthresh=0.001)
	megalut.plot.scatter.scatter(ax, cat, tru_sb, tru_rad, featc=pre_s_bias, cmap="coolwarm")
	"""
	
	ax = fig.add_subplot(1, 3, 3)
	megalut.plot.scatter.scatter(ax, cat, tru_sb, tru_rad, featc=abs_pre_s_bias, cmap="plasma_r", s=10)

	
	plt.tight_layout()


	megalut.plot.figures.savefig(os.path.join(config.valdir, config.valname + "_resi_{}".format(comp)), fig, fancy=True, pdf_transparence=True)
	plt.show()

