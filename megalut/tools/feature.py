"""
Helpers to specify a column of an astropy table.
"""

import numpy as np
import astropy.table

import logging
logger = logging.getLogger(__name__)


class Feature():
	"""
	This class holds a column name together with an interval to nicely show 
	this column values on plots, and also to select a given "realization" of a column.
	It's called "Feature", but it can well apply to any column of an astropy table (including "labels", in machine learning speak...).
	One can also specify a column name for the uncertainties (that will typically be shown as 1-sigma error bars).
	It is not tied to a particular table, nor to a particular plot: the same "Feature" object can be reused for different tables and plots.
	"""
	def __init__(self, colname, low=None, high=None, nicename=None, errcolname=None, rea=None):
		"""

		:param colanme: name of a catalog column containing the values to be plotted 
		:param low: (optional) lower bound of the interval to show on the plot
		:param high: (optional) higher bound
		:param nicename: (optional) a "nice" string designating the feature, to be used as axis label.
		:param errcolname: (optional) name of a column containing uncertainties / errorbars
		:param rea: specifies which realization to use, if several are available. "full" means all. 0 means first (etc), -5 means "the first 5 reas".
		:type rea: int or string
		
		"""
		
		self.colname = colname
		self.errcolname = errcolname
		self.low = low
		self.high = high
		
		self.rea = rea
		
		if nicename == None:
			self.nicename = self.colname
		else:
			self.nicename = nicename


	def err(self):
		"""
		Returns a new Feature describing the errcolname, if this was specified.
		This is useful to get one Feature per column that is required for a plot.
		"""
		if self.errcolname is not None:
			return Feature(self.errcolname, rea=self.rea)
		else:
			return None


	def get(self, cat, flatten=False):
		"""
		Returns the column corresponding to the feature, from the given catalog (as masked, if the column was masked).
		We don't do anything about the mask here.
		The point here is to get nice automatic behaviour even for 2D columns.
		If flatten is True, 2D columns are returned as flattened to 1D.
		Note that we use the default "C" order for this flattening. One could use "F", so that the output starts with the first realization of all the rows, then the second realization, etc.
		But any "inconsistency" in the catalog would already be done before. Switching to F only helps if we also change the way meas.avg.onsims stacks its stuff.
		
		"""
		
		
		if self.colname not in cat.colnames:
			raise RuntimeError("The column '%s' is not available in %s" % (self.colname, cat.colnames))
				
		if cat[self.colname].ndim == 1:
			# Things are easy, we don't need rea.
			# Let's check if there is a rea, this could be a mistake.
			if not self.rea is None:
				logger.warning("Feature {self.colname} has rea={self.rea} but the column is 1D!".format(self=self))
			output = cat[self.colname]
		
		elif cat[self.colname].ndim == 2:
		
			
			if cat[self.colname].shape[1] == 1: # Then in fact it's a 1D column, with just one value per cell...
				# We simply return the data from this colum, no need to care for rea.
				output = cat[self.colname] #.flatten() # Not sure if would be logic to flatten it here. No, why would you do that ?
			
			elif self.rea is None:
				raise RuntimeError("The column {self.colname} is 2D, please specify a rea for this feature!".format(self=self))
			
			elif type(self.rea) == int:
				
				if self.rea >= 0:
					output = cat[self.colname][:,self.rea]
					assert output.ndim == 1
					logger.info("Only using the particular rea {self.rea} of 2D colum '{self.colname}'".format(self=self))
					
				else: # Negative rea, means: use the first -rea realizations!
					
					#if -self.rea > cat[self.colname].shape[1]
					#	raise RuntimeError("Cannot select rea = {0} from a column with shape {1}".format(self.rea, cat[self.colname].shape))
				
					output = cat[self.colname][:,0:-self.rea]
					logger.info("Using the first {nrea}/{totrea} reas of 2D colum '{self.colname}'".format(self=self, nrea=-self.rea, totrea=cat[self.colname].shape[1]))
				
			elif self.rea in ["full", "Full", "All", "all"]:
				
				output = cat[self.colname]
				assert output.ndim == 2
				logger.info("Using the full {nrea} reas of 2D colum '{self.colname}'".format(self=self, nrea=cat[self.colname].shape[1]))
				
			else:
				raise RuntimeError("Could not understand rea={self.rea} of the feature {self.colname}.".format(self=self))
			
		else:
			raise RuntimeError("Weird column shape!")
		
		if output.ndim != 1 and flatten:
			return output.T.flatten()	
		else:
			return output
				

