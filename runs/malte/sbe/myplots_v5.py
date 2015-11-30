import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import megalut.plot
from megalut.tools.feature import Feature

import logging
logger = logging.getLogger(__name__)




def measfails(run, simparams, filepath=None, rea="full"):
	"""
	On the sims, we study what kind of galaxies are missed...
	"""
	
	cat = megalut.tools.io.readpickle(os.path.join(run.worksimdir, simparams.name, "groupmeascat.pkl"))
	
	#print cat
	#print cat.colnames
	
	#exit()
	
	
	psf_g1 = Feature("tru_psf_g1", -0.06, 0.06)
	psf_g2 = Feature("tru_psf_g2", -0.06, 0.06)
	psf_sigma = Feature("tru_psf_sigma")
	
	tru_flux = Feature("tru_flux")
	tru_sigma = Feature("tru_sigma")
	
	tru_g1 = Feature("tru_g1")
	tru_g2 = Feature("tru_g2")
	
	
	ix = Feature("ix")
	iy = Feature("iy")

	selector = megalut.tools.table.Selector("Failed", [("mask", "adamom_sigma")]) 
	failcat = selector.select(cat)

	#print failcat
	
	fig = plt.figure(figsize=(23, 11))
		
	ax = fig.add_subplot(2, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_flux, tru_sigma, sidehists=False, color="gray")
	megalut.plot.scatter.scatter(ax, failcat, tru_flux, tru_sigma, sidehists=True, color="red")
	
	ax = fig.add_subplot(2, 4, 2)
	megalut.plot.scatter.scatter(ax, cat, ix, iy, sidehists=False, color="gray")
	megalut.plot.scatter.scatter(ax, failcat, ix, iy, sidehists=True, color="red")
	
	ax = fig.add_subplot(2, 4, 3)
	megalut.plot.scatter.scatter(ax, cat, tru_g1, tru_g2, sidehists=False, color="gray")
	megalut.plot.scatter.scatter(ax, failcat, tru_g1, tru_g2, sidehists=True, color="red")
	
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.




def simobscompa(run, simparams, prefix="adamom_", filepath=None, rea="full"):
	"""
	Classic comparision between obs and sims
	"""
	
	#simcatpath = megalut.meas.utils.simmeasdict(run.worksimdir, simparams).values()[0][0]
	simcatpath = "groupmeascat.pkl"
	
	simcat = megalut.tools.io.readpickle(os.path.join(run.worksimdir, simparams.name, simcatpath))
	
	
	#print simcat
	
	#exit()
	
	
	# And a bunch of the obs
	obscat = megalut.tools.io.readpickle(run.groupobspath)
			
	simcat = megalut.tools.table.shuffle(simcat)
	obscat = megalut.tools.table.shuffle(obscat)
		
	flux = Feature(prefix+"flux", rea=rea)
	sigma = Feature(prefix+"sigma", 0, 30, rea=rea)
	rho4 = Feature(prefix+"rho4", 1.3, 2.6, rea=rea)
	g1 = Feature(prefix+"g1", -0.8, 0.8, rea=rea)
	g2 = Feature(prefix+"g2", -0.8, 0.8, rea=rea)
	skymad = Feature("skymad", rea=rea)
	skystd = Feature("skystd", rea=rea)
	skymed = Feature("skymed", rea=rea)
	skymean = Feature("skymean", rea=rea)
	psf_g1 = Feature("tru_psf_g1", -0.06, 0.06, rea=rea)
	psf_g2 = Feature("tru_psf_g2", -0.06, 0.06, rea=rea)
	psf_sigma = Feature("tru_psf_sigma", rea=rea)
	snr =Feature("snr", rea=rea)

	fig = plt.figure(figsize=(23, 11))
		
	ax = fig.add_subplot(2, 4, 1)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, flux, sigma, sidehists=False, legend=False, pale=True)
	megalut.plot.contour.simobs(ax, simcat, obscat, flux, sigma, legend=True)

	ax = fig.add_subplot(2, 4, 2)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, sigma, rho4, sidehists=False, legend=False, pale=True)
	megalut.plot.contour.simobs(ax, simcat, obscat, sigma, rho4)

	ax = fig.add_subplot(2, 4, 3)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, g1, g2, sidehists=False, legend=False, pale=True)
	megalut.plot.contour.simobs(ax, simcat, obscat, g1, g2)
	
	ax = fig.add_subplot(2, 4, 4)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, flux, snr, sidehists=False, legend=False, pale=True)
	megalut.plot.contour.simobs(ax, simcat, obscat, flux, snr)
		
	ax = fig.add_subplot(2, 4, 5)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, flux, skystd, sidehists=False, legend=False, pale=True)	
	megalut.plot.contour.simobs(ax, simcat, obscat, skymad, skystd)
	
	ax = fig.add_subplot(2, 4, 6)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, skymed, skymean, sidehists=False, legend=False, pale=True)
	megalut.plot.contour.simobs(ax, simcat, obscat, skymed, flux)
	
	ax = fig.add_subplot(2, 4, 7)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, psf_sigma, sigma, sidehists=False, legend=False, pale=True)
	megalut.plot.contour.simobs(ax, simcat, obscat, psf_sigma, sigma)
	
	ax = fig.add_subplot(2, 4, 8)
	#megalut.plot.scatter.simobs(ax, simcat, obscat, psf_g1, psf_g2, sidehists=False, legend=False, pale=True)
	megalut.plot.contour.simobs(ax, simcat, obscat, psf_g1, psf_g2)
	
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.







