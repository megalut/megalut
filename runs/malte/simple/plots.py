

import megalut.plot
from megalut.tools.feature import Feature

import matplotlib
import matplotlib.pyplot as plt

import numpy as np


def shear_true(cat, filepath=None):

	cat["tru_g"] = np.hypot(cat["tru_g1"], cat["tru_g2"])

	print megalut.tools.table.info(cat)

	
	fig = plt.figure(figsize=(20, 13))
	#fig = plt.figure(figsize=(8, 8))


	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, Feature("tru_g", rea=1),  Feature("tru_sigma"), sidehists=True, sidehistkwargs={"bins":20})
	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("tru_s2"))


	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", -0.01, 0.02, rea="full"), Feature("snr", rea="full"), ncbins=3, equalcount=True)
	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", -0.01, 0.02, rea="full"), Feature("snr", rea="full"), ncbins=3, equalcount=True)


	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", -0.01, 0.01, rea="full"))
	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", -0.01, 0.02, rea="full"), Feature("tru_flux"), ncbins=3)
	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", -0.01, 0.02, rea="full"), Feature("tru_sigma"), ncbins=3)
	ax = fig.add_subplot(3, 4, 8)
	megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", -0.01, 0.02, rea="full"), Feature("tru_g", rea="full"), ncbins=3)


	ax = fig.add_subplot(3, 4, 9)
	megalut.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", -0.01, 0.01, rea="full"))
	ax = fig.add_subplot(3, 4, 10)
	megalut.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", -0.01, 0.02, rea="full"), Feature("tru_flux"), ncbins=3)
	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", -0.01, 0.02, rea="full"), Feature("tru_sigma"), ncbins=3)
	ax = fig.add_subplot(3, 4, 12)
	megalut.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", -0.01, 0.02, rea="full"), Feature("tru_g", rea="full"), ncbins=3)

	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.



def shear_mes(cat, filepath=None):

	cat["adamom_g"] = np.hypot(cat["adamom_g1"], cat["adamom_g2"])

	print megalut.tools.table.info(cat)

	
	fig = plt.figure(figsize=(20, 13))
	#fig = plt.figure(figsize=(8, 8))

	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.bin.res(ax, cat, Feature("tru_g1", rea="full"), Feature("pre_s1", -0.15, 0.15, rea="full"))
	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.bin.res(ax, cat, Feature("tru_g2", rea="full"), Feature("pre_s2", -0.15, 0.15, rea="full"))
	
	
	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.bin.res(ax, cat, Feature("tru_g1", rea="full"), Feature("pre_s1", -0.15, 0.15, rea="full"), Feature("tru_g2", rea="full"), equalcount=True, ncbins=2)
	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.bin.res(ax, cat, Feature("tru_g2", rea="full"), Feature("pre_s2", -0.15, 0.15, rea="full"), Feature("tru_g1", rea="full"), equalcount=True, ncbins=2)
	
	
	
	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", -0.01, 0.01, rea="full"))
	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", -0.01, 0.02, rea="full"), Feature("adamom_flux", rea="full"), ncbins=3, equalcount=True)
	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", -0.01, 0.02, rea="full"), Feature("adamom_sigma", rea="full"), ncbins=3, equalcount=True)
	ax = fig.add_subplot(3, 4, 8)
	megalut.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", -0.1, 0.2, rea="full"), Feature("adamom_g", rea="full"), ncbins=3, equalcount=True)


	ax = fig.add_subplot(3, 4, 9)
	megalut.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", -0.01, 0.01, rea="full"))
	ax = fig.add_subplot(3, 4, 10)
	megalut.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", -0.01, 0.02, rea="full"), Feature("adamom_flux", rea="full"), ncbins=3, equalcount=True)
	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", -0.01, 0.02, rea="full"), Feature("adamom_sigma", rea="full"), ncbins=3, equalcount=True)
	ax = fig.add_subplot(3, 4, 12)
	megalut.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", -0.1, 0.2, rea="full"), Feature("adamom_g", rea="full"), ncbins=3, equalcount=True)


	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.
