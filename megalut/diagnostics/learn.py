import numpy as np
import matplotlib.pyplot as plt
from .. import plot
from .. import tools
from astropy.table import Table

class learn():
	
	def __init__(self, myml, inputcat):
		self.myml = myml
		
		self.inputcat = inputcat
		
		traincat = myml.predict(inputcat)
		self.validationcat = traincat[myml.training_set_index:]
		self.traincat = traincat[:myml.training_set_index]
		
		if np.size(self.validationcat) == 0:
			raise ValueError("There is no validation set")

	def compare_distrib(self, fig, prelabels=None, error=False, trulabels=None, fit_linreg=True,
					fitlinekwargs=None, titles=None, show_id_line=True, idlinekwargs=None, **kwargs):
		
		if prelabels is None:
			prelabels = [item for item in self.traincat.colnames if item.startswith('pre')]
			if error:
				trulabels = ["tru" + i[3:] for i in prelabels]
		
		total = len(prelabels)
		assert total < 10
		
		for i in range(len(prelabels)):
			datax = self.traincat
			datay = self.validationcat
			
			if error:
				newlabel = "RMSD %s" % prelabels[i]
				
				datax = datax[prelabels[i]]-datax[trulabels[i]]
				datax = np.ma.sqrt(datax*datax)
				datax = Table([datax], names=[newlabel])
				
				datay = datay[prelabels[i]]-datay[trulabels[i]]
				datay = np.ma.sqrt(datay*datay)
				datay = Table([datay], names=[newlabel])
				
				prelabels[i] = newlabel
			
			feat = plot.feature.Feature(prelabels[i])
			
			plot_id = 100 + total * 10 + i + 1
			
			ax = fig.add_subplot(plot_id)
		
			xx, yy = plot.qqplot.qqplot2dataset(ax, datax, datay, feat, **kwargs)
			
			if show_id_line: # Show the "diagonal" identity line
				
				# For "low":
				minid = max(np.min(datax[prelabels[i]]), np.min(datay[prelabels[i]]))
				# Same for "high":
				maxid = min(np.max(datax[prelabels[i]]), np.max(datay[prelabels[i]]))
					
				if idlinekwargs == None:
					idlinekwargs = {}
				myidlinekwargs = {"ls":"--", "color":"gray", "lw":1}
				myidlinekwargs.update(idlinekwargs)	
				
				# And we plot the line:
				ax.plot((minid, maxid), (minid, maxid), **myidlinekwargs)
				
				if not error:
					ax.axvline(0, **myidlinekwargs)
					ax.axhline(0, **myidlinekwargs)
						
			if fit_linreg:
				ret = tools.calc.linreg(xx,yy)
				
				# And we plot the line:
				if fitlinekwargs == None:
					fitlinekwargs = {}
				myfitlinekwargs = {"ls":"--", "color":"red", "lw":1}
				myfitlinekwargs.update(fitlinekwargs)	
				
				dx = np.array([np.amin(xx), np.amax(xx)])

				ax.plot(dx, dx * (ret['m'] + 1) + ret['c'], **myfitlinekwargs)
				
				ax.annotate("Slope = %1.3f\nIntercept = %1.3f" % (ret['m'] + 1, ret['c']), 
						xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), 
						textcoords='offset points', ha='left', va='top')
			
			if i == 0:
				plt.xlabel("Train set quantiles")
				plt.ylabel("Cross-validation set quantiles")
			
			if titles is None:
				ax.set_title(prelabels[i])
			else:
				ax.set_title(titles[i])
				
		
			plt.grid()
