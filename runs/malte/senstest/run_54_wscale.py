import config
import numpy as np
import os

from megalut.tools.feature import Feature
import matplotlib.pyplot as plt
import megalut.plot


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

redo = False




def main():
	

	valname = "pred_{}".format(config.datasets["valid-overall"])
	predcatpath = os.path.join(config.valdir, valname + ".pkl")

	cat = megalut.tools.io.readpickle(predcatpath)
	#print megalut.tools.table.info(cat)
	

	for component in [1, 2]:
	
		trufeat = Feature("tru_s{}".format(component))
		predfeat = Feature("pre_s{}".format(component), rea=1) # We only take the first rea, to avoid SNC
		wfeat = Feature("pre_s{}w".format(component), rea=1)
		
		logger.info("Working on component {}...".format(component))
		wscale(cat, trufeat, predfeat, wfeat)
		
		#x = metcat[trufeat.colname]
		#y = metcat[predfeat.colname]
		#w = metcat[wfeat.colname]
		#metcat["sigfromw_{}".format(component)] = np.sqrt(1.0/np.clip(metcat["pre_s{}w".format(component)], 1e-18, 1e18)) # We don't want weights of exactly zero here.
		#metcat["esterror_{}".format(component)] = metcat[predfeat.colname] - metcat[trufeat.colname]
		#sigfromws
		
		"""
		fig = plt.figure(figsize=(10, 10))

		ax = fig.add_subplot(2, 2, 1)
		megalut.plot.bin.bin(ax, metcat, Feature("pre_s{}w".format(component)), Feature("bias"), yisres=True, showidline=True)

		ax = fig.add_subplot(2, 2, 2)
		megalut.plot.scatter.scatter(ax, metcat, Feature("pre_s{}w".format(component)), Feature("bias"))
		plt.tight_layout()

		plt.show()
		plt.close(fig) # Helps releasing memory when calling in large loops.
		"""
		#exit()
		#megalut.tools.table.addstats(cat, "pre_s{}".format(component), "pre_s{}w".format(component))
		#megalut.tools.metrics.wmetrics(cat, Feature("tru_s{}".format(component)), Feature("pre_s{}_wmean".format(component)), wfeat=Feature("pre_s{}_wmeanw".format(component)))
	



def wscale(cat, trufeat, predfeat, wfeat, showplot=False):
	"""
	We compute a scale factor to multiply the weights with so that weights = 1 / sigma**2
	For this the catalog is flattened out and bins in w are made.
	The shear distribution should not really matter
	"""
	logger.info("Working out wscale for {}...".format(wfeat.colname))
	
	metcat =  megalut.tools.feature.get1Ddata(cat, [trufeat, predfeat, wfeat], keepmasked=False)
	#print megalut.tools.table.info(metcat)
	
	metcat["sigfromw"] = np.sqrt(1.0/np.clip(metcat[wfeat.colname], 1e-18, 1e18)) # We don't want weights of exactly zero here.
	metcat["esterror"] = metcat[predfeat.colname] - metcat[trufeat.colname]
	
	
	# The median-weight-matching: simple idea
	# Get range of weights around median weight:
	
	a = np.percentile(metcat[wfeat.colname], 45)
	b = np.percentile(metcat[wfeat.colname], 55)
	logger.info("Percentiles: {} {}".format(a, b))
	
	s = megalut.tools.table.Selector("wbin", [
		("in", wfeat.colname, a, b),
	])
	selcat = s.select(metcat)
	messtd = np.ma.std(selcat["esterror"])
	meanw = (a + b) / 2.0
	logger.info("Measured shear est error std: {}".format(messtd))
	logger.info("Mean w: {}".format(meanw))
	logger.info("Actual mean w: {}".format(np.ma.mean(selcat[wfeat.colname])))
	
	ratio = (1.0 / (messtd**2)) / meanw
	logger.info("ratio = {}".format(ratio))
	
	if showplot is False:
		return ratio
	
	
	metcat[wfeat.colname] = ratio * metcat[wfeat.colname]
	metcat["sigfromw"] = np.sqrt(1.0/np.clip(metcat[wfeat.colname], 1e-18, 1e18))

	
	
	binrange = (0, 1*ratio)
	nbins = 100
	
	binlims = np.linspace(binrange[0], binrange[1], nbins+1)
	bincenters = 0.5 * (binlims[0:-1] + binlims[1:])
	assert len(bincenters) == nbins
	
	binindices = np.digitize(metcat[wfeat.colname], bins=binlims)
	
	inrangeindices = np.arange(nbins)+1 # the indices that are within the binlims
	assert len(inrangeindices) == nbins
		
	esterrormeans = []
	esterrorstds = []
	wmeans = []
	sigfromwmeans = []
	ns = []
		
	for ind in inrangeindices: # We loop over the bins
		
		inbools = binindices == ind # a boolean array
		nin = np.sum(inbools)
		
		if nin < 20:
			esterrormeans.append(np.nan)
			esterrorstds.append(np.nan)
			ns.append(nin)
			wmeans.append(np.nan)
			sigfromwmeans.append(np.nan)
			continue
		
		ns.append(nin)
		
		esterrormeans.append(np.ma.mean(metcat["esterror"][inbools]))
		esterrorstds.append(np.ma.std(metcat["esterror"][inbools]))
		
		wmeans.append(np.ma.mean(metcat[wfeat.colname][inbools]))
		sigfromwmeans.append(np.ma.mean(metcat["sigfromw"][inbools]))
	
	
	for l in [esterrormeans, esterrorstds, wmeans, sigfromwmeans, ns]:	
		assert len(l) == nbins
		

	#print wmeans
	
	fig = plt.figure(figsize=(10, 10))
	
	ax = fig.add_subplot(2, 2, 1)
	megalut.plot.hist.hist(ax, metcat, Feature(wfeat.colname))
	
	ax = fig.add_subplot(2, 2, 2)
	megalut.plot.scatter.scatter(ax, metcat, Feature(wfeat.colname), Feature("esterror"))
	
	
	ax = fig.add_subplot(2, 2, 3)
	#ax.scatter(wmeans, esterrorstds)
	#ax.set_xlabel("weight")
	#ax.set_ylabel("std(shear pred errors)")
	megalut.plot.hist.hist(ax, metcat, Feature("sigfromw"))
	
	ax = fig.add_subplot(2, 2, 4)
	#megalut.plot.hist.hist(ax, metcat, Feature("sigfromw"), normed=True)
	ax.scatter(sigfromwmeans, esterrorstds)
	
	ax.set_xlabel("1/sqrt(weight)")
	ax.set_ylabel("std(shear pred errors)")
	
	plt.show()
	
	
	

if __name__ == "__main__":
    main()
