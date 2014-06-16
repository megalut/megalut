"""
Functions to flag galaxies according to general criteria

Some demo constraints :

constraints = [
megalut.galflag.Interval(attr="pre_rad", minval=0.8),
megalut.galflag.Polygon(attrs=("mes_snr", "mes_gs_sizeratio"), points=[(25, 2), (15, 3), (15, 7), (45, 7), (45, 2)])
]

"""

import galaxy
	
try:
	import shapely.geometry
except:
	print "I can't import shapely: not a problem if you don't use it."
	print "To install, try"
	print "pip install --user Shapely"

	

class Interval:

	def __init__(self, attr, minval=None, maxval=None):
		"""
		minval and maxval are optional. Specify only one of them to test only upper or lower bounds...
		"""
		self.attr = attr
		self.minval = minval
		self.maxval = maxval
	
	
	def test(self, galaxy):
		"""
		Tests a galaxy. Returns True if the galaxy is in the interval, False if it is outside.
		"""
		
		if not hasattr(galaxy, self.attr):
			print "WARNING, DON'T HAVE %s" % (self.attr)
			return True
		
		if self.minval != None:
			if getattr(galaxy, self.attr) < self.minval:
				return False
				
		if self.maxval != None:
			if getattr(galaxy, self.attr) > self.maxval:
				return False
				
		return True
		
	
class Polygon:
	

	def __init__(self, attrs, points):
		"""
		attrs is a tuple (attr1, attr2)
		points is a list of tuples (x, y) with the corners of the polygons.
		This list will be closed automatically
		For full info, see
		http://toblerity.org/shapely/manual.html#polygons
		
		"""
		self.attrs = attrs
		self.points = points
		
		self.poly = shapely.geometry.Polygon(self.points)
		

	def test(self, galaxy):
		"""
		Tests a galaxy. Returns True if the galaxy is inside of the polygon, False if it is outside.
		"""
		
		if not (hasattr(galaxy, self.attrs[0]) and hasattr(galaxy, self.attrs[1])):
			print "WARNING, DON'T HAVE %s" % (str(self.attrs))
			return True

		p = shapely.geometry.Point(getattr(galaxy, self.attrs[0]), getattr(galaxy, self.attrs[1]))
		
		if not self.poly.contains(p):
			return False
		else:
			return True
		


def setflag(galaxies, constraints):
	"""
	constraints is a list of Intervals and Polygons.
	Sets flag to 1 for all galaxies which are *outside* of the constraints.
	"""
	
	for g in galaxies:
		
		g.flag = 0
		
		for c in constraints:
		
			if c.test(g) == False:
				g.flag = 1
				
				
			
