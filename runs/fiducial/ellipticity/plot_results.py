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

main_pred = "g1"
main_feat = Feature("tru_{}".format(main_pred))





outdirplots = os.path.join(traindir, "plots")
if not os.path.exists(outdirplots):
	os.mkdir(outdirplots)
valprecatpath = os.path.join(traindir, "selfprecat.pkl")





cat = megalut.tools.io.readpickle(valprecatpath)
print megalut.tools.table.info(cat)

cat["pre_{}".format(main_pred)] = cat["pre_{}_adamom".format(main_pred)]
megalut.tools.table.addstats(cat, "pre_{}".format(main_pred))
megalut.tools.table.addrmsd(cat, "pre_{}".format(main_pred), "tru_{}".format(main_pred))
megalut.tools.table.addstats(cat, "snr")


ebarmode = "scatter"
#--------------------------------------------------------------------------------------------------
fig = plt.figure(figsize=(23, 13))



#------------------- 1st line
ax = fig.add_subplot(3, 5, 1)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_{}_mean".format(main_pred)), featc=Feature("snr_mean"), showidline=True)

ax = fig.add_subplot(3, 5, 2)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("snr_mean"), featc=Feature("pre_{}_bias".format(main_pred)))

ax = fig.add_subplot(3, 5, 3)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("tru_rad"), featc=Feature("pre_{}_bias".format(main_pred)))

ax = fig.add_subplot(3, 5, 4)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("tru_sersicn"), featc=Feature("pre_{}_bias".format(main_pred)))

ax = fig.add_subplot(3, 5, 5)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("tru_g"), featc=Feature("pre_{}_bias".format(main_pred)))
#------------------- 2nd line
ax = fig.add_subplot(3, 5, 6)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_{}_bias".format(main_pred)), featc=Feature("snr_mean"))

ax = fig.add_subplot(3, 5, 7)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_{}_bias".format(main_pred)), featc=Feature("tru_sb"))

ax = fig.add_subplot(3, 5, 8)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_{}_bias".format(main_pred)), featc=Feature("tru_rad"))

ax = fig.add_subplot(3, 5, 9)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_{}_bias".format(main_pred)), featc=Feature("tru_sersicn"))

ax = fig.add_subplot(3, 5, 10)
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_{}_bias".format(main_pred)), featc=Feature("tru_g"))
#------------------- 3rd line
ax = fig.add_subplot(3, 5, 11)
megalut.plot.bin.res(ax, cat, main_feat, Feature("pre_{}_mean".format(main_pred)), Feature("snr_mean"), ncbins=3, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 12)
megalut.plot.bin.res(ax, cat, main_feat, Feature("pre_{}_mean".format(main_pred)), Feature("tru_flux"), ncbins=3, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 13)
megalut.plot.bin.res(ax, cat, main_feat, Feature("pre_{}_mean".format(main_pred)), Feature("tru_rad"), ncbins=3, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 14)
megalut.plot.bin.res(ax, cat, main_feat, Feature("pre_{}_mean".format(main_pred)), Feature("tru_sersicn"), ncbins=3, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 15)
megalut.plot.bin.res(ax, cat, main_feat, Feature("pre_{}_mean".format(main_pred)), Feature("tru_g"), ncbins=3, equalcount=True, ebarmode=ebarmode)

plt.tight_layout()
fig.savefig(os.path.join(outdirplots, "validation_{}.png".format(main_pred)))
plt.show()