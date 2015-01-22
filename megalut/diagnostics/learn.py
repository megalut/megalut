import numpy as np
import matplotlib.pyplot as plt
from .. import plot
from .. import tools
from astropy.table import Table

class Learn():
	"""
	The class containing the diagnostics for testing the robustness of the learning
	"""
	
	def __init__(self, myml, inputcat):
		"""
		:param myml: a ML instance
		:param inputcat: the input astropy table used for training
		"""
		self.myml = myml
		
		self.inputcat = inputcat
		
		traincat = myml.predict(inputcat)
		self.validationcat = traincat[myml.training_set_index:]
		self.traincat = traincat[:myml.training_set_index]
		
		if np.size(self.validationcat) == 0:
			raise ValueError("There is no validation set")

	def compare_distrib(self, fig, prelabels=None, error=False, trulabels=None, fit_linreg=True,
					fitlinekwargs=None, titles=None, show_id_line=True, idlinekwargs=None, **kwargs):
		"""
		Make a QQ-plot of the predictions after the training of the training and cross-validation set
		
		:param fig: a figure instance of pyplot
		:param prelabels: a list containing all the columns to show. If set to None, will find automatically
			the columns to plot
		:param error: if set to `True`, will show the RMSD from the truth, else simply the distribution of the prediction
		:param trulabels: the corresponding columns for `prelabels` if `error` is `True`, same None behaviour.
		:param fit_linreg: Fits and shows a linear fit through the QQ-plot.
		:param fitlinekwargs: kwargs for `fit_linreg`
		:param titles: must be of the same lenght as `prelabels`, contains the titles of the subplots
		:param show_id_line: shows the identity line
		:param idlinekwargs: kwargs for show_id_line
		
	
		All further **kwargs** are passed to axes.plot()
		"""
		
		# Get all the colnames that start by "pre" and construct the prelabels if needed
		if prelabels is None:
			prelabels = [item for item in self.traincat.colnames if item.startswith('pre')]
			if error:
				trulabels = ["tru" + i[3:] for i in prelabels]
		
		total = len(prelabels)
		
		# Make a few security checks
		assert total < 10
		if not len(prelabels) == len(trulabels):
			raise RuntimeError("Your lists prelabels and trulabels do not have the same size")
		
		if (titles is not None) and (not len(prelabels) == len(trulabels)):
			raise RuntimeError("Your lists prelabels and trulabels do not have the same size")
		
		# Start plotting
		for i in range(len(prelabels)):
			# Shorthand notation
			datax = self.traincat
			datay = self.validationcat
			
			# If error, then compute the RMSD and build a new astropy array
			if error:
				newlabel = "RMSD %s" % prelabels[i]
				
				datax = datax[prelabels[i]]-datax[trulabels[i]]
				datax = np.ma.sqrt(datax*datax)
				datax = Table([datax], names=[newlabel])
				
				datay = datay[prelabels[i]]-datay[trulabels[i]]
				datay = np.ma.sqrt(datay*datay)
				datay = Table([datay], names=[newlabel])
				
				prelabels[i] = newlabel
			
			# Construct the feature object to select the right column in the astopy table
			feat = plot.feature.Feature(prelabels[i])
			
			# Handles the subplot number
			plot_id = 100 + total * 10 + i + 1
			
			ax = fig.add_subplot(plot_id)
		
			# Actually draws the QQ plot
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
						
			if fit_linreg: # Show the fit line
				ret = tools.calc.linreg(xx,yy)
				
				# And we plot the line:
				if fitlinekwargs == None:
					fitlinekwargs = {}
				myfitlinekwargs = {"ls":"--", "color":"red", "lw":1}
				myfitlinekwargs.update(fitlinekwargs)	
				
				dx = np.array([np.amin(xx), np.amax(xx)])

				ax.plot(dx, dx * (ret['m'] + 1) + ret['c'], **myfitlinekwargs)
				
				# Show the slope and intercept value
				text = r"Slope $%1.3f\pm%1.3f$" % (ret['m'] + 1, ret['merr']) + "\n"
				text += r"Intercept $%1.3f\pm%1.3f$" % (ret['c'], ret['cerr'])
				ax.annotate(text, 
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
