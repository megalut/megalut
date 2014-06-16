import numpy as np
import asciidata

class SourceSelect():
	'''
	Class to select sources amongst the galaxies avalaible in a catalogue
	A defintion of the catalogue must be supplied!
	'''
	# TODO: make this a class that inherit from sexmeas which also inherit of run, thus the catalogue definition is only computed ones
	# TODO: Include FWHM SELECTION
	required_params = ['XWIN_IMAGE', 'YWIN_IMAGE','AWIN_IMAGE','BWIN_IMAGE','FWHM_IMAGE','FLUX_AUTO','FLUXERR_AUTO','VECTOR_ASSOC2']
	settable = []
	
	def __init__(self, catalogue, id_image=None, verbose=True, debug=False):
		if type(catalogue) == asciidata.asciidata.AsciiData:
			print 'Source Selection received an ASCII catalogue, catalogue definition is inferred from data.'
			for col_i in range(len(catalogue)):
				if catalogue[col_i].colname in self.required_params or catalogue[col_i].colname in self.settable:
					setattr(self, catalogue[col_i].colname, col_i)
					if debug: print 'Set %s to column %d' % (catalogue[col_i].colname, col_i)
			catalogue = np.array(catalogue).T
		else:
			print '! WARNING: Source Selection received a numpy array, using default definition from revision *90*.'
			for param in self.required_params:
				setattr(self, param, None)
			for param in self.settable:
				setattr(self, param, None)
			'''
			/!\	WARNING: The default configuration corresponds to Sextractor parameters of revision *90* /!\
			'''
			self.set_catalogue_params(XWIN_IMAGE=5,YWIN_IMAGE=6,AWIN_IMAGE=9,BWIN_IMAGE=10,FWHM_IMAGE=14,FLUX_AUTO=15,FLUXERR_AUTO=16,VECTOR_ASSOC2=2)

		self.catalogue = catalogue
		self.id_image=id_image
		self.n_init = np.shape(catalogue)[0]
		self.verbose=verbose
		self.debug = debug

		self.skiplist_id = self.catalogue[:,self.VECTOR_ASSOC2]
		self.skiplist = np.array([False]*(np.shape(catalogue)[0]))

		if verbose == True:
			if not id_image == None:
				sub = ' from subfield %d' % id_image
			else: sub = ''
			print 'Loaded %d galaxies%s' % (self.n_init, sub)
			
		self.consistency_check()
		

	def consistency_check(self):
		try:
			for param in self.required_params:
				assert not getattr(self, param) == None
		except AssertionError:
			raise AssertionError('Could not understand which column is %s.' % param)
		
	def set_catalogue_params(self, **kwargs):
		# Get the definitions of the columns from the user
		for arg in kwargs:
			if arg in self.required_params or arg in self.settable:
				setattr(self, arg, kwargs[arg])
				if self.debug: print 'Set %s to column %d' % (arg, kwargs[arg])
		
	def get_catalogue(self):
		return self.catalogue

	def get_skiplist(self):
		return self.skiplist, self.skiplist_id
	
	def count_gal(self):
		return np.shape(self.catalogue)[0]
	
	def count_removed(self):
		return self.n_init-self.count_gal()

	def default_removal(self):
		self.remove_blends()
		r = 0
		if self.verbose:
			print '%5d objects were removed because of false detection of blending.' % (self.count_removed()-r)
			r = self.count_removed()
		
		mu = 3.5*np.std(self.catalogue[:,self.FLUX_AUTO])+np.mean(self.catalogue[:,self.FLUX_AUTO])
		mu = np.amin([mu, 220])
		self.remove_flux(mu)
		if self.verbose:
			print '%5d objects were removed because of flux.' % (self.count_removed()-r)
			r = self.count_removed()
	
		#self.remove_snr(10)
		if self.verbose:
			print '%5d objects were removed because of SNR.' % (self.count_removed()-r)
			r = self.count_removed()

		#self.remove_ellipticity(g_max=0.2)
		if self.verbose:
			print '%5d objects were removed because of ellipticity.' % (self.count_removed()-r)
			r = self.count_removed()

		#self.remove_fwhm(psf_fhwm=4, factor_min=1.2, factor_max=None)
		if self.verbose:
			print '%5d objects were removed because of FWHM.' % (self.count_removed()-r)
			r = self.count_removed()

		if self.verbose:
			print '+ -----'
			print '%5d objects were removed in total.' % (self.count_removed())

	#** BLENDING REMOVAL **************************************************************************
	def remove_blends(self,distance_upper_bound=10):
		from scipy.spatial import cKDTree
		arr = np.array([self.catalogue[:,self.XWIN_IMAGE], self.catalogue[:,self.YWIN_IMAGE]]).T
		Tree=cKDTree(arr)
		dist, id_list = Tree.query(Tree.data, k=2, distance_upper_bound=distance_upper_bound)
		ids = np.isfinite(dist[:,1])
		id_list = id_list[ids]
		self.skiplist[id_list] = True
		self.catalogue = np.delete(self.catalogue,id_list[::2].ravel(),axis=0)
	
	#** FWHM SELECTION ****************************************************************************
	def remove_fwhm(self, psf_fhwm, factor_min=1.2, factor_max=None):
		ids = np.where(self.catalogue[:,self.FWHM_IMAGE]<psf_fhwm*factor_min)[0]
		self.skiplist[ids] = True
		self.catalogue = np.delete(self.catalogue,ids,axis=0)
		if not factor_max == None: 
			ids = np.where(self.catalogue[:,self.FWHM_IMAGE]>psf_fhwm*factor_max)[0]
			self.skiplist[ids] = True
			self.catalogue = np.delete(self.catalogue,ids,axis=0)
		
	#** FLUX SELECTION ****************************************************************************
	def remove_flux(self, flux_max, flux_min=None):
		ids = np.where(self.catalogue[:,self.FLUX_AUTO]>flux_max)[0]
		self.skiplist[ids] = True
		self.catalogue = np.delete(self.catalogue,ids,axis=0)
		if not flux_min == None: 
			ids = np.where(flux_min>self.catalogue[:,self.FLUX_AUTO])[0]
			self.skiplist[ids] = True
			self.catalogue = np.delete(self.catalogue,ids,axis=0)
	
	#** NOISE SELECTION ***************************************************************************	
	def remove_snr(self, snr_min):
		snr = self.catalogue[:,self.FLUX_AUTO]/self.catalogue[:,self.FLUXERR_AUTO]
		ids = np.where(snr<snr_min)[0]
		#print self.catalogue[:,self.FLUX_AUTO]
		#print self.catalogue[:,self.FLUXERR_AUTO]
		#print snr
		self.skiplist[ids] = True
		self.catalogue = np.delete(self.catalogue,ids,axis=0)
		
	#** ELLIPTICITY SELECTION *********************************************************************
	def remove_ellipticity(self, g_max, g_min=None):
		eps = (self.catalogue[:,self.AWIN_IMAGE]-self.catalogue[:,self.BWIN_IMAGE])/(self.catalogue[:,self.AWIN_IMAGE]+self.catalogue[:,self.BWIN_IMAGE])
		
		ids = np.where(eps>g_max)[0]
		self.skiplist[id_list] = True
		self.catalogue = np.delete(self.catalogue,ids,axis=0)
		if not g_min == None:
			ids = np.where(eps<g_min)[0]
			self.catalogue = np.delete(self.catalogue,ids,axis=0)	
			self.skiplist[id_list] = True		