def shearsimbias(run, simparams, filepath=None, rea="full", mode="low"):
	"""

	"""
	
	#cat =  megalut.tools.io.readpickle(os.path.join(run.worksimdir, simparams.name, "groupmeascat.pkl"))
	#cat =  megalut.tools.io.readpickle(os.path.join(run.worksimdir, simparams.name, "groupmeascat_cases.pkl"))
	
	name = "with_" + simparams.name
	traindir = os.path.join(run.workmldir, name)
	cat =  megalut.tools.io.readpickle(os.path.join(traindir, "selfprecat_shear.pkl"))

	#print cat.colnames
	#print cat
	#print cat.meta
	
	if mode == "low":
		rs = 0.03
		rg = 0.7
		rb = 0.005
		relrb = 20.0
		snrrange=(0, 60)
		
	elif mode == "high":
		rs = 0.03
		rg = 0.7
		rb = 0.001
		relrb = 5.0
		snrrange=(0, 300)	
	
	else:
		raise RuntimeError("wrong mode")
	
	#cat["pre_s1"] = cat["pre_s1pw"]
	#cat["pre_s2"] = cat["pre_s2pw"]

	pre_s1 = Feature("pre_s1", -rg, rg, rea=rea)
	pre_s2 = Feature("pre_s2", -rg, rg, rea=rea)
	
	tru_s1 = Feature("tru_s1", -rs, rs)
	tru_s2 = Feature("tru_s2", -rs, rs)
	tru_psf_g1 = Feature("tru_psf_g1", -rs, rs)
	tru_psf_g2 = Feature("tru_psf_g2", -rs, rs)
	
	megalut.tools.table.addstats(cat, "pre_s1")
	megalut.tools.table.addstats(cat, "pre_s2")
	
	tru_g1 = Feature("tru_g1", -rg, rg, rea=rea)
	tru_g2 = Feature("tru_g2", -rg, rg, rea=rea)

	snr = Feature("snr", snrrange[0], snrrange[1], rea=rea)
	
	
	
	
	cat["bias_s1"] = cat["pre_s1_mean"] - cat["tru_s1"]
	cat["bias_s2"] = cat["pre_s2_mean"] - cat["tru_s2"]
	
	cat["bias_s1_err"] = cat["pre_s1_std"] / cat["pre_s1_n"]
	cat["bias_s2_err"] = cat["pre_s2_std"] / cat["pre_s2_n"]
	
	cat["rel_bias_s1"] = 100.0 * cat["bias_s1"] / cat["tru_s1"]
	cat["rel_bias_s2"] = 100.0 * cat["bias_s1"] / cat["tru_s2"]
	
		
	bias_s1 = Feature("bias_s1", -rb, rb, errcolname="bias_s1_err")
	bias_s2 = Feature("bias_s2", -rb, rb, errcolname="bias_s2_err")		
	rel_bias_s1 = Feature("rel_bias_s1", -relrb, relrb, nicename = "Rel bias on s1 (percent)")
	rel_bias_s2 = Feature("rel_bias_s2", -relrb, relrb, nicename = "Rel bias on s2 (percent)")
	
	
	bias_s1_err = Feature("bias_s1_err")
	bias_s2_err = Feature("bias_s2_err")
	pre_s1_mean = Feature("pre_s1_mean", -rs, rs, errcolname="bias_s1_err")
	pre_s2_mean = Feature("pre_s2_mean", -rs, rs, errcolname="bias_s2_err")

	
	fig = plt.figure(figsize=(22, 13))
	cmap = matplotlib.cm.get_cmap("rainbow")
	
	sckws = {"cmap":cmap}
	idkws={"color":"black", "lw":2}
	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_mean, tru_psf_g1, s=10, metrics=True, showidline=True, idlinekwargs=idkws, **sckws)

	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_mean, tru_psf_g1, s=10, metrics=True, showidline=True, idlinekwargs=idkws, **sckws)


	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.hexbin.hexbin(ax, cat, tru_s1, pre_s1_mean, showidline=True, idlinekwargs=idkws)

	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.hexbin.hexbin(ax, cat, tru_s2, pre_s2_mean, showidline=True, idlinekwargs=idkws)




	
	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.hexbin.hexbin(ax, cat, tru_s1, tru_s2, rel_bias_s1, cmap=cmap, gridsize=6)

	ax = fig.add_subplot(3, 4, 6)
	#megalut.plot.scatter.scatter(ax, cat, tru_s2, bias_s2, tru_s1, s=10, **sckws)
	megalut.plot.hexbin.hexbin(ax, cat, tru_s1, tru_s2, rel_bias_s2, cmap=cmap, gridsize=6)

	
	ax = fig.add_subplot(3, 4, 7)
	#megalut.plot.scatter.scatter(ax, cat, tru_psf_g1, tru_psf_g2, bias_s1, s=10, **sckws)
	megalut.plot.hexbin.hexbin(ax, cat, tru_psf_g1, tru_psf_g2, bias_s1, cmap=cmap, gridsize=6)


	ax = fig.add_subplot(3, 4, 8)
	#megalut.plot.scatter.scatter(ax, cat, tru_psf_g1, tru_psf_g2, bias_s2, s=10, **sckws)
	megalut.plot.hexbin.hexbin(ax, cat, tru_psf_g1, tru_psf_g2, bias_s2, cmap=cmap, gridsize=6)



	
	ax = fig.add_subplot(3, 4, 9)
	megalut.plot.hexbin.hexbin(ax, cat, tru_g1, pre_s1, showidline=True, idlinekwargs=idkws)

	"""
	ax = fig.add_subplot(3, 4, 10)
	megalut.plot.hexbin.hexbin(ax, cat, tru_g2, pre_s2, showidline=True, idlinekwargs=idkws)

	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.hexbin.hexbin(ax, cat, tru_g1, pre_s1, snr, showidline=True, idlinekwargs=idkws, cmap=cmap)

	ax = fig.add_subplot(3, 4, 12)
	megalut.plot.hexbin.hexbin(ax, cat, tru_g2, pre_s2, snr, showidline=True, idlinekwargs=idkws, cmap=cmap)
	"""

	"""
	ax = fig.add_subplot(2, 3, 4)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1, snr, s=5, metrics=True, showidline=True, idlinekwargs=idkws, **sckws)

	ax = fig.add_subplot(2, 3, 5)
	megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2, snr, s=5, metrics=True, showidline=True, idlinekwargs=idkws, **sckws)
	"""

	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.






