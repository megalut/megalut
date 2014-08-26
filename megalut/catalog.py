"""
This module defines a simple catalog structure which we use accross MegaLUT.
A catalog is simply a dict (or a list, depending on what we do) of Galaxy objects.
"""

import copy as pythoncopy

class Galaxy:
	"""
	Represents a galaxy and all its information. It's mainly a dict.
	"""

	def __init__(self, id="0", ra=0.0, dec=0.0):
		"""
		Minimal constructor.
		The pythonic way is to avoid type checking. But in principle, we expect id to be a string...
		The minimal fields given here should always exist.
		"""
		self.fields = {"id"=id, "ra":ra, "dec":dec}
	
	
	def __str__(self):
		"""
		Uses only the minimal fields ?
		"""
		return "Galaxy %i (ra = %.6f, dec = %.6f) with %i fields" % (self.fields["id"], self.fields["ra"], self.fields["dec"], len(self.fields)) 
		
		
	def copy(self):
		"""
		Returns a copy of myself.
		"""
		return pythoncopy.deepcopy(self)
													
				
	def getarray(self, keys):
		"""
		Returns numerical field values in form a numpy array. Useful for instance to feed machine learning, both for features or labels.
		:param keys: a list of key names, or just a single key
		"""
		# We could check that everything is float / int / numeric here ? I guess better not.
		
		try: 
			return np.array([self.fields.get(self, key) for key in keys])
		except TypeError as err:
			print "Give me a list of keys, not a single key !"
			raise err
			
		
	def setarray(self, array, keylist, overwritewarning=True):
		"""
		The inverse of getarray. Useful for instance to write some predicted data into the catalog. 
		"""
		assert len(array) == len(keylist)
		for val, key in zip(array, keylist):
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
		







