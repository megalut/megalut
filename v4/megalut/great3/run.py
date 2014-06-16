"""
The class to hold a MegaLUT run with all its config parameters etc.
"""

import os
import glob
import numpy as np

import io
import sim
import megalut

class Run:
	ava_methods = ['sex','acf','galsim']

	def __init__(self, datadir, workdir, branch, version, **kwargs):

		"""
		Some attributes with default params. There are no setter functions, feel free to change these attributes yourself.
		
		branch is a list of 3 elements
		e.g. : ["control", "ground", "variable"]
		
		Here are the choices for branches :
		experiments = ['control', 'real_galaxy', 'variable_psf', 'multiepoch', 'full']
		observation_types = ['ground', 'space']
		shear_types = ['constant', 'variable']
		
		"""
		
		self.datadir = datadir
		self.workdir = workdir
		self.branch = branch
		self.version = version

		self.reset_default()
		
		for arg in kwargs: # Take all supplementary arguments and store them
			# Not so safe...
			# TODO: make sure this is does not overwrite parameters
			setattr(self, arg, kwargs[arg])
			
		self.config_consistency_check()
		
		message = 'This run of MegaLUT will be on %s-%s-%s-%s' % (branch[0],branch[1],branch[2], version)

		print (len(message)+4)*'*'
		print '*', message, '*'
		print (len(message)+4)*'*'


	def reset_default(self):
		'''
		Reset run parameters to "Factory defaults"
		'''
	
		for m in self.ava_methods: 
			setattr(self, 'use_%s' % m, False)
		self.use_sex = True
		

		self.obssubfields = range(0, 200) # The subfields on wich to run on
				
		# The subfields I should simulate
		self.simsubfields = range(0, 200) # Will probably have to be adapted for other branches...
		
		if self.branch[0] in ["control", "real_galaxy", "multiepoch", "full", "variable_psf"]: # WARNING, NOT YET TESTED IF THIS APPLIES TO FULL and variable_psf ???? Thibault, do we know this ?
			if self.branch[2] == "constant":
				self.simsubfields = range(0, 200)
			elif self.branch[2] == "variable":
				self.simsubfields = range(0, 200, 20)
		else:
			raise RuntimeError("Tell me how to use this branch !")

		# By default, not using source selection
		self.source_selection = False

		# Minimum percentage of galaxies that is tolerated to go on. 90% --> 0.9
		self.min_nb_good_galaxies = 0.9
		
		# Denoising ?
		self.denoisethres = None
		self.denoise = None

		# Prior coadding ?
		self.precoadd = "" # Set this to a non-empty string (the precoadd version name), and I will take my data from there ! 

		# Artificial Neuronal Network config
		
		#self.NN_committee_members = 1	# Number of times SkyNet will train idepently on the data -- as it uses random weights at initialiasation, then this method may correct for local minimums or overfitting. Idea from arXiv:astro-ph/0311058

		# Number of simulated images drawn with n galaxies
		self.nsimimages=1

		self.multiepoch = False
		
	def config_consistency_check(self):
		'''
		Check that the simulation can run until the end, if yes return True, if no raises a corresponding error
		'''
		enabled_methods = []
		for m in self.ava_methods: 
			enabled_methods.append(getattr(self, 'use_%s' % m))

		if not any(enabled_methods):
			raise RuntimeError('No shape measurement method enabled... Aborting')
			
		experiments = ['control', 'real_galaxy', 'variable_psf', 'multiepoch', 'full']
		observation_types = ['ground', 'space']
		shear_types = ['constant', 'variable']
		if not self.branch[0] in experiments:
			raise RuntimeError('Experiment %s unknown... Aborting' % self.branch[0] )
			
		if not self.branch[1] in observation_types:
			raise RuntimeError('observation_types %s unknown... Aborting' % self.branch[1] )
			
		if not self.branch[2] in shear_types:
			raise RuntimeError('shear_types %s unknown... Aborting' % self.branch[2] )
			
		return True
	
	# Now we define some paths that will get used by more or less all methods :	
	
		# General directories
		
	def obsdir(self): # Measurements on observations will go here
		if self.denoise:
			return os.path.join(self.workdir, "obs-" + "-".join(self.branch) + "-%s-den%s" % (self.version, self.denoise))
		else:
			return os.path.join(self.workdir, "obs-" + "-".join(self.branch) + "-%s" % (self.version))
	
	def simdir(self): # Simulation related stuff will go here
		if self.denoise:
			return os.path.join(self.workdir, "sim-" + "-".join(self.branch) + "-%s-den%s" % (self.version, self.denoise))
		else:
			return os.path.join(self.workdir, "sim-" + "-".join(self.branch) + "-%s" % (self.version))
	
	def outdir(self): # Submission files will go here
		if self.denoise:
			return os.path.join(self.workdir, "out-" + "-".join(self.branch) + "-%s-den%s" % (self.version, self.denoise))
		else:	
			return os.path.join(self.workdir, "out-" + "-".join(self.branch) + "-%s" % (self.version))
	
	
	def subfilepath(self): # the final submission file
		if self.denoise:
			return os.path.join(self.workdir, "out-" + "-".join(self.branch) + "-%s-den%s.txt" % (self.version, self.denoise))
		else:	
			return os.path.join(self.workdir, "out-" + "-".join(self.branch) + "-%s.txt" % (self.version))
		
	
	
	def branchdir(self): # This is where the GREAT3 data is
		return os.path.join(self.datadir, "/".join(self.branch))

		# When observed data is denoised, it is written here :
	def denbranchdir(self):
		return os.path.join(self.workdir, "den-" + self.denoise, "/".join(self.branch))

	def check_dir(self):
		# Making sure all the directories are there:
		if self.denoise:
			#Observation
			if not os.path.exists(self.denbranchdir()):
				os.makedirs(self.denbranchdir())
		# Observation
		if not os.path.isdir(self.obsdir()):
			os.mkdir(self.obsdir())
		# Simulations
		if not os.path.isdir(self.simdir()):
			os.mkdir(self.simdir())
		# Outdir
		if not os.path.exists(self.outdir()):
			os.mkdir(self.outdir())

	def precoadddir(self):
		if len(self.precoadd) == 0:
			raise RuntimeError("Ouch, I don't know where is the precoadd data !")
		return os.path.join(self.workdir, "obs-" + "-".join(self.branch) + "-coadd-" + self.precoadd)


		# Stuff related to the observations
		
	def obsgalimgfilepath(self, subfield, epoch=0):
		return os.path.join(self.branchdir(), "image-%03i-%i.fits" % (subfield, epoch)) # This is set by GREAT3

	def denobsgalimgfilepath(self, subfield, epoch=0):
		return os.path.join(self.denbranchdir(), "image-%03i-%i.fits" % (subfield, epoch))
	
	def precoaddgalimgfilepath(self, subfield):
		return os.path.join(self.precoadddir(), "coadd_image-%03i.fits" % (subfield))

	def obspsfimgfilepath(self, subfield, epoch=0):
		return os.path.join(self.branchdir(), "starfield_image-%03i-%i.fits" % (subfield, epoch)) # This is set by GREAT3

	def precoaddpsfimgfilepath(self, subfield):
		return os.path.join(self.precoadddir(), "coadd_starfield_image-%03i.fits" % (subfield))

	def obscatfilepath(self, subfield):
		return os.path.join(self.branchdir(), "galaxy_catalog-%03i.txt" % (subfield)) # This is set by GREAT3
		
	def obsgalfilepath(self, subfield):
		return os.path.join(self.obsdir(), "obs-%03i.pkl" % (subfield))

	def obsstarfilepath(self, subfield):
		return os.path.join(self.obsdir(), "obs-star-%03i.pkl" % (subfield))

	def obsstarcatpath(self, subfield):
		return os.path.join(self.branchdir(), 'star_catalog-%03i.txt' % subfield) # This is set by GREAT3

	def obsstarsexpath(self, subfield):
		return os.path.join(self.obsdir(), 'star_catalog-%03i.txt' % subfield) # This is set by GREAT3


		# Stuff related to the simulations
		
	def simgalimgfilepath(self, subfield, nimg=None):
		if nimg == None:
			return os.path.join(self.simdir(), "sim-%03i-galimg.fits" % (subfield))
		else:
			return os.path.join(self.simdir(), "sim-%03i-%02i-galimg.fits" % (subfield,nimg))
		
	def densimgalimgfilepath(self, subfield):
		return os.path.join(self.simdir(), "sim-%03i-galimg-den.fits" % (subfield))
	
	def simgalfilepath(self, subfield,nimg):
		if nimg == None:
			return os.path.join(self.simdir(), "sim-%03i.pkl" % (subfield))
		else:
			return os.path.join(self.simdir(), "sim-%03i-%02i.pkl" % (subfield,nimg))

