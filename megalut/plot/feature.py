class Feature():
	"""
	A feature is essentially a column name together with an interval to nicely show 
	this column on plots.
	"""
	def __init__(self, colname, low=None, high=None, nicename=None, ):
		"""

		:param colanme: name of a column 
		:param low: lower bound of the interval to show on the plot.
		:param high: higher bound
		:param nicename: A nicer string designating the feature, to be used as axis label.
		"""
		
		self.colname = colname
		self.low = low
		self.high = high
		
		if nicename == None:
			self.nicename = self.colname
		else:
			self.nicename = nicename
