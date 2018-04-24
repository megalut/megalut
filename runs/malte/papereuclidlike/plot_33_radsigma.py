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


tru_rad = Feature("tru_rad", -1, 13, nicename=r"Half-light radius $R$ [pix]")

tru_rad_zoom = Feature("tru_rad", 0, 5, nicename=r"Half-light radius $R$ [pix]")

adamom_sigma = Feature("adamom_sigma", 0, 5, rea=1, nicename=r"adamom\_sigma")

snr_mean = Feature("snr_mean", nicename="$\\langle \mathrm{S}/\mathrm{N}\\rangle$")

#for comp in ["1","2"]:
for comp in ["1"]:

	
	megalut.tools.table.addrmsd(cat, "pre_s{}".format(comp), "tru_s{}".format(comp))
	megalut.tools.table.addstats(cat, "pre_s{}".format(comp))
	
	cat["abs_pre_s{}_bias".format(comp)] = np.fabs(cat["pre_s{}_bias".format(comp)])
	cat["log_abs_pre_s{}_bias".format(comp)] = np.log10(np.fabs(cat["pre_s{}_bias".format(comp)]))
	
	
	s_high = megalut.tools.table.Selector("snr_mean > 10", [
		("min", "snr_mean", 10.0),
	])
	
	s_low = megalut.tools.table.Selector("snr_mean < 10", [
		("max", "snr_mean", 10.0),
	])
	
	cat_high = s_high.select(cat)
	cat_low = s_low.select(cat)
	
	
	max_bias = np.max(cat["abs_pre_s{}_bias".format(comp)])
	hard_coded_max_bias = max_bias # 0.02
	
	max_bias_high = np.max(cat_high["abs_pre_s{}_bias".format(comp)])
	hard_coded_max_bias_high = 0.008
	max_bias_low = np.max(cat_low["abs_pre_s{}_bias".format(comp)])
	hard_coded_max_bias_low = max_bias_low # 0.02
	
	
	
	# latex and format are ugly to mix, doing it manually:
	if comp == "1":
		tru_s = Feature("tru_s{}".format(comp), -0.12, 0.12, nicename=r"$g_1^{\mathrm{true}}$")
		pre_s_mean = Feature("pre_s{}_mean".format(comp), nicename=r"Estimated $\hat{g}_{1}$ (average over realizations)")
		pre_s_bias = Feature("pre_s{}_bias".format(comp), -max_bias, max_bias, nicename=r"$\langle \hat{g}_{1} \rangle - g_{1}^{\mathrm{true}} $")
		pre_s_bias_fix = Feature("pre_s{}_bias".format(comp), -hard_coded_max_bias_high, hard_coded_max_bias_high, nicename=r"$\langle \hat{g}_{1} \rangle - g_{1}^{\mathrm{true}} $")
		abs_pre_s_bias = Feature("abs_pre_s{}_bias".format(comp), 1e-4, 1e-1, nicename=r"$|\langle \hat{g}_{1} \rangle - g_{1}^{\mathrm{true}}|$ ")
		#log_abs_pre_s_bias = Feature("log_abs_pre_s{}_bias".format(comp), nicename=r"$\log(|g_1|$ estimation error)")
		
	if comp == "2":
		tru_s = Feature("tru_s{}".format(comp), -0.12, 0.12, nicename=r"$g_2^{\mathrm{true}}$")
		pre_s_mean = Feature("pre_s{}_mean".format(comp), nicename=r"Estimated $\hat{g}_{2}$ (average over realizations)")
		pre_s_bias = Feature("pre_s{}_bias".format(comp), -max_bias_high, max_bias_high, nicename=r"$\langle \hat{g}_{2} \rangle - g_{2}^{\mathrm{true}} $")
		pre_s_bias_fix = Feature("pre_s{}_bias".format(comp), -hard_coded_max_bias_high, hard_coded_max_bias_high, nicename=r"$\langle \hat{g}_{2} \rangle - g_{2}^{\mathrm{true}} $")
		abs_pre_s_bias = Feature("abs_pre_s{}_bias".format(comp), 1e-4, 1e-1, nicename=r"$|\langle \hat{g}_{2} \rangle - g_{2}^{\mathrm{true}} |$ ")
		#log_abs_pre_s_bias = Feature("log_abs_pre_s{}_bias".format(comp), nicename=r"$\log(|g_2|$ estimation error)")
	
		


	#fig = plt.figure(figsize=(11.5, 3.0))
	fig = plt.figure(figsize=(9.0, 3.5))
	plt.subplots_adjust(
		left  = 0.09,  # the left side of the subplots of the figure
		right = 0.9,    # the right side of the subplots of the figure
		bottom = 0.15,   # the bottom of the subplots of the figure
		top = 0.95,      # the top of the subplots of the figure
		wspace = 0.7,   # the amount of width reserved for blank space between subplots,
	                # expressed as a fraction of the average axis width
		hspace = 0.3,   # the amount of height reserved for white space between subplots,
					# expressed as a fraction of the average axis heightbottom=0.1, right=0.8, top=0.9)
		)


	rasterized=True

	
	ax = fig.add_subplot(1, 2, 1)
	cnorm = matplotlib.colors.SymLogNorm(linthresh=0.005)
	megalut.plot.scatter.scatter(ax, cat_high, tru_s, tru_rad, featc=pre_s_bias_fix, cmap="coolwarm", norm=cnorm, s=10, rasterized=rasterized)
	ax.text(0.1, 0.87, r"$\langle \mathrm{S}/\mathrm{N} \rangle > 10$", verticalalignment='center', transform=ax.transAxes)
	
	
	
	ax = fig.add_subplot(1, 2, 2)
	cnorm = matplotlib.colors.LogNorm(vmin=1e-4, vmax=1e-1, clip=True)
	megalut.plot.scatter.scatter(ax, cat_high, adamom_sigma, tru_rad_zoom, featc=abs_pre_s_bias, cmap="plasma_r", s=10, norm=cnorm, rasterized=rasterized)
	ax.text(0.1, 0.87, r"$\langle \mathrm{S}/\mathrm{N} \rangle > 10$", verticalalignment='center', transform=ax.transAxes)
	
	


	megalut.plot.figures.savefig(os.path.join(config.valdir, config.valname + "_radsigma_{}".format(comp)), fig, fancy=True, pdf_transparence=True)
	plt.show()

