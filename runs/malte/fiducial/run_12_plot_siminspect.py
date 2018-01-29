import megalut
import os
import config
import numpy as np

from megalut.tools.feature import Feature

import matplotlib
import matplotlib.pyplot as plt



cat = megalut.tools.io.readpickle(os.path.join(config.simmeasdir, config.datasets["siminspect"], "groupmeascat.pkl"))

print megalut.tools.table.info(cat)


fig = plt.figure(figsize=(20, 13))


ax = fig.add_subplot(3, 4, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g"),  Feature("tru_sersicn"), sidehists=True, sidehistkwargs={"bins":20})
ax = fig.add_subplot(3, 4, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_flux"),  Feature("tru_rad"), sidehists=True, sidehistkwargs={"bins":20})
ax = fig.add_subplot(3, 4, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_sb"),  Feature("tru_rad"), Feature("snr"))



ax = fig.add_subplot(3, 4, 5)
megalut.plot.scatter.scatter(ax, cat, Feature("snr"), Feature("tru_flux"))
ax = fig.add_subplot(3, 4, 6)
megalut.plot.scatter.scatter(ax, cat, Feature("snr"), Feature("tru_sb"))
ax = fig.add_subplot(3, 4, 7)
megalut.plot.scatter.scatter(ax, cat, Feature("snr"), Feature("tru_rad"))



"""
ax = fig.add_subplot(3, 4, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g1"), Feature("tru_rad"), Feature("pre_g1_bias"))

ax = fig.add_subplot(3, 4, 5)
megalut.plot.bin.res(ax, cat, Feature("tru_g1"), Feature("pre_g1", rea="full"), ebarmode="scatter")
ax = fig.add_subplot(3, 4, 6)
megalut.plot.bin.res(ax, cat, Feature("tru_g1"), Feature("pre_g1", rea="full"), Feature("tru_flux"), ncbins=3, equalcount=True, ebarmode="scatter")
ax = fig.add_subplot(3, 4, 7)
megalut.plot.bin.res(ax, cat, Feature("tru_g1"), Feature("pre_g1", rea="full"), Feature("tru_rad"), ncbins=3, equalcount=True, ebarmode="scatter")
ax = fig.add_subplot(3, 4, 8)
megalut.plot.bin.res(ax, cat, Feature("tru_g1"), Feature("pre_g1", rea="full"), Feature("tru_g"), ncbins=3, equalcount=True, ebarmode="scatter")

ax = fig.add_subplot(3, 4, 9)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g1"), Feature("pre_g1_mean"), Feature("tru_g2"), showidline=True, metrics=True)
ax = fig.add_subplot(3, 4, 10)
#megalut.plot.scatter.scatter(ax, cat, Feature("adamom_g1", rea=1), Feature("pre_s1", rea=1), Feature("tru_rad", rea=1), showidline=True)
megalut.plot.scatter.scatter(ax, cat, Feature("adamom_g1", rea="full"), Feature("pre_g1", rea="full"), showidline=True)

ax = fig.add_subplot(3, 4, 11)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g2", rea="full"), Feature("pre_g1_bias"))
ax = fig.add_subplot(3, 4, 12)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g", rea="full"), Feature("pre_g1_bias"))
"""

plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.


"""
cat = megalut.tools.io.readpickle(os.path.join(workdir, "train4_Simple1", "precat.pkl"))

print megalut.tools.table.info(cat)

cat["pre_s1"] = cat["pre_s1_000"]


for col in ["pre_s1", "snr"]:
	megalut.tools.table.addstats(cat, col)
megalut.tools.table.addrmsd(cat, "pre_s1", "tru_s1")

print megalut.tools.table.info(cat)


	
fig = plt.figure(figsize=(20, 13))
#fig = plt.figure(figsize=(8, 8))


ax = fig.add_subplot(3, 4, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g", rea=1),  Feature("tru_sersicn"), sidehists=True, sidehistkwargs={"bins":20})
ax = fig.add_subplot(3, 4, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_flux", rea=1),  Feature("tru_rad"), sidehists=True, sidehistkwargs={"bins":20})
ax = fig.add_subplot(3, 4, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("adamom_sigma", rea="full"), Feature("tru_rad"))

ax = fig.add_subplot(3, 4, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("tru_rad"), Feature("pre_s1_bias"))

ax = fig.add_subplot(3, 4, 5)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", rea="full"))
ax = fig.add_subplot(3, 4, 6)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", rea="full"), Feature("tru_flux"), ncbins=3, equalcount=True)
ax = fig.add_subplot(3, 4, 7)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", rea="full"), Feature("tru_rad"), ncbins=3, equalcount=True)
ax = fig.add_subplot(3, 4, 8)
megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", rea="full"), Feature("tru_g"), ncbins=3, equalcount=True)

ax = fig.add_subplot(3, 4, 9)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("pre_s1_mean"), Feature("tru_s2"), showidline=True, metrics=True)
ax = fig.add_subplot(3, 4, 10)
#megalut.plot.scatter.scatter(ax, cat, Feature("adamom_g1", rea=1), Feature("pre_s1", rea=1), Feature("tru_rad", rea=1), showidline=True)
megalut.plot.scatter.scatter(ax, cat, Feature("adamom_g1", rea="full"), Feature("pre_s1", rea="full"), showidline=True)

ax = fig.add_subplot(3, 4, 11)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", rea="full"), Feature("pre_s1_bias"))
ax = fig.add_subplot(3, 4, 12)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g", rea="full"), Feature("pre_s1_bias"))



plt.tight_layout(
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.

"""