def get1Ddata(cat, features, keepmasked=True):
	"""
	Prepares 1D arrays of the same length, one for each feature.
	If features contains both 2D and 1D stuff, this is done by reapeating the 1D stuff. In other words, it intelligently flattens realizations.
	We don't do anything special about masks, they get carried arround as expected. Except if keepmasked is False, than we keep only unmasked points at the end.
	This is the function that you want to use when preparing plots or computing metrics...
	"""
	
	data = []
	for f in features:
		d = f.get(cat, flatten=True)
		assert d.ndim == 1
		data.append(d)
		
	lengths = [d.size for d in data]
	unilengths = list(set(lengths)) # Unique list of lenghts.
	
	
	fixeddata = []
	
	if len(unilengths) == 1: # Nothing special to do, then
		fixeddata = data	

	elif len(unilengths) == 2:
	
		small = min(unilengths)
		large = max(unilengths)
		(div, mod) = divmod(large, small)
			
		if mod != 0:
			raise RuntimeError("Cannot work with lengths %i and %i" % (large, small))
		
		logger.warning("Mild warning: some of the columns need to be tiled {0} times, and at this stage we cannot verify if the ordering of this tiling is as intended.".format(div))
		
		# We repeat the smaller column div times...
		for d in data:
			if d.size == small:
				fixedd = np.tile(d, div)
				assert fixedd.size == large
				fixeddata.append(fixedd)
			else:
				fixeddata.append(d)
	else:
		raise RuntimeError("Mixture is weird or too complicated: {0}".format(unilengths))
		
	assert len(fixeddata) == len(features)
	
	# We return this as a table.
	colnames = [f.colname for f in features]
	
	table1d = astropy.table.Table(fixeddata, names=colnames)
	
	
	if keepmasked == True:
		return table1d
		
	else:
		# We prepare a version of "features" with all reas set to 1D, so that we can use cutmasked:
		features1d = [Feature(colname=f.colname, rea=None) for f in features]
		return cutmasked(table1d, features1d)
	
	
	


def cutmasked(cat, features):
	"""
	Prepares a copy of cat containing only those rows for which none of the features is masked.
	To do this, it cleverly combines the masks.
	This is in principle close to what **numpy.ma.compress_rows** does.
	But here we also log a bit about the masked columns, and we take care of 2D columns by respecting the "rea" of Feature.

	
	:param cat: an astropy table
	:param features: a list of Feature objects
	
	:returns: a table containing only the available rows 
	
	"""
	
	if len(cat) == 0:
		raise RuntimeError("Give me a non-empty catalog.")
	# The first objective is to get a list of 1D masks, one per column.
	
	masklist = []
	colnames = []
	
	for f in features:
	
		column = f.get(cat)
		mask = np.array(np.ma.getmaskarray(column), dtype=bool)
		assert mask.ndim in [1, 2]
		if mask.ndim == 2: # This means if rea was "full"
			mask = np.any(mask, axis=1)
		assert mask.ndim == 1
		assert mask.size == len(cat)
		masklist.append(mask)
		colnames.append(f.colname)	
		
	
	# We now group all the masks into a single 2D array.
	assert len(colnames) == len(masklist)
	masks = np.column_stack(masklist)
	
	
	# Now we log some details about how many points are masked in each column.
	for (i, colname) in enumerate(colnames):
		mask = masks[:,i]
		assert len(mask) == len(cat)
		nbad = np.sum(mask)
		logger.info("Column %20s: %5i (%5.2f %%) of the %i entries are masked" \
			% ("'"+colname+"'", nbad, 100.0 * float(nbad) / float(len(cat)), len(cat)))
	
	# Now we combine the masks:
	combimask = np.logical_not(np.sum(masks, axis=1).astype(bool)) # So "True" means "keep this".
	assert combimask.size == len(cat)
	ngood = np.sum(combimask)
	nbad = combimask.size - ngood
	logger.info("Combination: %i out of %i (%.2f %%) rows have masked values and will be disregarded" \
		% (nbad, combimask.size, 100.0 * float(nbad) / float(combimask.size)))
	
	# We disregard the masked rows:
	nomaskcat = cat[combimask] # Only works as combimask is a numpy array ! It would do something else with a list !
	# Wow, this is extremely SLOW !
	# Note that everything so far also works for columns which are **not** masked. They will remain maskless.
	
	# More asserts:
	assert len(nomaskcat) == ngood
	#for colname in colnames:
	#	assert np.any(np.ma.getmaskarray(nomaskcat[colname])) == False # No item should be masked
	# No, as some other reas might be masked.	
	
	
	return nomaskcat


	
