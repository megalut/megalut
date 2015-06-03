import megalut
import megalut.meas

import numpy as np
import os
import sys
import astropy
import glob
import random

import logging
logger = logging.getLogger(__name__)

import io
import plot
import analysis

class Run():


	def __init__(self, sbedatadir, workdir, ncpu=4):
		"""
		:param sbedatadir: where the SBE data is
		:param workdir: where megalut can write any intermediary files
		:param ncpu: max number of CPU to use
		"""
		self.sbedatadir = sbedatadir
		self.workdir = workdir
		self.ncpu = ncpu
		
		self.workobsdir = os.path.join(self.workdir, "obs")
		self.worksimdir = os.path.join(self.workdir, "sim")
		self.workmldir = os.path.join(self.workdir, "ml")
		
		
		if not os.path.exists(self.workdir):
			os.makedirs(self.workdir)
		if not os.path.exists(self.workobsdir):
			os.makedirs(self.workobsdir)
		if not os.path.exists(self.worksimdir):
			os.makedirs(self.worksimdir)
		if not os.path.exists(self.workmldir):
			os.makedirs(self.workmldir)

		self.groupobspath = os.path.join(self.workobsdir, "groupobs.pkl")


	
	def makecats(self, onlyn = None, sbe_sample_scale=0.05):
		"""
		Read the SBE data files and prepare MegaLUT "observations" catalogs.
		For each SBE image, an input catalog is written into the workdir.
		"""

		filenames = io.get_filenames(self.sbedatadir)
		if onlyn != None:
			filenames = filenames[:onlyn]
		
		
		# Hardcoded for now:
		stampsize = 200
		n = 32
		
		logger.info("Will make %i cats..." % len(filenames))
		
		for filename in filenames:
			
			datafilepath = io.datafile(filename)
			imagefilepath = io.imagefile(filename)
			workname = io.workname(filename)
			catfilepath = os.path.join(self.workobsdir, workname + "-inputcat.pkl")
			imageworkdirfilepath = os.path.join(self.workobsdir, workname + "-imageworkdir")
			
			if os.path.exists(catfilepath):
				logger.info("Skipping '%s', catalog already exists" % (workname))
				continue
			
			# We read the data file and turn it into an astropy table
			cat = astropy.io.ascii.read(datafilepath)
			
			# Let's keep the file identification also in the meta dict:
			cat.meta["sbefilename"] = filename # very weird SBE thing, without extension...
			cat.meta["workname"] = workname
			
			# Let's convert the true shape parameters into more convenient forms:
			
			cat["PSF_e1"] = cat["PSF_shape_1"] * np.cos(2.0*cat["PSF_shape_2"]*np.pi/180)
			cat["PSF_e2"] = cat["PSF_shape_1"] * np.sin(2.0*cat["PSF_shape_2"]*np.pi/180)
			cat["Galaxy_e1"] = cat["Galaxy_shape_1"] * np.cos(2.0*cat["Galaxy_shape_2"]*np.pi/180)
			cat["Galaxy_e2"] = cat["Galaxy_shape_1"] * np.sin(2.0*cat["Galaxy_shape_2"]*np.pi/180)
			cat["Galaxy_g1"] = cat["Galaxy_shear_1"] * np.cos(2.0*cat["Galaxy_shear_2"]*np.pi/180)
 			cat["Galaxy_g2"] = cat["Galaxy_shear_1"] * np.sin(2.0*cat["Galaxy_shear_2"]*np.pi/180)

			# And for convenience, include some standard MegaLUT names for the PSFs
			cat["tru_psf_g1"] = cat["PSF_e1"]
			cat["tru_psf_g2"] = cat["PSF_e2"]
			cat["tru_psf_sigma"] = cat["PSF_sigma_arcsec"] / sbe_sample_scale
   
			# We add the xid, yid, x and y columns, following an explanation by Bryan
			# on how the data/fits files should be interpreted ("like english text").
			#cat["xid"] = np.concatenate([np.arange(n) for i in range(n)])
			#cat["yid"] = np.concatenate([np.ones(n, dtype=np.int)*(n - i -1) for i in range(n)])
			# Well, not exactly. One should start y at the bottom, it seems:
			cat["xid"] = np.concatenate([np.arange(n) for i in range(n)])
			cat["yid"] = np.concatenate([np.ones(n, dtype=np.int)*i for i in range(n)])		
			cat["x"] = stampsize/2.0 + cat["xid"]*(stampsize + 1) + 0.5
			cat["y"] = stampsize/2.0 + cat["yid"]*(stampsize + 1) + 0.5
					
			# We create the ImageInfo object
			img = megalut.tools.imageinfo.ImageInfo(
				filepath = imagefilepath,
				xname = "x", yname = "y",
				stampsize = stampsize,
				workdir = imageworkdirfilepath
				)
			cat.meta["img"] = img
			
			# And save the catalog
			megalut.tools.io.writepickle(cat, catfilepath)
		

	def measobs(self, measfct, stampsize=200, skipdone=True):
		"""
		Runs the measfct on the observations
		"""
		
		incatfilepaths = glob.glob(os.path.join(self.workobsdir, "*-inputcat.pkl"))
		outcatfilepaths = [incat.replace("inputcat", "meascat") for incat in incatfilepaths]
		
		logger.info("Measuring %i cats..." % len(incatfilepaths))
	
		measfctkwargs = {"stampsize":stampsize}
	
		megalut.meas.run.general(incatfilepaths, outcatfilepaths, measfct, measfctkwargs, ncpu=self.ncpu, skipdone=skipdone)
		
		
		

	def plotobscheck(self, prefix="adamom_", g12_low=None, g12_high=None):
		"""
		One checkplot for every SBE "file"
		"""
		
		catfilepaths = glob.glob(os.path.join(self.workobsdir, "*-meascat.pkl"))
	
		for catfilepath in catfilepaths:#[:1]:
			
			
			cat = megalut.tools.io.readpickle(catfilepath)
			
			plotfilepath = os.path.join(self.workobsdir, cat.meta["workname"] + "-measobscheckplot.png")
			
			plot.meascheck(cat, plotfilepath, prefix, g12_low, g12_high)
	

	def groupobs(self, nfiles="all"):
		"""
		Groups either all or some tractable sample of the obs measurements into a single catalog, handy for testing distributions.
		"""
		
		catfilepaths = glob.glob(os.path.join(self.workobsdir, "*-meascat.pkl"))
		
		if nfiles == "all":
			somefiles = catfilepaths
		else:
			somefiles = random.sample(catfilepaths, nfiles)
		
		somecats = [megalut.tools.io.readpickle(f) for f in somefiles]
		for cat in somecats:
			cat.meta = {} # To avoid conflicts when stacking
		
		groupcat = astropy.table.vstack(somecats, join_type="exact", metadata_conflicts="error")
		
		megalut.tools.io.writepickle(groupcat, self.groupobspath)
		
	
	def showmeasobsfrac(self, fields = ["skystd", "sewpy_FLUX_AUTO", "adamom_flux"]):
		"""
		For testing purposes, computes measurement success fractions.
		"""
		
		cat = megalut.tools.io.readpickle(self.groupobspath)
		#print cat.colnames
				
		for field in fields:
			nbad = np.sum(cat[field].mask)
			ntot = len(cat)
			print "%20s: %.3f%% ( %i / %i are masked)" % (field, 100.0*float(ntot - nbad)/float(ntot), nbad, ntot)
			
		#import matplotlib.pyplot as plt
		#plt.plot(cat["sewpy_FLUX_AUTO"], cat["adamom_flux"], "b.")
		#plt.show()

	def plotmixobscheck(self, prefix='adamom_', filepath=None):
		"""
		One checkplot mixing several SBE files.
		"""
		
		cat = megalut.tools.io.readpickle(self.groupobspath)
		plot.meascheck(cat, prefix=prefix, filepath=filepath)
	
	
	
	def drawsims(self, simparams, n=10, ncat=1, nrea=1, stampsize=200):
		"""
		Draws many sims on several cpus, in the standard MegaLUT style.
		"""
		
		drawcatkwargs = {"n":n, "stampsize":stampsize}
		drawimgkwargs = {}
		
		megalut.sim.run.multi(self.worksimdir, simparams, drawcatkwargs, drawimgkwargs, 
			psfcat = None, ncat=ncat, nrea=nrea, ncpu=self.ncpu,
			savepsfimg=True, savetrugalimg=True)


	def meassims(self, simparams, measfct, stampsize=200):
		"""
		Idem
		"""
		measfctkwargs = {"stampsize":stampsize}
		megalut.meas.run.onsims(self.worksimdir, simparams, self.worksimdir, measfct, measfctkwargs, ncpu=self.ncpu)
		


	def plotsimobscompa(self, simparams, prefix="adamom_", filepath=None):
		"""
		Again, a classic...
		"""
		
		# We read the first rea of the sims
		simcatpath = megalut.meas.utils.simmeasdict(self.worksimdir, simparams).values()[0][0]
		simcat = megalut.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, simcatpath))
				
		# And a bunch of the obs
		obscat = megalut.tools.io.readpickle(self.groupobspath)
			
		plot.simobscompa(simcat, obscat, prefix=prefix, filepath=filepath)
		


	def avgsimmeas(self, simparams, groupcols, removecols):
		"""
		Averages the measurements on the sims accross the different realizations, and writes
		a single training catalog for the ML.
		"""	
	
		avgmeascat = megalut.meas.avg.onsims(self.worksimdir, simparams,
			groupcols=groupcols,
			removecols=removecols,
			removereas=False,
			keepfirstrea=True
		)

		megalut.tools.io.writepickle(avgmeascat, os.path.join(self.worksimdir, simparams.name, "avgmeascat.pkl"))


	def train(self, simparams, trainparamslist):
		"""
		
		"""
		
		# We load the training catalog
		simcat = megalut.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "avgmeascat.pkl"))
		
		# We reject crap ones
		ngroupstats = simcat.meta["ngroupstats"]
		simcat = simcat[simcat["adamom_flux_n"] > float(ngroupstats)/2.0]
		logger.info("Keeping %i galaxies for training" % (len(simcat)))
		
		megalut.tools.io.writepickle(simcat, os.path.join(self.workmldir, "traincat.pkl"))
		#plot.simcheck(simcat)
		
		megalut.learn.run.train(simcat, self.workmldir, trainparamslist, ncpu=self.ncpu)
			
		
	
	def predictsims(self, simparams, trainparamslist):
		
		cat = megalut.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "avgmeascat.pkl"))
		
		#cat = megalut.learn.run.predict(cat, self.workmldir, trainparamslist, tweakmode="all")
		cat = megalut.learn.run.predict(cat, self.workmldir, trainparamslist, tweakmode="_rea0")
		
		megalut.tools.io.writepickle(cat, os.path.join(self.workmldir, "selfprecat.pkl"))
	


	def plotpredsims(self):
		
		cat = megalut.tools.io.readpickle(os.path.join(self.workmldir, "selfprecat.pkl"))
		plot.predscatter(cat)
		
	def analysepredsims(self):
		"""
		Measures m and c on the sims.
		Does not fully work as PSF_shape_2 is not present in the sims catalog. Easy to add, but do we need this ?
		"""
		
		cat =  megalut.tools.io.readpickle(os.path.join(self.workmldir, "selfprecat.pkl"))
		
		analysis.analyse(cat, 
			colname_PSF_ellipticity_angles_degrees="PSF_shape_2",
			colname_e1_guesses="pre_g1",
			colname_e2_guesses="pre_g2",
			colname_gal_g1s="tru_g1",
			colname_gal_g2s="tru_g2",
		)



	def predictobs(self, trainparamslist):
	
		cat = megalut.tools.io.readpickle(self.groupobspath)
		
		cat = megalut.learn.run.predict(cat, self.workmldir, trainparamslist, tweakmode="") # Drop the "_mean" which does not exists for obs
		
		megalut.tools.io.writepickle(cat, os.path.join(self.workmldir, "obsprecat.pkl"))

	
	def analysepredobs(self):
		"""
		Measures m and c directly from the catalog, without havign to write the ascii output files.
		"""
		
		cat =  megalut.tools.io.readpickle(os.path.join(self.workmldir, "obsprecat.pkl"))
		
		analysis.analyse(cat, 
			colname_PSF_ellipticity_angles_degrees="PSF_shape_2",
			colname_e1_guesses="pre_g1",
			colname_e2_guesses="pre_g2",
			colname_gal_g1s="Galaxy_g1",
			colname_gal_g2s="Galaxy_g2",
		)



	def writepredsbe(self, outdir=None):
		"""
		
		Warning, this writes results into the sbedatadir, as does the example script
		"""
		
		# When merging the catalogs, we lost the info about filenames.
		# It might be that in the following we mix up file names with respect to the original drawing.
		# But given that each file is equivalent (params randomly drawn from the same distribs)
		# this will produce exactly the same results.
		
		filenames = io.get_filenames(self.sbedatadir)
		#print "\n".join(filenames)
		
		cat = megalut.tools.io.readpickle(os.path.join(self.workmldir, "obsprecat.pkl"))
		
		# As the SBE scripts are fully self-inconsistent, we have to rename even their own columns here...
		
		cat["PSF_shape_angle_degrees"] = cat["PSF_shape_2"]
		cat["e1_guess"] = cat["pre_g1"]
		cat["e2_guess"] = cat["pre_g2"]
		cat["gal_g1"] = cat["Galaxy_g1"]
		cat["gal_g2"] = cat["Galaxy_g2"]
		cat["weight"] = np.logical_not(cat["pre_g1"].mask).astype("float")
		
		cat.keep_columns(["PSF_shape_angle_degrees", "e1_guess", "e2_guess", "gal_g1", "gal_g2", "weight"])
		
		print "For testing, here are a few rows of your catalog:"
		print cat[:20]
		
		
		
		for (i, filename) in enumerate(filenames):
			
			subcat = cat[i*1024:(i+1)*1024].filled(999.0)
			assert len(subcat) == 1024
			
			#print filename
			exportpath = filename + "_res.dat"
			#exportpath = "test.txt"
			
			subcat.write(exportpath, format='ascii.commented_header', delimiter="\t")
			
			logger.info("Wrote %s" % exportpath)


			#exit()
	
	


	def predictobs_indiv(self, trainparamslist):
		"""
		Predicts each SBE file separately DO WE NEED THIS
		"""
		"""
		incatfilepaths = glob.glob(os.path.join(self.workobsdir, "*-meascat.pkl"))
		
		logger.info("Predicting %i cats..." % len(incatfilepaths))
	
		for incatfilepath in incatfilepaths:

			
			cat = megalut.tools.io.readpickle(incatfilepath)
			outcatfilepath = os.path.join(self.workmldir, cat.meta["workname"] + "-precat.pkl")

			cat = megalut.learn.run.predict(cat, self.workmldir, trainparamslist, totweak="_mean", tweakmode="")
		
			# The uncertainties:
			#cat = megalut.learn.run.predict(cat, self.mlworkdir, errtrainparamslist, totweak="_rea0", tweakmode="")
		
			megalut.tools.io.writepickle(cat, outcatfilepath)
		"""
		


	
	def writeresults(self):
		
		"""
		catfilepaths = glob.glob(os.path.join(self.workmldir, "*-precat.pkl"))
		
		
		# Output the result data table
		
		for catfilepath in catfilepaths:
			
			cat = megalut.tools.io.readpickle(catfilepath)
			
			resfilepath = cat.meta["workprefix"] + "-measobscheckplot.png"
			cat = 
			result_filename = filename_root + mv.result_tail + mv.datafile_extension
		
		
    ascii.write([PSF_e_angles,
                 e1_guesses,
                 e2_guesses,
                 g1s,
                 g2s,
                 weights],
                result_filename,
                names=[mv.result_PSF_e_angle_colname,
                       mv.result_e1_guess_colname,
                       mv.result_e2_guess_colname,
                       mv.result_gal_g1_colname,
                       mv.result_gal_g2_colname,
                       mv.result_weight_colname],
                delimiter="\t",
                Writer=CommentedHeader)
        
		"""
	
	
	
		
	
