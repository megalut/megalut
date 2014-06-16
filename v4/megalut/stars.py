import copy as pythoncopy
import numpy as np
import asciidata
#import astropy.io.ascii

class Star:
	"""
	Represents a star and all its information, can generate PSF from star.
	"""
	__current_id = 0

	def __init__(self):
		
		# The information given in the catalogs
		self.ID = Star.__current_id + 1 # This is an int unique to each star.
		Star.__current_id += 1
		self.x = 0.0
		self.y = 0.0
		self.x_tile_index = 0
		self.y_tile_index = 0
		self.x_tile_true_deg = 0.0
		self.y_tile_true_deg = 0.0
		self.x_field_true_deg = 0.0
		self.y_field_true_deg = 0.0
	
		self.reset()
	
	def reset(self):
		"""
		This method *defines* the attributes that we will use.
		"""
		
		# The measured information, from the shape measurement on the observed image
		self.mes_x = 0.0
		self.mes_y = 0.0
		self.mes_a = 0.0
		self.mes_b = 0.0
		self.mes_theta = 0.0 # Sextractor : from -90 to 90 deg
		self.mes_fwhm = 0.0
		self.mes_flux = 0.0
		self.mes_fluxerr = 0.0
		self.mes_flux_max = 0.0

		self.mes_sky = 0.0
		self.mes_sig = 0.0
		
	
	def __str__(self):
		return "Star ID %i at (%.1f, %.1f)" % (self.ID, self.x, self.y) 
	
	
	def isgood(self):
		"""
		Returns True if the star has been well-measured.
		"""
		answer = True
		
		if self.mes_flux <= 0.0:
			answer = False

		return answer
	
	
	def copy(self):
		"""
		Returns a copy of myself
		"""
		return pythoncopy.deepcopy(self)
													

	
	def getattrs(self, attrlist):
		"""
		Returns "raw" data for machine learning, features or labels
		"""
		return np.array([getattr(self, attr) for attr in attrlist])
		
		
	def setattrs(self, data, attrlist, id_array=None):
		"""
		The inverse of getattrs
		"""
		assert len(data) == len(attrlist)
		for d, attr in zip(data, attrlist):
			if id_array == None: setattr(self, attr, d)
			else:getattr(self, attr)[id_array] = d # Setting 1d array elements

	def snr(self):
		return self.mes_flux/self.mes_fluxerr

	def isbrighter(self, snr):
		return self.snr()/snr>=1.

	def get_xy_tile(self):
		return [self.x_tile_index, self.y_tile_index]

	def get_xy_field_deg(self):
		return [self.x_field_true_deg, self.y_field_true_deg]

	def get_xy_tile_deg(self):
		return [self.x_tile_true_deg, self.y_tile_true_deg]

	def info(self):
		"""
		Prints out all the variables for a given star of the class
		"""
		import inspect
	
		message = "All variables available for star ID %i" % self.ID		
		print message
		print '-'*len(message)
		attributes = inspect.getmembers(self, lambda a:not(inspect.isroutine(a)))
		for a in attributes:
			if (a[0].startswith('__') and a[0].endswith('__')): continue
			print a[0], "=", a[1]

	

def fitsformat(element):

	if isinstance(element, (int, long)):
		return "J"
	elif isinstance(element, str):
		return "20A"
	else:
		return "D"
		
	#else:
	#	raise RuntimeError("Teach me !")



def convert(g, a):
	try:
		return float(getattr(g, a, 999.0))
	except:
		print "Export convert problem !"
		print getattr(g, a, 999.0)
		return 999.0

def export(stars, filepath):
	"""
	Saves the stars into a FITS table for interactive inspection with tools like topcat
	
	
	"""
	import inspect
	try:
		import pyfits
	except:
		print "pyfits could not be imported, no problem if you don't need it."
	
	allattributes = set([])
	for s in stars:
		s.good = s.isgood()
		
		
		attributes = inspect.getmembers(s, lambda a:not(inspect.isroutine(a)))
		attributes = set([a[0] for a in attributes if not(a[0].startswith('__') and a[0].endswith('__')) and not 'committee' in a[0]])
		
		allattributes = attributes.union(allattributes)
		
	cols = [pyfits.Column(name=a, format="D", array=np.array([convert(s, a) for s in stars])) for a in sorted(list(allattributes))]
	
	coldefs = pyfits.ColDefs(cols)
	tbhdu = pyfits.new_table(coldefs)
	tbhdu.writeto(filepath, clobber=True)
	print "Wrote %s" % (filepath)
	

	
	
	



