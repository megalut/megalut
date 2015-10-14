import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import megalut.plot
from megalut.tools.feature import Feature

import logging
logger = logging.getLogger(__name__)





def shearsimbias(run, filepath=None, rea="full"):
	"""
	Compares weighted predicted shapes with true shear, what should work.
	"""

	cat =  megalut.tools.io.readpickle(os.path.join(run.workmldir, "selfprecat_shear.pkl"))
	
	#cat = cat[0:1]
	
	print cat.colnames

	
	rs = 0.04
	rg = 0.7

	
	pre_s1 = Feature("pre_s1", rea=rea)
	pre_s2 = Feature("pre_s2", rea=rea)
	tru_s1 = Feature("tru_s1", -rs, rs)
	tru_s2 = Feature("tru_s2", -rs, rs)
	
	tru_g1 = Feature("tru_g1", -rg, rg, rea=rea)
	tru_g2 = Feature("tru_g2", -rg, rg, rea=rea)
	
	
	megalut.tools.table.addstats(cat, "pre_s1")
	megalut.tools.table.addstats(cat, "pre_s2")
	
	
	pre_s1_mean = Feature("pre_s1_mean")
	pre_s2_mean = Feature("pre_s2_mean")
	
	
	snr = Feature("snr", 5, 40, rea=rea)
	
	
	fig = plt.figure(figsize=(22, 13))
	cmap = matplotlib.cm.get_cmap("rainbow")
	
	sckws={"cmap":cmap}
	idkws={"color":"black", "lw":2}
		
	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_mean, metrics=True, showidline=True, idlinekwargs=idkws)
	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_mean, metrics=True, showidline=True, idlinekwargs=idkws)
	
	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.hexbin.hexbin(ax, cat, tru_g1, pre_s1, showidline=True, idlinekwargs=idkws)
	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.hexbin.hexbin(ax, cat, tru_g2, pre_s2, showidline=True, idlinekwargs=idkws)
	

	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.


	







