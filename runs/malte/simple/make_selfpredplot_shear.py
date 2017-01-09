execfile("config.py")

from megalut.tools.feature import Feature

import matplotlib
import matplotlib.pyplot as plt

import numpy as np


cat = megalut.tools.io.readpickle(os.path.join(workdir, "train1_SimpleS1", "precat.pkl"))
#cat = megalut.tools.io.readpickle(os.path.join(workdir, "validcat.pkl"))

print megalut.tools.table.info(cat)



for col in ["pre_s1", "pre_s2", "snr"]:
	megalut.tools.table.addstats(cat, col)
megalut.tools.table.addrmsd(cat, "pre_s1", "tru_s1")
megalut.tools.table.addrmsd(cat, "pre_s2", "tru_s2")

print megalut.tools.table.info(cat)


fig = plt.figure(figsize=(20, 13))


ax = fig.add_subplot(3, 4, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_rad", rea=1),  Feature("tru_sersicn", rea="full"), sidehists=True, sidehistkwargs={"bins":20})
ax = fig.add_subplot(3, 4, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("adamom_sigma", rea="full"), Feature("tru_rad", rea="full"))
ax = fig.add_subplot(3, 4, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2"), Feature("tru_rad", rea="full"), Feature("pre_s2_bias"))
ax = fig.add_subplot(3, 4, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("tru_rad", rea="full"), Feature("pre_s1_bias"))

ax = fig.add_subplot(3, 4, 5)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", rea="full"), ebarmode="scatter")
ax = fig.add_subplot(3, 4, 6)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", rea="full"), Feature("tru_flux"), ncbins=3, equalcount=True, ebarmode="scatter")
ax = fig.add_subplot(3, 4, 7)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", rea="full"), Feature("tru_rad", rea="full"), ncbins=3, equalcount=True, ebarmode="scatter")
ax = fig.add_subplot(3, 4, 8)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", rea="full"), Feature("tru_g", rea="full"), ncbins=3, equalcount=True, ebarmode="scatter")

ax = fig.add_subplot(3, 4, 9)
megalut.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", rea="full"), ebarmode="scatter")
ax = fig.add_subplot(3, 4, 10)
megalut.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", rea="full"), Feature("tru_flux", rea="full"), ncbins=3, equalcount=True, ebarmode="scatter")
ax = fig.add_subplot(3, 4, 11)
megalut.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", rea="full"), Feature("tru_rad", rea="full"), ncbins=3, equalcount=True, ebarmode="scatter")
ax = fig.add_subplot(3, 4, 12)
megalut.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", rea="full"), Feature("tru_g", rea="full"), ncbins=3, equalcount=True, ebarmode="scatter")


plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.


