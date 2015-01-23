import numpy as np
import matplotlib.pyplot as plt
from .. import plot
from .. import tools
from astropy.table import Table, vstack
import multiprocessing
import copy

import logging
logger = logging.getLogger(__name__)

class Learn():
	"""
	The class containing the diagnostics for testing the robustness of the learning
	"""
	
	def __init__(self, ml, inputcat):
		"""
		:param ml: a ML instance
		:param inputcat: the input astropy table used for training
		"""
		self.ml = ml
		
		self.inputcat = inputcat
		
		traincat = ml.predict(inputcat)
		self.validationcat = traincat[ml.training_set_index:]
		self.traincat = traincat[:ml.training_set_index]
		
		if np.size(self.validationcat) == 0:
			raise ValueError("There is no validation set")
		
		# Declare that the training on different size has not been done.
		self.errors_training_size = None
		
	def __str__(self):
		txt = "Diagnostics on the %s ML algorithm" % self.ml.mlparams.__str__() + \
		"\nUsing %s" % self.ml.toolparams.__str__() + \
		"\nWith %d training samples and %d cross-validation samples." % (np.shape(self.traincat)[0],
														np.shape(self.validationcat)[0],)
		return txt

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
			
	def is_overfitting(self, threshold=0.05):
		"""
		Returns a simple estimation of the overfit (True/False) if the variance error is larger than
			the threshold*training_error.
		"""
		
		logger.info("Training error is %g" % self.ml.train_error)
		logger.info("Cross-validation error is %g" % self.ml.validation_error) 
		
		delta = self.ml.validation_error-self.ml.train_error
		
		if delta < 0 :
			logger.warning("The training error is larger than validation error, something's wrong")
		
		mag = delta/self.ml.train_error
		msg = "Variance is %2.1f%% of the training error." % (100.*mag)
		if mag > threshold:
			logger.warning(msg+" That's a lot!")
			return True
		else:
			logger.info()
			return False
		
	def test_training_size(self, fig, fractions=[0.2, 0.4, 0.6, 0.8, 1.], ncpu=1, **kwargs):
		
		logger.info("Beginning the test on different training sample size")
		
		cat = vstack([self.traincat, self.validationcat])
		
		if self.errors_training_size is None or not self.fractions_training_size == fractions:
			trainparams = [[f, copy.deepcopy(self.ml), \
				cat[:np.int(f * np.shape(cat)[0])]] for f in fractions]
			
			if ncpu == 1: # The single-processing version, much easier to debug !
				res = map(_trainer_size, trainparams)
		
			else: # The simple multiprocessing map is:
				print "multi-cpu"
				pool = multiprocessing.Pool(processes=ncpu)
				res = pool.map(_trainer_size, trainparams)
				pool.close()
				pool.join()
			
			res = np.sort(np.asarray(res), axis=0)
			self.errors_training_size = res
			self.fractions_training_size = np.asarray(fractions) * (1. - self.ml.validation_fraction)
			
		mykwargs = {"marker":"+", "ms":5, "ls":"--", "alpha":1.}
		mykwargs.update(kwargs)
		mykwargs.update({'color':"blue"})

		print self.fractions_training_size
		xx = self.fractions_training_size * np.shape(cat)[0]
		print xx
		plt.plot(xx, self.errors_training_size[:,1], label="Training set", **mykwargs)
		
		mykwargs.update({'color':"green"})
		plt.plot(xx, self.errors_training_size[:,2], label="Cross-validation set", **mykwargs)
		plt.grid()
		plt.legend(loc="best")
		plt.xlabel("Training set size")
		plt.ylabel("%s RMS error" % (self.ml.toolparams.name))
		
def _trainer_size(params):
	frac, ml, cat = params
	ml.train(cat)
	return frac, ml.train_error, ml.validation_error