#	def simstarfilepath(self, subfield):
#		return os.path.join(self.obsdir(), "sim-star-%03i.pkl" % (subfield))
	
	def simtrugalimgfilepath(self, subfield,nimg):
		return os.path.join(self.simdir(), "sim-%03i-%02i-trugalimg.fits" % (subfield,nimg))

	def simpsfimgfilepath(self, subfield,nimg):
		return os.path.join(self.simdir(), "sim-%03i-%02i-psfimg.fits" % (subfield,nimg))
	
	

	def gets(self):
		"""
		s is the stamp size in pixels
		"""
		if self.branch[1] == "ground":
			return 48
		elif self.branch[1] == "space":
			return 96

	
	
	################################################################################################

	def measstars(self, skipdone=True):
		print '\n'*3
		message = 'START OF MEASURMENTS ON STARS'
		print message
		print "="*len(message)

		if not os.path.isdir(self.obsdir()):
			os.mkdir(self.obsdir())

		for subfield in self.obssubfields:
			if skipdone and os.path.exists(self.obsstarfilepath(subfield)):
				print "Skipping %s ..." % (self.obsstarfilepath(subfield))
				continue

			# Load all stars
			stars = io.readstarcat(self.obsstarcatpath(subfield))

			# Prepare the filename
			sexcatfilepath = os.path.join(self.obsdir(), self.obsstarsexpath(subfield))
			assocfilepath=os.path.join(self.obsdir(), "starassoc-%03i.txt" % subfield)
			imgfilepath=self.obspsfimgfilepath(subfield)

			#np.savetxt(fname,stars)
			# Prepare the assoc file for sextractor
			megalut.sexstarmeas.writeassoc(stars, assocfilepath)

			# Sextractor run on the stars.
			megalut.sexstarmeas.run(imgfilepath, sexcatfilepath, assocfilepath)

			# Read the sextractor catalog
			megalut.sexstarmeas.readout(stars, sexcatfilepath)

			# Write the database into a pkl file
			megalut.utils.writepickle(stars, self.obsstarfilepath(subfield))
			megalut.stars.export(stars, self.obsstarfilepath(subfield)+".fits")

	
	def measobs(self, skipdone=True):
		"""
		First task : measure the observations
		"""
		print '\n'*3
		message = 'START OF MEASURMENTS ON OBSERVATIONS'
		print message
		print "="*len(message)
	
		# Should we denoise ?
		if self.denoise:
			
			print "We first have to denoise the observations."
	
			if not os.path.exists(self.denbranchdir()):
				os.makedirs(self.denbranchdir())
			
			for subfield in self.obssubfields:
		
				if skipdone and os.path.exists(self.denobsgalimgfilepath(subfield)):
					print "Skipping %s ..." % (self.obsgalimgfilepath(subfield))
					continue
			
				(sky, sig) = sim.measuresky(self.obsgalimgfilepath(subfield))
				absthres = sig * np.array(self.denoisethres)
				print "Using thresholds %s" % (str(absthres))
			
				megalut.waveletdenoise.fitsdenoise(self.obsgalimgfilepath(subfield), self.denobsgalimgfilepath(subfield), absthres)
				#exit()
		
			print "Done with the denoising, now comes the shape measurement."
		
		
		if not os.path.isdir(self.obsdir()):
			os.mkdir(self.obsdir())

		
		for subfield in self.obssubfields:
			
			# Import the GREAT3 catalog
			galaxies = io.readcat(self.obscatfilepath(subfield))
			if len(self.precoadd) != 0:
				if self.branch[1] == "space":
					# Then we have to multiply the galaxy positions by the upsampling factor...
					for g in galaxies:
						g.x *= 2.0
						g.y *= 2.0

			if skipdone and os.path.exists(self.obsgalfilepath(subfield)):
				print "Skipping %s ..." % (self.obsgalfilepath(subfield))
				continue
	
			# The image on which to run:
			
			if len(self.precoadd) == 0:
				if self.denoise:
					imgfilepath = self.denobsgalimgfilepath(subfield)
				else:
					imgfilepath = self.obsgalimgfilepath(subfield)
			else:
				imgfilepath = self.precoaddgalimgfilepath(subfield)
			
			
			# Write the assoc file
			
			assocfilepath = os.path.join(self.obsdir(), "assoc-%03i.txt" % (subfield))
			megalut.sexmeas.writeassoc(galaxies, assocfilepath)
			
			# Run sextractor on the image
			sexcatfilepath = os.path.join(self.obsdir(), "sex-%03i.cat" % (subfield))
			megalut.sexmeas.run(imgfilepath, sexcatfilepath, assocfilepath)

			# Read the sextractor catalog
			megalut.sexmeas.readout(galaxies, sexcatfilepath, source_selection=self.source_selection, id_image=subfield)
			
			if self.use_acf:
				# Run the ACF on the image
				acfcatfilepath = os.path.join(self.obsdir(), "acf-%03i.cat" % (subfield))
				megalut.acfmeas.run(imgfilepath, acfcatfilepath, assocfilepath, galaxies)
				megalut.acfmeas.readout(galaxies, acfcatfilepath)
			
			if self.use_galsim:
				megalut.galsimmeas.measure(imgfilepath, galaxies, s=self.gets())
				
			
			# Compute the sky stats for the (undenoised!) image, add this to the galaxies
			(sky, sig) = sim.measuresky(self.obsgalimgfilepath(subfield))
			for g in galaxies:
				g.mes_sky = sky
				g.mes_sig = sig
			
			# Conclude
			ngood = len([g for g in galaxies if g.isgood()])
			print "We have %i out of %i good galaxies." % (ngood, len(galaxies))
			if float(ngood)/float(len(galaxies)) < self.min_nb_good_galaxies:
				print '! WARNING: Number of valid measurements (%d) in subfield %d is below the acceptable limit of %d%%' % (float(ngood),subfield,self.min_nb_good_galaxies*100)
			
			# Write the database into a pkl file
			megalut.utils.writepickle(galaxies, self.obsgalfilepath(subfield))
			megalut.galaxy.export(galaxies, self.obsgalfilepath(subfield)+".fits")


	def makesim(self, simparams, n=100, skipdone=True, random_psf=False, givensig=None, givenpsfsubfield=None, measurepsf=True):
		"""
		Second task : draw the learning sample.
		
		simparams is an object describing the sims.
		
		n**2 is the number of stamps you want.
		
		
		For tests only:
		If you specify givensig and givenpsf, I will use these instead of reading it from the observations.
		
		"""

		print '\n'*3
		message = 'START OF SIMULATIONS'
		print message
		print "="*len(message)
		
		if not os.path.isdir(self.simdir()):
			os.mkdir(self.simdir())

		for subfield in self.simsubfields:
			for nimg in range(self.nsimimages):
				if skipdone and (os.path.exists(self.simgalfilepath(subfield,nimg))):
					skip=True
				else:
					skip=False
			if skip:			
				print "Skipping %s..." % (self.simgalfilepath(subfield,nimg))
				continue

			# We read in the sky noise of this subfield, to use in the simulations :
			if givensig == None:
				obsgalaxies = megalut.utils.readpickle(self.obsgalfilepath(subfield))
				simparams.sig = obsgalaxies[0].mes_sig
			else:
				print "#"*30 + " Warning : using given sig !"
				simparams.sig = givensig

			if givenpsfsubfield == None:
				subfieldtouse = subfield
			else:
				print "#"*30 + " Warning : using given PSF !"
				subfieldtouse = givenpsfsubfield
				
			if len(self.precoadd) == 0:	
				obspsfimgfilepath = self.obspsfimgfilepath#(subfieldtouse)
			else:
				obspsfimgfilepath = self.precoaddpsfimgfilepath#(subfieldtouse)	
			
			if self.branch[0] == "variable_psf":
				is_psfvar=True
				# We read in the database
				stars = [self.obsstarfilepath,self.branch[2]]
			else:
				is_psfvar=False
				stars=None

			# We call drawsim to draw the simulations
			print 'Starting to draw %i galaxies...' % (n*n*self.nsimimages)
			"""from psfcoadd import psfcoadd
			psfcoadd(
				simparams,
				s = self.gets(), n=n, nimg=self.nsimimages,
				obspsfimgfilepath = obspsfimgfilepath,
				simgalimgfilepath = self.simgalimgfilepath,
				simgalfilepath = self.simgalfilepath,
				simtrugalimgfilepath = self.simtrugalimgfilepath,
				simpsfimgfilepath = self.simpsfimgfilepath,
				stars=stars, 
				is_psfvar=is_psfvar,
				current_subfield=subfield,
				random_psf=random_psf
			)
			exit()"""
			sim.drawsim(
				simparams,
				s = self.gets(), n=n, nimg=self.nsimimages,
				obspsfimgfilepath = obspsfimgfilepath,
				simgalimgfilepath = self.simgalimgfilepath,
				simgalfilepath = self.simgalfilepath,
				simtrugalimgfilepath = self.simtrugalimgfilepath,
				simpsfimgfilepath = self.simpsfimgfilepath,
				stars=stars, 
				is_psfvar=is_psfvar,
				current_subfield=subfield,
				random_psf=random_psf,
				measurepsf=measurepsf
			)
