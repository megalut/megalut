import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import megalut.plot
from megalut.tools.feature import Feature

import logging
logger = logging.getLogger(__name__)

def shearbias(run, filepath=None, rea="full"):

	"""
	#cat =  megalut.tools.io.readpickle(os.path.join(run.workmldir, "obsprecat.pkl"))
	cat =  megalut.tools.io.readpickle(os.path.join(run.workmldir, "selfprecat.pkl"))
	
	
	print cat.colnames
	#print len(cat)
	
	
	cat = megalut.tools.table.groupreshape(cat, bincolnames=["tru_s1", "tru_s2", "tru_mu"])
	
	megalut.tools.io.writepickle(cat, os.path.join(run.workmldir, "test.pkl"))
	"""
	
	cat =  megalut.tools.io.readpickle(os.path.join(run.workmldir, "test.pkl"))
	
	
	megalut.tools.table.addstats(cat, "pre_g1")
	
	cat["pre_g1_errmean"] = cat["pre_g1_std"] / np.sqrt(cat["pre_g1_n"])
	
	cat["bias_s1"] = cat["pre_g1_mean"] - cat["tru_s1"]
	
	pre_g1_mean = Feature("pre_g1_mean")
	pre_g1 = Feature("pre_g1", rea="full")
	snr = Feature("snr", rea="full")
	s1_bias = Feature("s1_bias", nicename="Bias on s1")
	tru_s1 = Feature("tru_s1", nicename="True shear s1")
	
	
	
	fig = plt.figure(figsize=(21, 12))

	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_g1, showidline=True, metrics=True)
	
	
	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_g1_mean, showidline=True, metrics=True, color="red", alpha=1)

	
	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, bias_s1, color="red", alpha=1)
	
	
	
		
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.
	




def groupshearbias(run, filepath=None):
	
	indicat =  megalut.tools.io.readpickle(os.path.join(run.workmldir, "selfprecat.pkl"))
	tru_g1 = Feature("tru_g1")
	tru_g2 = Feature("tru_g2")
	pre_s1 = Feature("pre_s1")
	pre_s2 = Feature("pre_s2")
	tru_s1 = Feature("tru_s1", -0.06, 0.06)
	tru_s2 = Feature("tru_s2", -0.06, 0.06)

	print "Shear estimates:"
	print megalut.tools.metrics.metrics(indicat, tru_s1, pre_s1)
	print megalut.tools.metrics.metrics(indicat, tru_s2, pre_s2)
	
	cat = megalut.tools.table.groupreshape(indicat, groupcolnames=["tru_s1", "tru_s2"])
	
	megalut.tools.table.addstats(cat, "pre_s1")
	megalut.tools.table.addstats(cat, "pre_s2")
	

	cat["bias_s1"] = cat["pre_s1_mean"] - cat["tru_s1"]
	cat["bias_s2"] = cat["pre_s2_mean"] - cat["tru_s2"]
	
	cat["bias_s1_err"] = cat["pre_s1_std"] / cat["pre_s1_n"]
	cat["bias_s2_err"] = cat["pre_s2_std"] / cat["pre_s2_n"]
	
		
	bias_s1 = Feature("bias_s1", errcolname="bias_s1_err")
	bias_s2 = Feature("bias_s2", errcolname="bias_s2_err")
	bias_s1_err = Feature("bias_s1_err")
	bias_s2_err = Feature("bias_s2_err")
	pre_s1_mean = Feature("pre_s1_mean", errcolname="bias_s1_err")
	pre_s2_mean = Feature("pre_s2_mean", errcolname="bias_s2_err")
	snr = Feature("snr")
	tru_g1 = Feature("tru_g1")
	tru_g2 = Feature("tru_g2")
	pre_s1 = Feature("pre_s1")
	pre_s2 = Feature("pre_s2")
	tru_s1 = Feature("tru_s1", -0.06, 0.06)
	tru_s2 = Feature("tru_s2", -0.06, 0.06)

	
	fig = plt.figure(figsize=(18, 10))

	ax = fig.add_subplot(2, 3, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_mean, metrics=True)

	ax = fig.add_subplot(2, 3, 4)
	megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_mean, metrics=True)

	ax = fig.add_subplot(2, 3, 2)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, tru_s2, bias_s1, s=90)
	
	ax = fig.add_subplot(2, 3, 5)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, tru_s2, bias_s2, s=90)
	
	ax = fig.add_subplot(2, 3, 3)
	megalut.plot.hexbin.hexbin(ax, indicat, tru_g1, pre_s1)
	
	ax = fig.add_subplot(2, 3, 6)
	megalut.plot.hexbin.hexbin(ax, indicat, tru_g2, pre_s2)


	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.