def shearsimbias3(run, simparams, filepath=None, rea="full", mode="low"):
	"""

	"""
	
	#cat =  megalut.tools.io.readpickle(os.path.join(run.worksimdir, simparams.name, "groupmeascat.pkl"))
	#cat =  megalut.tools.io.readpickle(os.path.join(run.worksimdir, simparams.name, "groupmeascat_cases.pkl"))
	
	name = "with_" + simparams.name
	traindir = os.path.join(run.workmldir, name)
	cat =  megalut.tools.io.readpickle(os.path.join(traindir, "selfprecat_shear.pkl"))

	#print cat.colnames
	#print cat
	#print cat.meta
	
	if mode == "low":
		rs = 0.03
		rg = 0.7
		rb = 0.005
		relrb = 20.0
		snrrange=(0, 60)
		
	elif mode == "high":
		rs = 0.03
		rg = 0.7
		rb = 0.001
		relrb = 5.0
		snrrange=(0, 300)	
	
	else:
		raise RuntimeError("wrong mode")
	
	cat["pre_s1"] = cat["pre_s1pw"] * cat["pw"]
	cat["pre_s2"] = cat["pre_s2pw"] * cat["pw"]

	megalut.tools.table.addstats(cat, "pre_s1")
	megalut.tools.table.addstats(cat, "pre_s2")
	megalut.tools.table.addstats(cat, "pw")
	
	cat["s1wmean"] = cat["pre_s1_mean"] / cat["pw_mean"]
	cat["s2wmean"] = cat["pre_s2_mean"] / cat["pw_mean"]
	

	pre_s1_mean = Feature("s1wmean", -rs, rs)
	pre_s2_mean = Feature("s2wmean", -rs, rs)
	tru_s1 = Feature("tru_s1", -rs, rs)
	tru_s2 = Feature("tru_s2", -rs, rs)

	
	fig = plt.figure(figsize=(22, 13))
	cmap = matplotlib.cm.get_cmap("rainbow")
	
	sckws = {"cmap":cmap}
	idkws={"color":"black", "lw":2}
	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_mean, metrics=True, showidline=True, idlinekwargs=idkws)

	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_mean, metrics=True, showidline=True, idlinekwargs=idkws)


	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.



