"""
This module defines a simple catalog structure which we use accross MegaLUT.
A catalog is simply a dict (or a list, depending on what we do) of Galaxy objects.
"""

import copy as pythoncopy

class Galaxy:
	"""
	Represents a galaxy and all its information.
	"""

	def __init__(self, id="0"):
		"""
		Minimal constructor.
		The pythonic way is to avoid type checking. But in principle, we expect id to be a string...
		The minimal fields given here should always exist.	
		"""
		self.id = id
		"""A unique identification for this galaxy (typically a string)"""
		
		self.fields = {}
		"""A dict to hold all the data"""
	
	
	def __str__(self):
		"""
		A oneliner, using only the minimal fields
		"""
		return "Galaxy %s with %i fields" % (str(self.id), len(self.fields)) 
		
		
	def copy(self):
		"""
		Returns a copy of myself
		"""
		return pythoncopy.deepcopy(self)
													
				
	def getarray(self, keys):
		"""
		Returns numerical field values in form a numpy array. Useful for instance to feed machine learning, both for features or labels.
		
		:param keys: a list of field names
		
		"""
		# We could check that everything is float / int / numeric here ? I guess better not.
		
		try: 
			return np.array([self.fields.get(self, key) for key in keys])
		except TypeError as err:
			print "Give me a list of keys, not a single key !"
			raise err
			
		
	def setarray(self, array, keys, overwritewarning=True):
		"""
		The inverse of getarray. Useful for instance to write some predicted data into the catalog.
		
		:param array: array or list containing the data
		:param keys: list of keys that should be used to store this data
		:param overwritewarning: If set to False, I do not complain if you ask me to overwrite existing fields.
		
		"""
		assert len(array) == len(keys)
		for val, key in zip(array, keys):
			if overwritewarning:
				if key in self.fields:
					# We need a logging system here !
					raise RuntimeError("I should not overwrite the existing field %s!" % (key))
			
			self.fields[key] = val

			
	def info(self):
		"""
		Prints out all the fields
		"""
		print "%s:" % str(self)
		for (key, val) in self.fields.iteritems():
			print "%20s: %s" % (str(key), str(val))
		



class Catalog:
	"""
	A class containing a dict of galaxies, using the ids as keys, and a dict of metadata.
	The constructor takes a list of galaxies as input, and optionally a dict containing meta information about those galaxies.
	
	I though that for convenience, this guy should be iterable: for galaxy in catalog
	Let's test this. It might be too dangerous, confusions between list and dict, random ordering etc.
	
	"""

	def __init__(self, galaxies, meta=None):
		
		# We check that the ids are unique:
		assert len(galaxies) == len(set([gal.id for gal in galaxies])), "Your galaxies have non-unique ids !"
		
		self.galaxies = {gal.id: gal for gal in galaxies}
		self.meta = meta
		
	def __len__(self):
		return len(self.galaxies)
		
	def __str__(self):
		return "Catalog with %i galaxies and %i metadata" % (len(self), len(self.meta))

	def write(filepath):
		"""
		Writes the catalog to a pickle
		"""
		pass


	# Kind of works but is too confusing. Let's keep it simple
	#def __getitem__(self, galid):
	#	return self.galaxies[galid]
	#
	#def __iter__(self):
	#	for item in self.galaxies.values():
	#		yield item
	