#	
#	"""
#	# Potentially, these columns can exist:	
#	colnames = []
#	for feature in features:
#		colnames.append(feature.colname)
#		if feature.errcolname != None:
#			colnames.append(feature.errcolname)
#	
#	colnames = list(set(colnames)) # To ensure that they are unique
#	
#	# Some trivial tests:
#	for colname in colnames:
#		if colname not in cat.colnames:
#			raise RuntimeError("The column '%s' is not available among %s" % (colname, str(cat.colnames)))
#	
#	"""
#	"""
#		#assert cat[colname].ndim == 1 # This function has not been tested for anything else...
#		# No, this is now beginnign to get implemented...
#			
#	if len(colnames) != len(list(set(colnames))):
#		raise RuntimeError("Strange, some colnames appear multiple times in %s" % (str(colnames)))
#	
#	# First, get a list of 1D masks, one per column
#	"""
#	
#	masklist = []
#	
#	print "Terrible hack, just uses mask of first rea if 2D !"
#	
#	for colname in colnames:
#		
#		mask = np.array(np.ma.getmaskarray(np.ma.array(cat[colname])), dtype=bool)
#		assert mask.ndim in [1, 2]
#		if mask.ndim == 2:
#			mask = mask[:,0] # Just get the first realization..
#			
#		assert mask.ndim == 1
#		assert mask.size == len(cat)
#		masklist.append(mask)
#	
#	# We now group all the masks for all these columns.
#	masks = np.column_stack(masklist)
#	
#	# This is a 2D boolean array. Now we log some details about how many points are masked in each column.
#	for (i, colname) in enumerate(colnames):
#		mask = masks[:,i]
#		assert len(mask) == len(cat)
#		nbad = np.sum(mask)
#		logger.info("Column %20s: %5i (%5.2f %%) of the %i entries are masked" \
#			% ("'"+colname+"'", nbad, 100.0 * float(nbad) / float(len(cat)), len(cat)))
#	
#	# Now we combine the masks:
#	combimask = np.logical_not(np.sum(masks, axis=1).astype(bool)) # So "True" means "keep this".
#	assert combimask.size == len(cat)
#	ngood = np.sum(combimask)
#	nbad = combimask.size - ngood
#	logger.info("Combination: %i out of %i (%.2f %%) rows have masked values and will be disregarded" \
#		% (nbad, combimask.size, 100.0 * float(nbad) / float(combimask.size)))
#	
#	# We disregard the masked rows:
#	nomaskcat = cat[combimask] # Only works as combimask is a numpy array ! It would do something else with a list !
#	# Wow, this is extremely SLOW !
#	# Note that everything so far also works for columns which are **not** masked. They will remain maskless.
#	
#	# More asserts:
#	assert len(nomaskcat) == ngood
#	for colname in colnames:
#		if hasattr(nomaskcat[colname], "mask"): # We make this test only if the column is masked
#			#assert np.all(np.logical_not(nomaskcat[colname].mask)) == True # Tests that all values are unmasked.
#			pass
#	
#	if not keep_all_columns:
#		nomaskcat.keep_columns(colnames)
#		# Moving this to before the slow "cat[combimask]" seems to not speedup this function -- strange ?
#	
#	return nomaskcat
#