def shearsimbias2(run, simparams, filepath=None, rea="full"):
	"""
	focuses on SNR dependency
	"""
	
	#cat =  megalut.tools.io.readpickle(os.path.join(run.worksimdir, simparams.name, "groupmeascat.pkl"))
	#cat =  megalut.tools.io.readpickle(os.path.join(run.worksimdir, simparams.name, "groupmeascat_cases.pkl"))
	
	name = "with_" + simparams.name
	traindir = os.path.join(run.workmldir, name)
	#cat =  megalut.tools.io.readpickle(os.path.join(traindir, "selfprecat_shear.pkl"))
	cat =  megalut.tools.io.readpickle(os.path.join(traindir, "selfprecat_shear_nocases.pkl"))

	lowSNsel = megalut.tools.table.Selector("lowSN",[("in", "snr", 5, 22)])
	midSNsel = megalut.tools.table.Selector("lowSN",[("in", "snr", 22, 35)])
	highSNsel = megalut.tools.table.Selector("lowSN",[("in", "snr", 35, 100)])
	
	lowSNcat = lowSNsel.select(cat)
	midSNcat = midSNsel.select(cat)
	highSNcat = highSNsel.select(cat)
	
	
	rs = 0.03
	rg = 0.7
	rb = 0.005
	relrb = 20.0
	snrrange=(0, 60)
	
	snr = Feature("snr", snrrange[0], snrrange[1], rea=rea)
	pre_s1 = Feature("pre_s1", -rg, rg, rea=rea)
	pre_s2 = Feature("pre_s2", -rg, rg, rea=rea)
	tru_s1 = Feature("tru_s1", -rs, rs)
	tru_s2 = Feature("tru_s2", -rs, rs)
	tru_psf_g1 = Feature("tru_psf_g1", -rs, rs)
	tru_psf_g2 = Feature("tru_psf_g2", -rs, rs)
	
	for c in [cat, lowSNcat, midSNcat, highSNcat]:
		#megalut.tools.table.addstats(c, "pre_s1")
		#megalut.tools.table.addstats(c, "pre_s2")
	
		c["tru_g1ps1"] = c["tru_g1"] + c["tru_s1"]
		c["tru_g2ps2"] = c["tru_g2"] + c["tru_s2"]
	
	pre_s1_mean = Feature("pre_s1_mean", -rs, rs)
	pre_s2_mean = Feature("pre_s2_mean", -rs, rs)

	tru_g1 = Feature("tru_g1", -rg, rg, rea=rea)
	tru_g2 = Feature("tru_g2", -rg, rg, rea=rea)

	
	
	#cat["bias_s1"] = cat["pre_s1_mean"] - cat["tru_s1"]
	#cat["bias_s2"] = cat["pre_s2_mean"] - cat["tru_s2"]
	#cat["bias_s1_err"] = cat["pre_s1_std"] / cat["pre_s1_n"]
	#cat["bias_s2_err"] = cat["pre_s2_std"] / cat["pre_s2_n"]
	#cat["rel_bias_s1"] = 100.0 * cat["bias_s1"] / cat["tru_s1"]
	#cat["rel_bias_s2"] = 100.0 * cat["bias_s1"] / cat["tru_s2"]
	
		
	#bias_s1 = Feature("bias_s1", -rb, rb, errcolname="bias_s1_err")
	#bias_s2 = Feature("bias_s2", -rb, rb, errcolname="bias_s2_err")		
	#rel_bias_s1 = Feature("rel_bias_s1", -relrb, relrb, nicename = "Rel bias on s1 (percent)")
	#rel_bias_s2 = Feature("rel_bias_s2", -relrb, relrb, nicename = "Rel bias on s2 (percent)")
	#bias_s1_err = Feature("bias_s1_err")
	#bias_s2_err = Feature("bias_s2_err")
	
	
	fig = plt.figure(figsize=(22, 13))
	cmap = matplotlib.cm.get_cmap("rainbow")
	
	sckws = {"cmap":cmap}
	idkws={"color":"black", "lw":2}
	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.hist.hist(ax, lowSNcat, snr, color="red")
	megalut.plot.hist.hist(ax, midSNcat, snr, color="black")
	megalut.plot.hist.hist(ax, highSNcat, snr, color="blue")
	

	"""
	megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_mean, tru_psf_g1, s=10, metrics=True, showidline=True, idlinekwargs=idkws, **sckws)

	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_mean, tru_psf_g1, s=10, metrics=True, showidline=True, idlinekwargs=idkws, **sckws)


	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.hexbin.hexbin(ax, cat, tru_s1, pre_s1_mean, showidline=True, idlinekwargs=idkws)

	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.hexbin.hexbin(ax, cat, tru_s2, pre_s2_mean, showidline=True, idlinekwargs=idkws)




	
	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.hexbin.hexbin(ax, cat, tru_s1, tru_s2, rel_bias_s1, cmap=cmap, gridsize=6)

	ax = fig.add_subplot(3, 4, 6)
	#megalut.plot.scatter.scatter(ax, cat, tru_s2, bias_s2, tru_s1, s=10, **sckws)
	megalut.plot.hexbin.hexbin(ax, cat, tru_s1, tru_s2, rel_bias_s2, cmap=cmap, gridsize=6)

	
	ax = fig.add_subplot(3, 4, 7)
	#megalut.plot.scatter.scatter(ax, cat, tru_psf_g1, tru_psf_g2, bias_s1, s=10, **sckws)
	megalut.plot.hexbin.hexbin(ax, cat, tru_psf_g1, tru_psf_g2, bias_s1, cmap=cmap, gridsize=6)


	ax = fig.add_subplot(3, 4, 8)
	#megalut.plot.scatter.scatter(ax, cat, tru_psf_g1, tru_psf_g2, bias_s2, s=10, **sckws)
	megalut.plot.hexbin.hexbin(ax, cat, tru_psf_g1, tru_psf_g2, bias_s2, cmap=cmap, gridsize=6)



	
	ax = fig.add_subplot(3, 4, 9)
	megalut.plot.hexbin.hexbin(ax, cat, tru_g1, pre_s1, showidline=True, idlinekwargs=idkws)
	"""
	
	"""
	ax = fig.add_subplot(3, 4, 10)
	megalut.plot.hexbin.hexbin(ax, cat, tru_g2, pre_s2, showidline=True, idlinekwargs=idkws)

	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.hexbin.hexbin(ax, cat, tru_g1, pre_s1, snr, showidline=True, idlinekwargs=idkws, cmap=cmap)

	ax = fig.add_subplot(3, 4, 12)
	megalut.plot.hexbin.hexbin(ax, cat, tru_g2, pre_s2, snr, showidline=True, idlinekwargs=idkws, cmap=cmap)
	"""

	"""
	ax = fig.add_subplot(2, 3, 4)
	megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1, snr, s=5, metrics=True, showidline=True, idlinekwargs=idkws, **sckws)

	ax = fig.add_subplot(2, 3, 5)
	megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2, snr, s=5, metrics=True, showidline=True, idlinekwargs=idkws, **sckws)
	"""

	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.

















