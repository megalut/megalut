
execfile("config.py")

import megalut.plot
from megalut.tools.feature import Feature

import matplotlib
import matplotlib.pyplot as plt

cat = megalut.tools.io.readpickle(os.path.join(workdir, "GauShear1", "selfprecat.pkl"))


cat["tru_g"] = np.hypot(cat["tru_g1"], cat["tru_g2"])

#print megalut.tools.table.info(cat)

	
hexbinkwargs = {"gridsize":50, "mincnt":100, "cmap":matplotlib.cm.get_cmap("rainbow")}


	
fig = plt.figure(figsize=(18, 12))

"""
ax = fig.add_subplot(3, 4, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g", rea=1),  Feature("tru_sigma"), sidehists=True, sidehistkwargs={"bins":20})

ax = fig.add_subplot(3, 4, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("tru_s2"))
ax = fig.add_subplot(3, 4, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g1", 0.3, 0.6, rea="full"), Feature("tru_g2", 0.3, 0.6, rea="full"))
	
	


cat["pre_s1_res"] = cat["pre_s1"] - cat["tru_s1"].reshape((-1, 1))


ax = fig.add_subplot(3, 4, 5)
megalut.plot.bin.bin(ax, cat, Feature("tru_s1"), Feature("pre_s1_res", rea="full"), ebarmode="bias")
"""

#ax = fig.add_subplot(3, 4, 6)
ax = fig.add_subplot(1,1,1)

megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", -0.01, 0.01, rea="full"), Feature("tru_flux"), ncbins=5, ebarmode="bias")



#psfselector = megalut.tools.table.Selector("Particular PSF",
#	[("in", "tru_psf_g1", 0.00, 0.05), ("in", "tru_psf_g2", -0.01, 0.01)]) 
#	psfselcat = psfselector.select(cat)


	
plt.tight_layout()

#plt.savefig("plot.png")
plt.show()

