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


#traindir = os.path.join(config.workdir, "train_Nico4nn_Sum55")
#traindir = os.path.join(config.workdir, "train_Nico4nn_2feat-multreallyfix55")
#traindir = os.path.join(config.workdir, "train_Nico4nn_3feat-sum55")
#traindir = os.path.join(config.workdir, "train_Nico4nn_2feat-sum55")
#traindir = os.path.join(config.workdir, "train_Nico4nn_3feat-sum55_norm-11")
#traindir = os.path.join(config.workdir, "train_Nico4nn_3featfou-sum55")

traindir = os.path.join(config.workdir, "train_Nico4nn_3featg1g2-sum55")

#valprecatpath = os.path.join(traindir, "valprecat_lowSN.pkl")
valprecatpath = os.path.join(traindir, "valprecat.pkl")






cat = megalut.tools.io.readpickle(valprecatpath)
print megalut.tools.table.info(cat)



cat["pre_g1"] = cat["pre_g1_adamom"]
cat["pre_g2"] = cat["pre_g2_adamom"]


cat["tru_s1"] = cat["tru_s2"]
cat["pre_g1"] = cat["pre_g2"] 

#cat["pre_g1"] = cat["pre_g1_fourier"]


megalut.tools.table.addstats(cat, "pre_g1")
megalut.tools.table.addrmsd(cat, "pre_g1", "tru_s1")
megalut.tools.table.addstats(cat, "snr")
#cat["tru_g"] = np.hypot(cat["tru_g1"], cat["tru_g2"])


# Keep only good-enough SNR ones
print min(cat["snr_mean"]), max(cat["snr_mean"]), np.median(cat["snr_mean"])

cat["adamom_frac"] = np.sum(cat["adamom_g1"].mask, axis=1)/float(cat["adamom_g1"].shape[1])

print min(cat["adamom_frac"]), max(cat["adamom_frac"]), np.median(cat["adamom_frac"])

s = megalut.tools.table.Selector("ok", [
	#("in", "snr_mean", 7, 15),
	("in", "tru_rad", 0, 11),
	("max", "adamom_frac", 0.01)]
	)

cat = s.select(cat)

print min(cat["snr_mean"]), max(cat["snr_mean"]), np.median(cat["snr_mean"])


rea = "All"
ebarmode = "scatter"

fig = plt.figure(figsize=(12, 8))


#key = "snr_mean"
#key = "tru_rad"
#key = "adamom_frac"
#key = "tru_sersicn"
key = "tru_g"



ax = fig.add_subplot(2, 2, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature(key), Feature("pre_g1_bias"))
ax = fig.add_subplot(2, 2, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"),  Feature("pre_g1_bias", -0.007, 0.007), featc=Feature(key))
ax = fig.add_subplot(2, 2, 3)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_g1_mean", -0.0015, 0.0025), Feature(key), ncbins=3, equalcount=True, ebarmode=ebarmode)







"""
ax = fig.add_subplot(2, 3, 4)
ax = fig.add_subplot(2, 3, 5)
ax = fig.add_subplot(2, 3, 6)


megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"),  Feature("pre_g1_mean"), featc=Feature("snr_mean"), showidline=True, metrics=True)
ax = fig.add_subplot(2, 3, 2)
#megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_g1_mean"), ebarmode=ebarmode)


megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("snr_mean"), Feature("pre_g1_bias"))
ax = fig.add_subplot(2, 3, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("tru_rad"), Feature("pre_g1_bias"))
ax = fig.add_subplot(2, 3, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("tru_sersicn"), Feature("pre_g1_bias"))
ax = fig.add_subplot(2, 3, 5)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("tru_g"), Feature("pre_g1_bias"))


ax = fig.add_subplot(2, 3, 6)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"),  Feature("pre_g1_bias"), featc=Feature("snr_mean"))
ax = fig.add_subplot(3, 5, 7)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"),  Feature("pre_g1_bias"), featc=Feature("adamom_frac"))
ax = fig.add_subplot(3, 5, 8)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"),  Feature("pre_g1_bias"), featc=Feature("tru_rad"))
ax = fig.add_subplot(3, 5, 9)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"),  Feature("pre_g1_bias"), featc=Feature("tru_sersicn"))
ax = fig.add_subplot(3, 5, 10)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"),  Feature("pre_g1_bias"), featc=Feature("tru_g"))


ax = fig.add_subplot(3, 5, 11)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_g1_mean"), Feature("snr_mean"), ncbins=3, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 12)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_g1_mean"), Feature("tru_flux"), ncbins=3, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 13)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_g1_mean"), Feature("tru_rad"), ncbins=3, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 14)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_g1_mean"), Feature("tru_sersicn"), ncbins=3, equalcount=True, ebarmode=ebarmode)
ax = fig.add_subplot(3, 5, 15)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_g1_mean"), Feature("tru_g"), ncbins=3, equalcount=True, ebarmode=ebarmode)
"""

plt.tight_layout()


plt.savefig("/users/mtewes/{}.pdf".format(key))


#plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.