#				print len(simgalaxies), 'galaxies drawn up to now.'
			# And write the new database of simulated Galaxies
#			megalut.utils.writepickle(simgalaxies, self.simgalfilepath(subfield))


	def meassim(self, skipdone=True):
		"""
		Third task : measure the learning sample
		
		I run on all available sims, without looking at self.simsubfields.
		"""
		print '\n'*3
		message = 'START OF MEASURMENTS ON SIMULATIONS'
		print message
		print "="*len(message)

		for subfield in self.simsubfields:

			for nimg in range(self.nsimimages):
				# Read the simulated galaxy pkl
				galaxies = megalut.utils.readpickle(self.simgalfilepath(subfield,nimg))

				sexcatfilepath = os.path.join(self.simdir(), "sex-%03i-%02i.cat" % (subfield,nimg))
			
				if skipdone and os.path.exists(sexcatfilepath):
					print "Skipping %s ..." % (sexcatfilepath)
					continue
				
				# Should we denoise the images ?
				if self.denoise:
					(sky, sig) = sim.measuresky(self.simgalimgfilepath(subfield,nimg))
					absthres = sig * np.array(self.denoisethres)
					print "Using thresholds %s" % (str(absthres))
			
					megalut.waveletdenoise.fitsdenoise(self.simgalimgfilepath(subfield,nimg), self.densimgalimgfilepath(subfield,nimg), absthres)

				# The image on which to run:
				if self.denoise:
					imgfilepath = self.densimgalimgfilepath(subfield,nimg)
				else:
					imgfilepath = self.simgalimgfilepath(subfield,nimg)
	
				# Write the assoc file
				assocfilepath = os.path.join(self.simdir(), "assoc-%03i-%02i.txt" % (subfield,nimg))
				megalut.sexmeas.writeassoc(galaxies, assocfilepath)

				# Run sextractor on the image
				megalut.sexmeas.run(imgfilepath, sexcatfilepath, assocfilepath)

				# Read the sextractor catalog
				megalut.sexmeas.readout(galaxies, sexcatfilepath, source_selection=self.source_selection, id_image=subfield)

				if self.use_acf:
					# Run the ACF on the image
					acfcatfilepath = os.path.join(self.simdir(), "acf-%03i-%02i.cat" % (subfield, nimg))
					megalut.acfmeas.run(imgfilepath, acfcatfilepath, assocfilepath, galaxies, n_stamps=int(np.sqrt(len(galaxies))))##, )))
					megalut.acfmeas.readout(galaxies, acfcatfilepath)#, nimg=nimg)
			
				if self.use_galsim:
					megalut.galsimmeas.measure(imgfilepath, galaxies, s=self.gets())
			
				# Compute the sky stats for the (undenoised!) image, add this to the galaxies
				(sky, sig) = sim.measuresky(self.simgalimgfilepath(subfield,nimg))
				for g in galaxies:
					g.mes_sky = sky
					g.mes_sig = sig
			
			# Conclude
				ngood = len([g for g in galaxies if g.isgood()])
				print "We have %i out of %i good galaxies." % (ngood, len(galaxies))
				if float(ngood)/float(len(galaxies)) < self.min_nb_good_galaxies:
					print '! WARNING: Number of valid measurements (%d) in subfield %d is below the acceptable limit of %d%%' % (ngood,subfield,self.min_nb_good_galaxies*100)
			
				# Update the database with those measurements.
				megalut.utils.writepickle(galaxies, self.simgalfilepath(subfield,nimg))
				megalut.galaxy.export(galaxies, self.simgalfilepath(subfield,nimg)+".fits")

	
	
	def plotsimobscompa(self, subfields):
		"""
		Some plots comparing the distributions of parameters measured on simulations and observations
		
		I use only the first nimg...
		
		"""
		for subfield in subfields:
			simgalaxies = megalut.utils.readpickle(self.simgalfilepath(subfield, nimg=0))
			obsgalaxies = megalut.utils.readpickle(self.obsgalfilepath(subfield))
		
			# No, don't do such funny selections, dangerous -- we want to see all galaxies
			#simgalaxies = [g for g in simgalaxies if g.mes_flux > 0.0]
			#obsgalaxies = [g for g in obsgalaxies if g.mes_flux > 0.0]
			
			for g in simgalaxies:
				g.calcmes()
			for g in obsgalaxies:
				g.calcmes()
			
			print "mes_sig (obs, sim) : ", obsgalaxies[0].mes_sig, simgalaxies[0].mes_sig
			
			if self.use_galsim == True:
				megalut.plots.mesdistribs(obsgalaxies, simgalaxies, 
					paramx = ("mes_gs_rho4", "mes_gs_rho4", 1.5, 3.0),
					paramy = ("mes_gs_sigma", "mes_gs_sigma", 0.0, 10.0),
					filepath = os.path.join(self.simdir(), "simobscompa-%03i-mes_gs_rho4_vs_sigma.png" % (subfield)),
					title = str(self.branch) + " (%03i)" % (subfield)
				)
			
			megalut.plots.mesdistribs(obsgalaxies, simgalaxies, 
				paramx = ("mes_fwhm", "FWHM", 0.,16.),
				paramy = ("mes_flux", "Flux", -10.0, 200.),
				filepath = os.path.join(self.simdir(), "simobscompa-%03i-mes_fwhm_vs_flux.png" % (subfield)),
				title = str(self.branch) + " (%03i)" % (subfield)
			)
			
			megalut.plots.mesdistribs(obsgalaxies, simgalaxies, 
				paramx = ("mes_c", "Concentration", 1.2, 4.0),
				paramy = ("mes_fwhm", "FWHM", 0.0, 35.0),
				filepath = os.path.join(self.simdir(), "simobscompa-%03i-mes_c_vs_fwhm.png" % (subfield)),
				title = str(self.branch) + " (%03i)" % (subfield)
			)

			megalut.plots.mesdistribs(obsgalaxies, simgalaxies, 
				paramx = ("mes_flux", "Flux", 0, 200.0),
				paramy = ("mes_eps", "eps", 0.0, 0.5),
				filepath = os.path.join(self.simdir(), "simobscompa-%03i-mes_flux_vs_eps.png" % (subfield)),
				title = str(self.branch) + " (%03i)" % (subfield)
			)
	
			megalut.plots.mesdistribs(obsgalaxies, simgalaxies, 
				paramx = ("mes_g1", "g1", -0.5, 0.5),
				paramy = ("mes_g2", "g2", -0.5, 0.5),
				filepath = os.path.join(self.simdir(), "simobscompa-%03i-mes_g1_vs_g2.png" % (subfield)),
				title = str(self.branch) + " (%03i)" % (subfield)
			)
	
			megalut.plots.mesdistribs(obsgalaxies, simgalaxies, 
				paramx = ("mes_flux", "Flux", 0.0, 200.0),
				paramy = ("mes_size", "Size", 0.0, 35.0),
				filepath = os.path.join(self.simdir(), "simobscompa-%03i-mes_flux_vs_size.png" % (subfield)),
				title = str(self.branch) + " (%03i)" % (subfield)
			)
		
			megalut.plots.mesdistribs(obsgalaxies, simgalaxies, 
				paramx = ("mes_fwhm", "FWHM", 0.0, 35.0),
				paramy = ("mes_size", "Size", 0.0, 35.0),
				filepath = os.path.join(self.simdir(), "simobscompa-%03i-mes_fwhm_vs_size.png" % (subfield)),
				title = str(self.branch) + " (%03i)" % (subfield)
			)
			
			megalut.plots.mesdistribs(obsgalaxies, simgalaxies, 
				paramx = ("mes_c", "Concentration", 1.2, 4.0),
				paramy = ("mes_size", "Size", 0.0, 35.0),
				filepath = os.path.join(self.simdir(), "simobscompa-%03i-mes_c_vs_size.png" % (subfield)),
				title = str(self.branch) + " (%03i)" % (subfield)
			)
			
			"""
			# Additional plot, not involving the observations :
			megalut.plots.simmesellip(simgalaxies#,
				filepath = os.path.join(self.simdir(), "simobscompa-%03i-mes_g_vs_true.png" % (subfield))
			)
			"""
	
		
	def train(self, paramlist, skipdone=True, saveselfpredict=True):
		"""
		Fourth task : train the machine learning on the simulations, compute the predictions for these simulations, and show how good/bad it went.
		
		I will process each simsubfield separately.
		
		For each simsubfield, we might want to train several different NNs:
			- one to predict g1 and g2
			- one to predict the flux
			- one to predict the rad
		Do do this, you can pass several parameter sets.
		
		paramlist is a list of tuples (MLParams, toolparams), where toolparams can be for instance SkyNetParams.
		I'll process this list tuple by tuple.
		
		If you keep saveselfpredict to True,
		I will also update the simulated galaxies with their predictions.
			
		"""

		print '\n'*3
		message = 'START OF TRAINING'
		print message
		print "="*len(message)
		

		for subfield in self.simsubfields:
			
			needtoload = True

			print "Training for simsubfield %i..." % (subfield)
			galaxies = []
			goodgalaxies=[]


			
			# Quick check that we will not mess up with directories :
			mlnames = [paramtuple[0].name for paramtuple in paramlist]
			assert len(mlnames) == len(set(mlnames))
			
			for (mlparams, toolparams) in paramlist:
	
				# We train each machine learning in a dedicaded directory
				mldir = os.path.join(self.simdir(), "ml-%03i-%s-%s-%s" % (subfield, mlparams.name, toolparams.tool, toolparams.name))
				mlpickle = os.path.join(mldir, "ML.pkl")
			
				if skipdone and os.path.exists(mldir) and os.path.isfile(mlpickle):
					print 'Skipping %s' % mldir
					continue

				if needtoload:
				
					if os.path.exists(self.simgalfilepath(subfield,nimg=None)):
						print "Loading from EXISTING summary pkl..."
						galaxies = megalut.utils.readpickle(self.simgalfilepath(subfield,nimg=None))
				
					else:
					
						for nimg in range(self.nsimimages):
							# We read in the database
							print "Loading %s..." % self.simgalfilepath(subfield,nimg)
							galaxies+=megalut.utils.readpickle(self.simgalfilepath(subfield,nimg))
						#print len(galaxies)

					print "Loaded %i galaxies for training..." % len(galaxies)
					# We use only good galaxies for training
					goodgalaxies = [g for g in galaxies if g.isgood()]
					needtoload = False
					
	
				
				ml = megalut.ml.ML(mlparams, toolparams, workdir=mldir)
				ml.train(goodgalaxies)
				# We save the ML object
				# TODO Save this to the original pickle ???
				megalut.utils.writepickle(ml, mlpickle)
			
				# We predict (mandatory, as the next mlparams might use the predicted stuff !)
				ml.predict(goodgalaxies)	
				megalut.galaxy.printmymetrics(goodgalaxies)
	
			
				if saveselfpredict:
					#if self.nsimimages != 1:
					#	raise RuntimeError("does not work, has to be reimplemented")
					# We save the *galaxies* (not only goodgalaxies !). goodgalaxies are part of galaxies and have been updated in place.
					megalut.utils.writepickle(galaxies, self.simgalfilepath(subfield,nimg=None))
					megalut.galaxy.export(galaxies, self.simgalfilepath(subfield,nimg=None)+".fits")
				
				
			"""
			if type(galaxies[0].pre_g1) == float or len(galaxies[0].pre_g1)!=self.NN_committee_members:
				print '! WARNING: The format of the class is decrepated or of wrong length.'

				for g in galaxies:
					g.pre_g1 = np.zeros(self.NN_committee_members)
					g.pre_g2 = np.zeros(self.NN_committee_members)
					g.pre_flux = np.zeros(self.NN_committee_members)
					g.pre_rad = np.zeros(self.NN_committee_members)
					g.pre_sersicn = np.zeros(self.NN_committee_members)

				print 'Corrected to arrays of %d in length' % len(g.pre_sersicn)
				skipdone=False
				megalut.utils.writepickle(galaxies, self.simgalfilepath(subfield))
			"""
	
			"""
			# We train each machine learning in a dedicaded directory (as SkyNet, for example, needs lots of files...)
			for committee_number in range(self.NN_committee_members):
				# ML 1 : predicting the ellipticity/shear g
				gmldir = os.path.join(self.simdir(), "g-ml-%03i-%i" % (subfield, committee_number))
				gmpickle = os.path.join(self.simdir(), "g-ml-%03i-%i/ML.pkl" % (subfield, committee_number))
				if skipdone and os.path.exists(gmldir) and os.path.isfile(gmpickle):
					print 'Skipping %s' % gmldir
					continue
			

				gml = megalut.ml.ML(features=gfeatures, labels=glabels, predlabels=gpredlabels, workdir=gmldir, committee_member_id=committee_number)
				gml.train(goodgalaxies, nhid = [30], max_iter = 300)
				gml.predict(goodgalaxies)
				# We save the ML object, so that we can reuse it when computing predictions.
				megalut.utils.writepickle(gml, os.path.join(gmldir, "ML.pkl"))
			
			
				# We print out some simple metrics comparing truth and predictions :
				metrics = megalut.galaxy.mymetrics(goodgalaxies)
				print "g1 : rms %8.5f, mad %8.5f" % (metrics["rms_g1"], metrics["mad_g1"])
				print "g2 : rms %8.5f, mad %8.5f" % (metrics["rms_g2"], metrics["mad_g2"])
			"""
	
	

	def plotpresummary(self, subfields, save=True):
		"""
		Plots that compare predicted to true parameters, for simulated galaxies.
		"""
		for subfield in subfields:
			goodgalaxies = []
			galaxies = megalut.utils.readpickle(self.simgalfilepath(subfield,None))
			goodgalaxies += [g for g in galaxies if g.isgood()]
	
			if save:plotfilepath = os.path.join(self.simdir(), "presummary-%03i.png" % (subfield))
			else: plotfilepath=None
			megalut.plots.presummary(goodgalaxies, plotfilepath, title = str(self.branch) + " (%03i)" % (subfield))



	def plotprerrbin(self, subfields, save=True):
		"""
		you can give me obssubfields, I pick the right simsubfields myself...
		
		"""
		for subfield in subfields:
			
			
			if self.branch[0] in ["control", "real_galaxy", "multiepoch"]:
				if self.branch[2] == "constant":
					simsubfield = subfield
				elif self.branch[2] == "variable":
					simsubfield = int(subfield/20)*20
			else:
				continue
			
			simgalaxies = megalut.utils.readpickle(self.simgalfilepath(simsubfield,None))
			goodsimgalaxies = [g for g in simgalaxies if g.isgood()]

			obsgalaxies = megalut.utils.readpickle(self.obsgalfilepath(subfield))
			goodobsgalaxies = [g for g in obsgalaxies if g.isgood()]

			
			if self.branch[1] == "space":
				sizeratiomax = 12.0
				snrmax = 250.0
			else:
				sizeratiomax = 3.0
				snrmax = 200.0

			if save:
				plotfilepath = os.path.join(self.simdir(), "prerrbin-%03i.png" % (subfield))
			else:
				plotfilepath = None
				
			megalut.plots.prerrbin_plot(simgalaxies=goodsimgalaxies, obsgalaxies=goodobsgalaxies,
				filepath=plotfilepath, title = str(self.branch) + " (%03i)" % (subfield),
				sizeratiomax = sizeratiomax, snrmax=snrmax)

		
		
		
	def predict(self, paramlist):
		"""
		Fifth task : predict shape of *observed* galaxies, using the Machine Learnings trained by the previous task.
		Give me the same paramlist as you gave to the training. 
		"""
		
		print '\n'*3
		message = 'START OF PREDICTIONS'
		print message
		print "="*len(message)

		for subfield in self.obssubfields:
			
			print "Predicting obssubfield %i..." % (subfield)
			
			# We read in the database of observed galaxies
			galaxies = megalut.utils.readpickle(self.obsgalfilepath(subfield))
						
			# Which simsubfield should I use ?
			if self.branch[0] in ["control", "real_galaxy", "multiepoch", "variable_psf"]:
				if self.branch[2] == "constant":
					simsubfield = subfield
				elif self.branch[2] == "variable":
					simsubfield = int(subfield/20)*20
			else:
				raise RuntimeError("Don't know how to use this branch !")
			
			print "... using simsubfield %i." % (simsubfield)

			for (mlparams, toolparams) in paramlist:
			
				# We compute the predictions one ML after the other.
				
				mldir = os.path.join(self.simdir(), "ml-%03i-%s-%s-%s" % (simsubfield, mlparams.name, toolparams.tool, toolparams.name))
				mlpickle = os.path.join(mldir, "ML.pkl")
				ml = megalut.utils.readpickle(mlpickle)
				ml.predict(galaxies)
			
			
			# Little hack, we also copy the PSF size into the observations
			
			if self.branch[0] in ["control", "real_galaxy", "multiepoch"]:
				print "Copying PSF size info..."
				simgalaxies = megalut.utils.readpickle(self.simgalfilepath(simsubfield,None))
				if not hasattr(simgalaxies[0], "mes_gs_psf_sigma"):
					print "warning, PSF not measured..."
					obs_psf_sigma = -1.0
				else:
					mes_gs_psf_sigma = np.array([g.mes_gs_psf_sigma for g in simgalaxies])
					assert np.std(mes_gs_psf_sigma) == 0.0
					obs_psf_sigma = mes_gs_psf_sigma[0]
				
				for g in galaxies:
					g.mes_gs_psf_sigma = obs_psf_sigma
					g.mes_gs_sizeratio = g.mes_gs_sigma / obs_psf_sigma
	
			
			# And save this back to the database
			megalut.utils.writepickle(galaxies, self.obsgalfilepath(subfield))
			megalut.galaxy.export(galaxies, self.obsgalfilepath(subfield)+".fits")
	
	

	def plotobsratiorad(self, save=True):
		for subfield in self.obssubfields:
			galaxies = megalut.utils.readpickle(self.obsgalfilepath(subfield))
			stars = megalut.utils.readpickle(self.obsstarfilepath(subfield))

			if save:plotfilepath = os.path.join(self.obsdir(), "obsratiorad-%03i.png" % (subfield))
			else: plotfilepath=None

			megalut.plots.compareradgalpsf(galaxies,stars,plotfilepath)
		

	
	def simpredict(self, paramlist, testsubfield, mlsubfield):
		"""
		For tests and tuning !
		Allows to predict *simulations* with MLs trained on other simulations.
		
		I do NOT update any files. Everything happens just in memory, and I give you back the predictions.
		
		"""
	
		testgalaxies=[]
		for nimg in range(self.nsimimages):
			testgalaxies += megalut.utils.readpickle(self.simgalfilepath(testsubfield,nimg))
						
		for (mlparams, toolparams) in paramlist:
			
			# We compute the predictions one ML after the other.
			mldir = os.path.join(self.simdir(), "ml-%03i-%s-%s-%s" % (mlsubfield, mlparams.name, toolparams.tool, toolparams.name))
			mlpickle = os.path.join(mldir, "ML.pkl")
			ml = megalut.utils.readpickle(mlpickle)
			ml.predict(testgalaxies)
		
		megalut.galaxy.printmymetrics(testgalaxies)
		return testgalaxies
		
	
	def setflag(self, constrains):
		"""
		I go over the obssubfield galaxy catalogs, and set the flag of each galaxy
		"""
		
		for subfield in self.obssubfields:
			
			print "Setting flag in obssubfield %i..." % (subfield)
			
			# We read in the database of observed galaxies
			galaxies = megalut.utils.readpickle(self.obsgalfilepath(subfield))
				
			megalut.galflag.setflag(galaxies, constrains)
		
			nflag = len([g for g in galaxies if g.flag > 0])
			print "Flagged %i out of %i galaxies" % (nflag, len(galaxies))	
			# And save this back to the database
			megalut.utils.writepickle(galaxies, self.obsgalfilepath(subfield))
			#megalut.galaxy.export(galaxies, self.obsgalfilepath(subfield)+".fits")
	
		
		
		
	
	def writeout(self, weight=None, weightparams=None, fact=None, use_radpsf=False, gmax=None, ignoreflag=False):
		"""
		Write the output catalogs
		
		You can choose differents weights (see code below)
		"""
		
		if not os.path.exists(self.outdir()):
			os.mkdir(self.outdir())
		
		for subfield in self.obssubfields:
			
			# We read in the database of observed galaxies
			galaxies = megalut.utils.readpickle(self.obsgalfilepath(subfield))

			if use_radpsf:
				stars = megalut.utils.readpickle(self.obsstarfilepath(subfield))
				rad_psf=0.
				fwhm_psf=0.
				for s in stars:
					fwhm_psf += s.mes_fwhm
					rad_psf += s.mes_equivrad
				rad_psf/=float(len(stars))
				fwhm_psf/=float(len(stars))
				radpsf=fwhm_psf
			else:radpsf=None
			
			print "Using weight : %s" % (weight)
			if weight=="flux":
				for g in galaxies:
					g.weight = np.clip(g.mes_flux, 0.0, 80.0)
			elif weight=="stddev":
				varname1 = "pre_g1_committee_%s_%s" % (weightparams['g1'][1], weightparams['g1'][0])
				varname2 = "pre_g2_committee_%s_%s" % (weightparams['g2'][1], weightparams['g2'][0])
				varname3 = "pre_flux_committee_%s_%s" % ('flux', weightparams['g2'][0])
				varname4 = "pre_sersicn_committee_%s_%s" % ('sersicn', weightparams['g2'][0])
				varname5 = "pre_rad_committee_%s_%s" % ('rad', weightparams['g2'][0])
				pre1=[]
				pre2=[]
				pre3=[]
				pre4=[]
				pre5=[]

				for g in galaxies:
					pre1.append(getattr(g, varname1))
					pre2.append(getattr(g, varname2))
					pre3.append(getattr(g, varname3))
					pre4.append(getattr(g, varname4))
					pre5.append(getattr(g, varname5))
				pre1=np.asarray(pre1)
				pre2=np.asarray(pre2)
				pre3=np.asarray(pre3)
				pre4=np.asarray(pre4)
				pre5=np.asarray(pre5)

				weights = (5.- (np.std(pre1, axis=1)/np.amax(np.std(pre1, axis=1)))**weightparams['index'] - (np.std(pre2, axis=1)/np.amax(np.std(pre2, axis=1)))**weightparams['index'] - (np.std(pre3, axis=1)/np.amax(np.std(pre3, axis=1)))**weightparams['index'] - (np.std(pre4, axis=1)/np.amax(np.std(pre4, axis=1)))**weightparams['index'] - (np.std(pre5, axis=1)/np.amax(np.std(pre5, axis=1)))**weightparams['index'] )/5.

				for ig, g in enumerate(galaxies):
					g.weight = weights[ig]		
		
			# And write the output catalogs
			if weight != None:
				weightt=True
			else: weightt=False

			"""import pylab as plt
			plt.figure()
			title = "%s%s%s - obs %03d" % (self.branch[0][0], self.branch[1][0],self.branch[2][0], subfield)
			plt.title(title)
			plt.hist(weights,bins=1000)
			plt.show()
			continue"""

			io.writeshearcat(galaxies, os.path.join(self.outdir(), "%03i.cat" % (subfield)), weight=weight, fact=fact, radpsf=radpsf, gmax=gmax, ignoreflag=ignoreflag)
				

		
		
	def presubmission(self, corr2path=".", use_weights=False):
		"""
		Prepares the submission by computing the correlation functions.
		
		For this it uses the "presubmission_scripts", that are now part of this SVN.
		Watch for updates from GREAT3 !
		"""

		presubdir = os.path.join(os.path.dirname(__file__), "presubmission_script")
		presubscriptpath = os.path.join(presubdir, "presubmission.py")
		catpath = os.path.join(self.outdir(), "*.cat")
		branchcode = "-".join(self.branch) # Not required given our filenames, but just to be sure.
		outfilepath = self.subfilepath()
		corr2path = os.path.join(corr2path, 'corr2')
		
		if use_weights:
			cmd = "python %s %s -b %s -w 3 -c2 %s -o %s" % (presubscriptpath, catpath, branchcode, corr2path, outfilepath)
		else:
			print "I am NOT using weights !"
			cmd = "python %s %s -b %s -c2 %s -o %s" % (presubscriptpath, catpath, branchcode, corr2path, outfilepath)
		os.system(cmd)
		

	def final_plots(self):
		"""
		Plots the values contained in the output files
		"""

		megalut.great3.plots.plot_results(self.subfilepath(), shear=self.branch[2], fig_dir=self.outdir())


	def simcommittee_plots(self, params, mlplotparam, save=True):
		"""
		Plots the committee figures
		"""
		for subfield in self.simsubfields:
		
			galaxies=self.simpredict(params, testsubfield=subfield, mlsubfield=subfield)

			galaxies = [g for g in galaxies if g.isgood()]

			if save:
				filepathsca = os.path.join(self.outdir(), "simcommittee_scatterplot-%03i.png" % (subfield))
				if 'color'  in mlplotparam:
					filepathstd = os.path.join(self.outdir(), "simcommittee_stddevplot-color%s-%03i.png" % (mlplotparam['color'],subfield))
				else:
					filepathstd = os.path.join(self.outdir(), "simcommittee_stddevplot-%03i.png" % (subfield))
			else:
				filepathstd = filepathsca = None

			title = "%s%s%s - sim %03d" % (self.branch[0][0], self.branch[1][0],self.branch[2][0], subfield)

			megalut.plots.committee_plot(megalut.plots.scatterplot,galaxies,mlparam=mlplotparam,filepath=filepathsca,title=title)
			megalut.plots.committee_plot(megalut.plots.stddevplot,galaxies,mlparam=mlplotparam,filepath=filepathstd,title=title)

	def obscommittee_plots(self, params, mlplotparam, save=True):
		"""
		Plots the committee figures
		"""
		for subfield in self.obssubfields:
		
			galaxies=megalut.utils.readpickle(self.obsgalfilepath(subfield))

			galaxies = [g for g in galaxies if g.isgood()]

			if save:
				filepathsca = os.path.join(self.outdir(), "obscommittee_scatterplot-%03i.png" % (subfield))
				if 'color'  in mlplotparam:
					filepathstd = os.path.join(self.outdir(), "obscommittee_stddevplot-color%s-%03i.png" % (mlplotparam['color'],subfield))
				else:
					filepathstd = os.path.join(self.outdir(), "obscommittee_stddevplot-%03i.png" % (subfield))
			else:
				filepathstd = filepathsca = None

			title = "%s%s%s - obs %03d" % (self.branch[0][0], self.branch[1][0],self.branch[2][0], subfield)

			megalut.plots.committee_plot(megalut.plots.obsscatterplot,galaxies,mlparam=mlplotparam,filepath=filepathsca,title=title)
			megalut.plots.committee_plot(megalut.plots.obsstddevplot,galaxies,mlparam=mlplotparam,filepath=filepathstd,title=title)


	################################################################################################
	
	
	
	
	def resetsimpred(self):
		
		for subfield in self.simsubfields:
			galaxies = megalut.utils.readpickle(run.simgalfilepath(0))
			for g in galaxies:
				g.resetpred()
			megalut.utils.writepickle(galaxies, run.simgalfilepath(0))

