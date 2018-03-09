import config
import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)



from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)



valcat = os.path.join(config.valdir, config.valname + ".pkl")
cat = megalut.tools.io.readpickle(valcat)

widescale=False
showlegend=False
if "sum55" in config.valname:
	text = "Ignoring the variability of the PSF"
	showlegend=True
	widescale=True
if "sum77" in config.valname:
	text = "Using field coordinates as features"
if "sum88" in config.valname:
	text = "Using PSF moments as features"


if widescale:
	lim = 1e0
else:
	lim = 1e-1

select = True
if select:
	megalut.tools.table.addstats(cat, "snr")
	s = megalut.tools.table.Selector("snr_mean > 10", [
		("min", "snr_mean", 10.0),
	])
	cat = s.select(cat)
#exit()

"""
for comp in ["1","2"]:

	# If no weights are in the catalog (or not yet), we add ones
	if not "pre_s{}w".format(comp) in cat.colnames:
		
		# First putting all weights to 1.0:
		cat["pre_s{}w".format(comp)] = np.ones(cat["adamom_g1"].shape)
		
	cat["pre_s{}w_norm".format(comp)] = cat["pre_s{}w".format(comp)] / np.max(cat["pre_s{}w".format(comp)])

	megalut.tools.table.addrmsd(cat, "pre_s{}".format(comp), "tru_s{}".format(comp))
	megalut.tools.table.addstats(cat, "pre_s{}".format(comp), "pre_s{}w".format(comp))
	cat["pre_s{}_wbias".format(comp)] = cat["pre_s{}_wmean".format(comp)] - cat["tru_s{}".format(comp)]
"""



fwhmpersigma = 2.3548
cat["tru_psf_fwhm"] = cat["tru_psf_sigma"] * fwhmpersigma

tru_psf_g1 = Feature("tru_psf_g1", -0.27, 0.27, nicename=r"PSF $\varepsilon_1$")
tru_psf_g2 = Feature("tru_psf_g2", -0.02, 0.27, nicename=r"PSF $\varepsilon_2$")
tru_psf_fwhm = Feature("tru_psf_fwhm", 4.1, 5.35, nicename=r"PSF FWHM [pix]")


def make_plot(ax, featbin, showlegend=False):
	ax.axhline(0.0, color='gray', lw=0.5)	
	megalut.plot.mcbin.mcbin(ax, cat, Feature("tru_s1"), Feature("pre_s1", rea="all"), featbin, comp=1)
	megalut.plot.mcbin.mcbin(ax, cat, Feature("tru_s2"), Feature("pre_s2", rea="all"), featbin, comp=2, showbins=False, showlegend=showlegend)
	megalut.plot.mcbin.make_symlog(ax, featbin, lim=lim)
	ax.set_xlabel(featbin.nicename)


fig = plt.figure(figsize=(10, 3.0))
plt.subplots_adjust(
	left  = 0.08,  # the left side of the subplots of the figure
	right = 0.99,    # the right side of the subplots of the figure
	bottom = 0.15,   # the bottom of the subplots of the figure
	top = 0.86,      # the top of the subplots of the figure
	wspace = 0.08,   # the amount of width reserved for blank space between subplots,
	                # expressed as a fraction of the average axis width
	hspace = 0.2,   # the amount of height reserved for white space between subplots,
					# expressed as a fraction of the average axis heightbottom=0.1, right=0.8, top=0.9)
	)

ax = plt.subplot(1, 3, 1)
make_plot(ax, tru_psf_g1)
ax.set_ylabel("Metric value")

ax = plt.subplot(1, 3, 2)
make_plot(ax, tru_psf_g2)
ax.set_yticklabels([])

ax = plt.subplot(1, 3, 3)
make_plot(ax, tru_psf_fwhm, showlegend=showlegend)
ax.set_yticklabels([])



fig.text(.005, .94, text, fontdict={"fontsize":12})

megalut.plot.figures.savefig(os.path.join(config.valdir, config.valname + "_psf_biases"), fig, fancy=True)

plt.show()