def newshearbias(run, filepath=None):
	

	indicat =  megalut.tools.io.readpickle(os.path.join(run.workmldir, "selfprecat.pkl"))
	print len(indicat)
	
	
	
	cat = megalut.tools.table.groupreshape(indicat, groupcolnames=["tru_s1", "tru_s2"])
	
	#cat = megalut.tools.io.readpickle(os.path.join(run.workmldir, "selfprecat_binreshape.pkl"))

	print len(cat)
	print cat.colnames
	
	
	#exit()
	megalut.tools.table.addstats(cat, "pre_s1")
	megalut.tools.table.addstats(cat, "pre_s2")
	
	cat["bias_s1"] = cat["pre_s1_mean"] - cat["tru_s1"]
	cat["bias_s2"] = cat["pre_s2_mean"] - cat["tru_s2"]
	
	cat["bias_s1_err"] = cat["pre_s1_std"] / cat["pre_s1_n"]
	cat["bias_s2_err"] = cat["pre_s2_std"] / cat["pre_s2_n"]
	
	
	#exit()
	
	
	
	bias_s1 = Feature("bias_s1", errcolname="bias_s1_err")
	bias_s2 = Feature("bias_s2", errcolname="bias_s2_err")
	bias_s1_err = Feature("bias_s1_err")
	bias_s2_err = Feature("bias_s2_err")
	pre_s1_mean = Feature("pre_s1_mean", errcolname="bias_s1_err")
	pre_s2_mean = Feature("pre_s2_mean", errcolname="bias_s2_err")
	tru_s1 = Feature("tru_s1")
	tru_s2 = Feature("tru_s2")
	tru_g1 = Feature("tru_g1")
	tru_g2 = Feature("tru_g2")
	
	pre_s1 = Feature("pre_s1")
	pre_s2 = Feature("pre_s2")

	snr = Feature("snr")
	
	
	fig = plt.figure(figsize=(21, 12))

	"""
	#ax = fig.add_subplot(3, 4, 9)
	#megalut.plot.scatter.scatter(ax, indicat, tru_g1, pre_s1, snr, metrics=True)
	#ax = fig.add_subplot(3, 4, 10)
	#megalut.plot.scatter.scatter(ax, indicat, tru_g2, pre_s2, snr, metrics=True)
	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.hexbin.hexbin(ax, indicat, tru_g1, pre_s1)
	ax = fig.add_subplot(3, 4, 12)
	megalut.plot.hexbin.hexbin(ax, indicat, tru_g2, pre_s2)
	"""
	
	"""
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, bias_s1, metrics=True)

	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.scatter.scatter(ax, cat, tru_s2, bias_s2, metrics=True)

	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_mean, showidline=True, metrics=True)

	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_mean, showidline=True, metrics=True)

	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, bias_s1_err)

	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.scatter.scatter(ax, cat, tru_s2, bias_s2_err)
	"""
	
	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, tru_s2, bias_s1, s=10)
	
	ax = fig.add_subplot(3, 4, 8)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, tru_s2, bias_s2)
	
	

	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.




