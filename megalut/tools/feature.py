
class Feature():
	"""
	This class holds a column name together with an interval to nicely show 
	this column values on plots.
	One can also specify a column name with uncertainties (that will typically be shown as 1-sigma error bars).
	It is not tied to a particular table, nor to a particular plot: the same "Feature" object can be reused for different tables and plots.
	"""
	def __init__(self, colname, low=None, high=None, nicename=None, errcolname=None):
		"""

		:param colanme: name of a catalog column containing the values to be plotted 
		:param low: (optional) lower bound of the interval to show on the plot
		:param high: (optional) higher bound
		:param nicename: (optional) a "nice" string designating the feature, to be used as axis label.
		:param errcolname: (optional) name of a column containing uncertainties / errorbars 
		
		"""
		
		self.colname = colname
		self.errcolname = errcolname
		self.low = low
		self.high = high
		
		if nicename == None:
			self.nicename = self.colname
		else:
			self.nicename = nicename




	def get(self, cat, rea=0):
		"""
		Returns the feature data from the given catalog, including its masks.
		The point here is to get nice automatic behaviour even for 2D columns.
		"""
		
		if self.colname not in cat.colnames:
			raise RuntimeError("The column '%s' is not available in %s" % (self.colname, cat.colnames))
				
		if cat[self.colname].ndim == 1:
			return cat[self.colname]
		
		if cat[self.colname].ndim == 2:
			return cat[self.colname][:,rea]
		
