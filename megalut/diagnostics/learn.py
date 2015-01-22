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
		:param prelabels: a list of features containing all the columns to show. If set to None, will find automatically
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
			# Construct the feature object to select the right column in the astopy table
			prelabels = [plot.feature.Feature(f) for f in prelabels] 
			
			if error:
				trulabels = ["tru" + i.colname[3:] for i in prelabels]
				trulabels = [plot.feature.Feature(f) for f in trulabels] 
		
		total = len(prelabels)
		
		# Make a few security checks
		assert total < 10
		if error and not len(prelabels) == len(trulabels):
			raise RuntimeError("Your lists prelabels and trulabels do not have the same size")
		
		if (titles is not None) and (not len(prelabels) == len(titles)):
			raise RuntimeError("Your lists prelabels and titles do not have the same size")
		
		# Start plotting
		for i in range(len(prelabels)):
			# Shorthand notation
			datax = self.traincat
			datay = self.validationcat
			
			prelab = prelabels[i].colname
			
			# If error, then compute the RMSD and build a new astropy array
			if error:
				newlabel = "RMSD %s" % prelab
				
				datax = datax[prelab]-datax[trulabels[i].colname]
				datax = np.ma.sqrt(datax*datax)
				datax = Table([datax], names=[newlabel])
				
				datay = datay[prelab]-datay[trulabels[i].colname]
				datay = np.ma.sqrt(datay*datay)
				datay = Table([datay], names=[newlabel])
				
				prelab = newlabel
				prelabels[i].colname = newlabel
			
			# Handles the subplot number
			plot_id = 100 + total * 10 + i + 1
			
			ax = fig.add_subplot(plot_id)
		
			# Actually draws the QQ plot
			xx, yy = plot.qqplot.qqplot2dataset(ax, datax, datay, prelabels[i], **kwargs)
			
			if show_id_line: # Show the "diagonal" identity line
				
				# For "low":
				minid = max(np.min(datax[prelab]), np.min(datay[prelab]))
				# Same for "high":
				maxid = min(np.max(datax[prelab]), np.max(datay[prelab]))
					
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
				ax.set_title(prelab)
			else:
				ax.set_title(titles[i])
				
			# Make sure we don't have negative values in error plots...
			if error:
				cur_ylim = ax.get_ylim()
				ax.set_ylim([0, cur_ylim[1]])
				
				cur_xlim = ax.get_xlim()
				ax.set_xlim([0, cur_xlim[1]])
				
		
			plt.grid()

	def compare_density(self, fig, prelabels=None, trulabels=None, fit_linreg=True, fitlinekwargs=None):
		"""
		Make a density plot of the predictions after the training of the training and cross-validation set
		
		:param fig: a figure instance of pyplot
		:param prelabels: a list of features containing all the columns to show. If set to None, will find automatically
			the columns to plot
		:param trulabels: the corresponding columns for `prelabels`, same None behaviour.
		:param fit_linreg: Fits and shows a linear fit with error bar.
		:param fitlinekwargs: kwargs for `fit_linreg`
		"""
		
		# Get all the colnames that start by "pre" and construct the prelabels if needed
		if prelabels is None:
			prelabels = [item for item in self.traincat.colnames if item.startswith('pre')]	
			# Construct the feature object to select the right column in the astopy table
			prelabels = [plot.feature.Feature(f) for f in prelabels] 
			
			trulabels = ["tru" + i.colname[3:] for i in prelabels]
			trulabels = [plot.feature.Feature(f) for f in trulabels]
			 
			deltalabels = ["delta" + i.colname[3:] for i in prelabels]
			deltalabels = [plot.feature.Feature(f) for f in deltalabels]
		
		total = len(prelabels)
		
		# Make a few security checks
		assert total < 10
		if not len(prelabels) == len(trulabels):
			raise RuntimeError("Your lists prelabels and trulabels do not have the same size")
		
		if not len(prelabels) == len(trulabels):
			raise RuntimeError("Your lists prelabels and trulabels do not have the same size")
		
		# And we plot the line:
		if fitlinekwargs == None:
			fitlinekwargs = {}
		myfitlinekwargs1 = {"ls":"--", "color":"black", "lw":2}
		myfitlinekwargs1.update(fitlinekwargs)	
		
		myfitlinekwargs2 = myfitlinekwargs1.copy()
		myfitlinekwargs2.update({"color":"darkblue", "ls":"-"})
		
		def _plot_helper(ax, cat, featx, featy, fit_linreg, **kwargs):
			xx = cat[featx.colname]
			yy = cat[featy.colname]
			
			plot.hexbin.hexbin(ax, cat, featx, featy, makecolorbar=False)
			
			if fit_linreg:
				ret = tools.calc.linreg_on_masked_array(xx, yy)
				dx = np.array([np.amin(xx), np.amax(xx)])
				dy = dx * (ret['m'] + 1) + ret['c']
			
				sig = np.std(yy - xx * (ret['m'] + 1) + ret['c'])
				ax.fill_between(dx, dy - sig, dy + sig, color=kwargs['color'], alpha=0.3)
				ax.plot(dx, dy, **kwargs)
			
			plt.grid()
			
			return dx, dy, sig
		
		# Start plotting
		for i in range(len(prelabels)):

			# Handles the subplot number
			plot_id = total * 100 + 20 + 2*i + 1

			ax1 = fig.add_subplot(plot_id)

			dx, dy, sig = _plot_helper(ax1, self.traincat, trulabels[i],
									prelabels[i], fit_linreg, **myfitlinekwargs1)
			
			if i == 0:
				ax1.set_title("Train set")
			
			# Handles the subplot number
			plot_id = total * 100 + 20 + 2*i + 2
			
			ax2 = fig.add_subplot(plot_id)
			featx = plot.feature.Feature(trulabels[i].colname, nicename='')
			featy = plot.feature.Feature(prelabels[i].colname, nicename='')
			_plot_helper(ax2, self.validationcat, featx, featy, fit_linreg, **myfitlinekwargs2)

			if fit_linreg:
				ax2.fill_between(dx, dy - sig, dy + sig, 
                	 color=myfitlinekwargs1['color'], alpha=0.3)
				ax2.plot(dx, dy, **myfitlinekwargs1)
			
			if i == 0:
				ax2.set_title("Cross-validation set")

			plt.setp(ax2.get_yticklabels(), visible=False)
			
		plt.subplots_adjust(wspace = .001)
		plt.subplots_adjust(hspace = .3)
			