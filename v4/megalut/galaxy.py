import copy as pythoncopy
import numpy as np
import asciidata
#import astropy.io.ascii

class Galaxy:
	"""
	Represents a galaxy and all its information that we will collect from sextractor, and the associated PSF.
	"""

	def __init__(self):
		
		# The information given in the catalogs
		self.ID = 0 # This is an int unique to each galaxy.
		self.x = 0.0
		self.y = 0.0
		#self.n_predictions = n_predictions
	
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
		self.mes_snr = 0.0
		self.mes_rad30 = 0.0
		self.mes_rad40 = 0.0
		self.mes_rad50 = 0.0
		self.mes_rad60 = 0.0
		self.mes_rad70 = 0.0
		self.mes_rad80 = 0.0
		self.mes_rad90 = 0.0
		self.mes_radkron = 0.0
		self.mes_sky = 0.0
		self.mes_sig = 0.0
		
		self.mes_acf_g1 = 0.0
		self.mes_acf_g2 = 0.0
		self.mes_acf_Ixx = 0.0
		self.mes_acf_Iyy = 0.0
		self.mes_acf_Ixy = 0.0
		
		
		# The true information, only available for sims :
		self.tru_g1 = 0.0
		self.tru_g2 = 0.0
		self.tru_flux = 0.0
		self.tru_rad = 0.0
		self.tru_sersicn = 0.0 # Sersic index
		self.tru_sig = 0.0
	
		self.flag = 0
	
		self.resetpred()
	
	def resetpred(self):
		
		# The predicted information :
		self.pre_g1 = 0.0
		self.pre_g2 = 0.0
		self.pre_flux = 0.0
		self.pre_rad = 0.0
		self.pre_sersicn = 0.0
		
	
	def __str__(self):
		return "ID %i of img %02i at (%.1f, %.1f) : a=%.2f, b=%.2f, theta=%.2f, flux=%.2f" % (self.ID, self.tru_nimg, self.x, self.y, self.mes_a, self.mes_b, self.mes_theta, self.mes_flux) 
	
	
	def isgood(self, radpsf=None):
		"""
		Returns True if the galaxy has been well-measured.
		"""
		
		if self.mes_flux <= 0.0:
			return False
		
		if getattr(self, "mes_gs_flux", 1.0) < 0.0:
			return False
		
		rad_attrs = ["mes_rad30","mes_rad40", "mes_rad50", "mes_rad60","mes_rad70","mes_rad80", "mes_rad90"] # Must be sorted !

		for attr in rad_attrs:
			if getattr(self, attr) < 0.0 or getattr(self, attr) > 50.0:
				return False
		for i in range(len(rad_attrs) - 1):
			if getattr(self, rad_attrs[i]) > getattr(self, rad_attrs[i+1]):
				return False

		if not radpsf==None:
#			print self.mes_fwhm/radpsf
			if self.mes_fwhm/radpsf<1.2:
				return False

		return True

	
	
	def copy(self):
		"""
		Returns a copy of myself
		"""
		return pythoncopy.deepcopy(self)
													
		
	def calcmes(self):																		
		"""
		Computes some additional attributes based on shape measurement results
		"""
		self.mes_size = self.mes_a * self.mes_b														
		if self.mes_a > 0.0 and self.mes_b > 0.0 :
			self.mes_eps = (self.mes_a - self.mes_b) / (self.mes_a + self.mes_b)
		else:
			self.mes_eps = 0.0
		self.mes_g1 = self.mes_eps * np.cos(2.0 * self.mes_theta*np.pi/180.0)
		self.mes_g2 = self.mes_eps * np.sin(2.0 * self.mes_theta*np.pi/180.0)
	
		if self.mes_rad30 > 0.00001:
			self.mes_c = float(self.mes_rad70) / float(self.mes_rad30)
		else:
			self.mes_c = 0.0
		
		if hasattr(self, "mes_gs_g1") and hasattr(self, "mes_gs_g2"):
			self.mes_gs_eps = np.hypot(self.mes_gs_g1, self.mes_gs_g2)
			#self.mes_gs_theta = # maybe even this. Or just normalized g1 g2 to give direction
			
		self.prerr_g1 = self.pre_g1 - self.tru_g1
		self.prerr_g2 = self.pre_g2 - self.tru_g2
		self.prerr_flux = self.pre_flux - self.tru_flux
		self.prerr_rad = self.pre_rad - self.tru_rad
		self.prerr_sersicn = self.pre_sersicn - self.tru_sersicn
		
		self.prerrabs_g1 = np.fabs(self.prerr_g1)
		self.prerrabs_g2 = np.fabs(self.prerr_g2)
		self.prerrabs_g = np.hypot(self.prerr_g1, self.prerr_g2)
		self.prerrabs_flux = np.fabs(self.prerr_flux)
		self.prerrabs_rad = np.fabs(self.prerr_rad)
		self.prerrabs_sersicn = np.fabs(self.prerr_sersicn)
		
		
		
	
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

	def info(self):
		"""
		Prints out all the variables for a given galaxy of the class
		"""
		import inspect
	
		message = "All variables available for galaxy ID %i" % self.ID		
		print message
		print '-'*len(message)
		attributes = inspect.getmembers(self, lambda a:not(inspect.isroutine(a)))
		for a in attributes:
			if (a[0].startswith('__') and a[0].endswith('__')): continue
			print a[0], "=", a[1]

