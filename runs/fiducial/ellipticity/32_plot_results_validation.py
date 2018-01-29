import megalut
import includes
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


traindir = os.path.join(includes.workdir, "train_simple")

component = "1"
main_pred = "s{}".format(component)
main_feat = Feature("tru_{}".format(main_pred))





outdirplots = os.path.join(traindir, "plots")
if not os.path.exists(outdirplots):
	os.mkdir(outdirplots)
valprecatpath = os.path.join(traindir, "valprecat.pkl")


cat = megalut.tools.io.readpickle(valprecatpath)
print megalut.tools.table.info(cat)


cat["pre_g{}".format(component)] = cat["pre_g{}_adamom".format(component)]
#cat["pre_g1"] = cat["pre_g1_fourier"]

megalut.tools.table.addstats(cat, "pre_g{}".format(component))
megalut.tools.table.addrmsd(cat, "pre_g{}".format(component), "tru_s{}".format(component))
megalut.tools.table.addstats(cat, "snr")


cat["adamom_frac"] = np.sum(cat["adamom_g{}".format(component)].mask, axis=1)/float(cat["adamom_g{}".format(component)].shape[1])

s = megalut.tools.table.Selector("ok", [
	#("in", "snr_mean", 7, 15),
	("min", "snr_mean", 10),
	#("in", "tru_rad", 0, 8),
	("max", "adamom_frac", 0.005)
	]
	)

cat = s.select(cat)


ebarmode = "scatter"
ncbins = 10
#--------------------------------------------------------------------------------------------------
fig = plt.figure(figsize=(23, 13))



#------------------- 1st line
ax = fig.add_subplot(3, 5, 1)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_g{}_mean".format(component)), featc=Feature("snr_mean"), showidline=True)

ax = fig.add_subplot(3, 5, 2)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("snr_mean"), featc=Feature("pre_g{}_bias".format(component)))

ax = fig.add_subplot(3, 5, 3)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("tru_rad"), featc=Feature("pre_g{}_bias".format(component)))

ax = fig.add_subplot(3, 5, 4)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("tru_sersicn"), featc=Feature("pre_g{}_bias".format(component)))

ax = fig.add_subplot(3, 5, 5)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("tru_g"), featc=Feature("pre_g{}_bias".format(component)))
#------------------- 2nd line
ax = fig.add_subplot(3, 5, 6)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_g{}_bias".format(component)), featc=Feature("snr_mean"))

ax = fig.add_subplot(3, 5, 7)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_g{}_bias".format(component)), featc=Feature("tru_sb"))

ax = fig.add_subplot(3, 5, 8)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_g{}_bias".format(component)), featc=Feature("tru_rad"))

ax = fig.add_subplot(3, 5, 9)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_g{}_bias".format(component)), featc=Feature("tru_sersicn"))

ax = fig.add_subplot(3, 5, 10)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_g{}_bias".format(component)), featc=Feature("tru_g"), metrics=True, yisres=True)
#------------------- 3rd line
ax = fig.add_subplot(3, 5, 11)
megalut.plot.bin.res(ax, cat, main_feat, Feature("pre_g{}_mean".format(component)), Feature("snr_mean"), ncbins=ncbins, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 12)
megalut.plot.bin.res(ax, cat, main_feat, Feature("pre_g{}_mean".format(component)), Feature("tru_flux"), ncbins=ncbins, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 13)
megalut.plot.bin.res(ax, cat, main_feat, Feature("pre_g{}_mean".format(component)), Feature("tru_rad"), ncbins=ncbins, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 14)
megalut.plot.bin.res(ax, cat, main_feat, Feature("pre_g{}_mean".format(component)), Feature("tru_sersicn"), ncbins=ncbins, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 15)
megalut.plot.bin.res(ax, cat, main_feat, Feature("pre_g{}_mean".format(component)), Feature("tru_g"), ncbins=ncbins, equalcount=True, ebarmode=ebarmode)

plt.tight_layout()
fig.savefig(os.path.join(outdirplots, "validation_{}.png".format(main_pred)))
plt.show()