def predsbe(run, filepath=None):
	
	cat =  megalut.tools.io.readpickle(os.path.join(run.workmldir, "obsprecat.pkl"))
		
	print cat.colnames
	#print len(cat)
	
	cat = megalut.tools.table.shuffle(cat)#[:100000]
	
	
	cat["tru_e"] = np.hypot(cat["Galaxy_e1"], cat["Galaxy_e2"])
	cat["tru_g"] = np.hypot(cat["Galaxy_g1"], cat["Galaxy_g2"])
	cat["psf_g"] = np.hypot(cat["tru_psf_g1"], cat["tru_psf_g2"])
	
	#cat["g1res"] = cat["pre_g1"] - cat["Galaxy_g1"]
	#cat["g2res"] = cat["pre_g2"] - cat["Galaxy_g2"]


	cmap = matplotlib.cm.get_cmap("rainbow")

	gresrad = 1.0		
	
	pre_g1 = Feature("pre_s1", -1, 1.5)
	pre_g2 = Feature("pre_s2", -1, 1.5)
	
	tru_g = Feature("tru_g")
	tru_e = Feature("tru_e")
	psf_g = Feature("psf_g")
	g1res = Feature("g1res", -gresrad, gresrad)
	g2res = Feature("g2res", -gresrad, gresrad)
	
	gal_e1 =  Feature("Galaxy_e1")
	gal_e2 =  Feature("Galaxy_e2")
	gal_g1 =  Feature("Galaxy_g1", -0.033, 0.033)
	gal_g2 =  Feature("Galaxy_g2")
	gal_size =  Feature("Galaxy_sigma_arcsec")
	psf_size =  Feature("tru_psf_sigma")
	
	gal_sn = Feature("Galaxy_SN")
	
	fig = plt.figure(figsize=(21, 12))
	"""
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, gal_e1, pre_g1, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)
	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.scatter.scatter(ax, cat, gal_e2, pre_g2, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)
	"""
	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.scatter.scatter(ax, cat, gal_g1, pre_g1, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)
	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.scatter.scatter(ax, cat, gal_g2, pre_g2, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)
	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.hist.hist(ax, cat, psf_g)
	
	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.hist.hist(ax, cat, psf_size)
	
	"""
	hexbinkwargs = {"mincnt":50}
	
	ax = fig.add_subplot(3, 4, 1)
	#megalut.plot.scatter.scatter(ax, cat, gal_e1, pre_g1, tru_e)
	megalut.plot.hexbin.hexbin(ax, cat, gal_e1, pre_g1, tru_e, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 2)
	#megalut.plot.scatter.scatter(ax, cat, gal_e2, pre_g2, tru_e)
	megalut.plot.hexbin.hexbin(ax, cat, gal_e2, pre_g2, tru_e, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 3)
	#megalut.plot.scatter.scatter(ax, cat, gal_g1, pre_g1, tru_e)
	megalut.plot.hexbin.hexbin(ax, cat, gal_g1, pre_g1, tru_e, **hexbinkwargs)
	
	
	ax = fig.add_subplot(3, 4, 4)
	#megalut.plot.scatter.scatter(ax, cat, gal_g2, pre_g2, tru_e)
	megalut.plot.hexbin.hexbin(ax, cat, gal_g2, pre_g2, tru_e, **hexbinkwargs)
	"""
	"""	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.hexbin.hexbin(ax, cat, gal_g1, g1res)

	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.hexbin.hexbin(ax, cat, gal_g1, g1res, gal_size, cmap=cmap)
	
	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.hexbin.hexbin(ax, cat, gal_g1, g1res, psf_size, cmap=cmap)
	"""
	
	#("in", "Galaxy_sigma_arcsec", 0.2, 0.4)("in", "Galaxy_SN", 1500, 3000)
	
	#("in", "tru_psf_sigma", 1.69, 1.71)
	s = megalut.tools.table.Selector("test",[
		("in", "psf_g", 0.0, 0.01)
		]) 
	
	selcat = s.select(cat)
	
	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.hist.hist(ax, selcat, psf_g)
	
	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.hist.hist(ax, selcat, psf_size)
	

	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.scatter.scatter(ax, selcat, gal_g1, pre_g1, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)
	ax = fig.add_subplot(3, 4, 8)
	megalut.plot.scatter.scatter(ax, selcat, gal_g2, pre_g2, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)
	
	
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.