def rms(tru, pre):
	return np.sqrt(np.mean((tru - pre)**2.0))

def mad(tru, pre):
	return np.median(np.fabs(tru - pre))


def mymetrics(galaxies):
	"""
	Some simple metrics about the prediction quality...
	"""


	pre_g1 = np.array([g.pre_g1 for g in galaxies])
	pre_g2 = np.array([g.pre_g2 for g in galaxies])
	pre_flux = np.array([g.pre_flux for g in galaxies])
	pre_rad = np.array([g.pre_rad for g in galaxies])
	pre_sersicn = np.array([g.pre_sersicn for g in galaxies])

	tru_g1 = np.array([g.tru_g1 for g in galaxies])
	tru_g2 = np.array([g.tru_g2 for g in galaxies])
	tru_flux = np.array([g.tru_flux for g in galaxies])
	tru_rad = np.array([g.tru_rad for g in galaxies])
	tru_sersicn = np.array([g.tru_sersicn for g in galaxies])

	
	metrics = {"n":len(galaxies),

		#"rms_g1":rms(np.mean(pre_g1), tru_g1), "rms_g2":rms(np.mean(pre_g2), tru_g2),
		#"mad_g1":mad(np.mean(pre_g1), tru_g1), "mad_g2":mad(np.mean(pre_g2), tru_g2),

		"rms_g1":rms(pre_g1, tru_g1), "rms_g2":rms(pre_g2, tru_g2),
		"mad_g1":mad(pre_g1, tru_g1), "mad_g2":mad(pre_g2, tru_g2),
		
		"rms_flux":rms(pre_flux, tru_flux), "mad_flux":mad(pre_flux, tru_flux),
		"rms_rad":rms(pre_rad, tru_rad), "mad_rad":mad(pre_rad, tru_rad),
		"rms_sersicn":rms(pre_sersicn, tru_sersicn), "mad_sersicn":mad(pre_sersicn, tru_sersicn),
		
	}

	return metrics


def printmymetrics(galaxies):
	
	metrics = mymetrics(galaxies)
	print "g1:      rms %8.5f, mad %8.5f" % (metrics["rms_g1"], metrics["mad_g1"])
	print "g2:      rms %8.5f, mad %8.5f" % (metrics["rms_g2"], metrics["mad_g2"])
	print "flux:    rms %8.5f, mad %8.5f" % (metrics["rms_flux"], metrics["mad_flux"])
	print "rad:     rms %8.5f, mad %8.5f" % (metrics["rms_rad"], metrics["mad_rad"])
	print "sersicn: rms %8.5f, mad %8.5f" % (metrics["rms_sersicn"], metrics["mad_sersicn"])
	
	

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

def export(galaxies, filepath):
	"""
	Saves the galaxies into a FITS table for interactive inspection with tools like topcat
	
	
	"""
	import inspect
	try:
		import pyfits
	except:
		print "pyfits could not be imported, no problem if you don't need it."
	
	allattributes = set([])
	for g in galaxies:
		g.calcmes()
		g.good = g.isgood()
		
		# this is now part of calcmes...
		"""
		g.prerr_g1 = g.pre_g1 - g.tru_g1
		g.prerr_g2 = g.pre_g2 - g.tru_g2
		g.prerr_flux = g.pre_flux - g.tru_flux
		g.prerr_rad = g.pre_rad - g.tru_rad
		g.prerr_sersicn = g.pre_sersicn - g.tru_sersicn
		
		g.prerrabs_g1 = np.fabs(g.prerr_g1)
		g.prerrabs_g2 = np.fabs(g.prerr_g2)
		g.prerrabs_g = np.hypot(g.prerr_g1, g.prerr_g2)
		g.prerrabs_flux = np.fabs(g.prerr_flux)
		g.prerrabs_rad = np.fabs(g.prerr_rad)
		g.prerrabs_sersicn = np.fabs(g.prerr_sersicn)
		"""
		
		attributes = inspect.getmembers(g, lambda a:not(inspect.isroutine(a)))
		attributes = set([a[0] for a in attributes if not(a[0].startswith('__') and a[0].endswith('__')) and not 'committee' in a[0]])
		
		allattributes = attributes.union(allattributes)
		

	cols = [pyfits.Column(name=a, format="D", array=np.array([convert(g, a) for g in galaxies])) for a in sorted(list(allattributes))]
	
	coldefs = pyfits.ColDefs(cols)
	tbhdu = pyfits.new_table(coldefs)
	tbhdu.writeto(filepath, clobber=True)
	print "Wrote %s" % (filepath)
	

	
	
	