def sbebias(run, filepath=None):

	cat =  megalut.tools.io.readpickle(os.path.join(run.workmldir, "obsprecat.pkl"))
		
	print cat.colnames
	print len(cat)
	
	gridsize = 6
	mincnt = 100
	
	gerrrad = 0.01
	relgerrrad = 25.0
	cmap = matplotlib.cm.get_cmap("rainbow")
	
	hexbinkwargs = {"gridsize":gridsize, "mincnt":mincnt, "cmap":cmap}

	
	cat["g1err"] = np.transpose(cat["pre_g1"].T - cat["Galaxy_g1"].T) # those T are the price to pay for having the rea as second index.
	cat["g2err"] = np.transpose(cat["pre_g2"].T - cat["Galaxy_g2"].T)
	
	cat["relg1err"] = 100.0*np.transpose(cat["g1err"].T / cat["Galaxy_g1"].T)
	cat["relg2err"] = 100.0*np.transpose(cat["g2err"].T / cat["Galaxy_g2"].T)
	
	cat["tru_sigma"] = 20.0*cat["Galaxy_sigma_arcsec"]
	
	
	g1err = Feature("g1err", -gerrrad, gerrrad, nicename="Bias on shear g1")
	g2err = Feature("g2err",-gerrrad, gerrrad, nicename="Bias on shear g2")
	relg1err = Feature("relg1err", -relgerrrad, relgerrrad, nicename="Rel. bias on shear g1 in %")
	relg2err = Feature("relg2err",-relgerrrad, relgerrrad, nicename="Rel. bias on shear g2 in %")

	pre_g1 = Feature("pre_g1", -1.0, 1.5, nicename="Predicted g1") # To get room for the metrics display...
	pre_g2 = Feature("pre_g2", -1.0, 1.5, nicename="Predicted g2")
	
	g1 = Feature("Galaxy_g1", nicename="True galaxy shear g1")
	g2 = Feature("Galaxy_g2", nicename="True galaxy shear g2")
	e1 = Feature("Galaxy_e1", nicename="True galaxy ellipticity e1")
	e2 = Feature("Galaxy_e2", nicename="True galaxy ellipticity e2")
	psfe1 = Feature("tru_psf_g1", nicename="True PSF ellipticity g1")
	psfe2 = Feature("tru_psf_g2", nicename="True PSF ellipticity g2")
	
	snr = Feature("snr")
	pre_sigma = Feature("pre_sigma")
	tru_sigma = Feature("tru_sigma")
	
	fig = plt.figure(figsize=(21, 12))
	
	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, g1, pre_g1, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)

	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.scatter.scatter(ax, cat, g2, pre_g2, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)

	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, relg1err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, relg2err, **hexbinkwargs)


	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.hexbin.hexbin(ax, cat, psfe1, psfe2, relg1err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.hexbin.hexbin(ax, cat, psfe1, psfe2, relg2err, **hexbinkwargs)
	
	
	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.scatter.scatter(ax, cat, tru_sigma, pre_sigma, showidline=True, idlinekwargs={"color":"red", "lw":2}, metrics=True)
	
	ax = fig.add_subplot(3, 4, 8)
	megalut.plot.hexbin.hexbin(ax, cat, tru_sigma, pre_sigma, bins="log", cblabel="log(counts)", gridsize=40, showidline=True, idlinekwargs={"color":"red", "lw":2})
	
	
	ax = fig.add_subplot(3, 4, 9)
	megalut.plot.hexbin.hexbin(ax, cat, g1, snr, relg1err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 10)
	megalut.plot.hexbin.hexbin(ax, cat, g2, snr, relg2err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.hexbin.hexbin(ax, cat, g1, tru_sigma, relg1err, **hexbinkwargs)

	ax = fig.add_subplot(3, 4, 12)
	megalut.plot.hexbin.hexbin(ax, cat, g2, tru_sigma, relg2err, **hexbinkwargs)
	
	
	
	"""
	
	psfselector = megalut.tools.table.Selector("Particular PSF",
		[("in", "tru_psf_g1", 0.00, 0.05), ("in", "tru_psf_g2", -0.01, 0.01)]) 
	psfselcat = psfselector.select(cat)


	ax = fig.add_subplot(3, 4, 9)
	megalut.plot.hexbin.hexbin(ax, psfselcat, g1, g2, g1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 10)
	megalut.plot.hexbin.hexbin(ax, psfselcat , g1, g2, g2err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.hexbin.hexbin(ax, psfselcat, g1, g2, adamomg1err, **hexbinkwargs)
	
	ax = fig.add_subplot(3, 4, 12)
	megalut.plot.hexbin.hexbin(ax, psfselcat, g1, g2, adamomg2err, **hexbinkwargs)
	"""
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.

