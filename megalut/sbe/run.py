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
		
		if not os.path.exists(self.workdir):
			os.makedirs(self.workdir)

	
	def makecats(self):
		"""
		Read the SBE data files and prepare MegaLUT "observations" catalogs.
		For each SBE image, an input catalog is written into the workdir.
		"""

		filenames = io.get_filenames(self.sbedatadir)
		
		# Hardcoded for now:
		stampsize = 200
		n = 32
		
		logger.info("Will make %i cats..." % len(filenames))
		
		for filename in filenames:#[:10]:
			
			datafilepath = io.datafile(filename)
			imagefilepath = io.imagefile(filename)
			workprefix = io.workprefix(filename, self.workdir)
			catfilepath = workprefix + "-inputcat.pkl"
			imageworkdirfilepath = workprefix + "-imageworkdir"
			
			# We read the data file and turn it into an astropy table
			cat = astropy.io.ascii.read(datafilepath)
			
			# Let's keep this filename
			cat.meta["sbefilename"] = filename
			cat.meta["workprefix"] = workprefix
			
			# Let's convert the true shape parameters into more convenient forms:
			
			cat["PSF_e1"] = cat["PSF_shape_1"] * np.cos(2.0*cat["PSF_shape_2"]*np.pi/180)
			cat["PSF_e2"] = cat["PSF_shape_1"] * np.sin(2.0*cat["PSF_shape_2"]*np.pi/180)
			cat["Galaxy_e1"] = cat["Galaxy_shape_1"] * np.cos(2.0*cat["Galaxy_shape_2"]*np.pi/180)
			cat["Galaxy_e2"] = cat["Galaxy_shape_1"] * np.sin(2.0*cat["Galaxy_shape_2"]*np.pi/180)
			cat["Galaxy_g1"] = cat["Galaxy_shear_1"] * np.cos(2.0*cat["Galaxy_shear_2"]*np.pi/180)
 			cat["Galaxy_g2"] = cat["Galaxy_shear_1"] * np.sin(2.0*cat["Galaxy_shear_2"]*np.pi/180)
   
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
		

	def measobs(self, measfct):
		"""
		Runs the measfct on the observations
		"""
		
		incatfilepaths = glob.glob(os.path.join(self.workdir, "*-inputcat.pkl"))
		outcatfilepaths = [incat.replace("inputcat", "meascat") for incat in incatfilepaths]
		
		logger.info("Measuring %i cats..." % len(incatfilepaths))
	
		measfctkwargs = {"stampsize":150} # 200 seems exagerated!
	
		megalut.meas.run.general(incatfilepaths, outcatfilepaths, measfct, measfctkwargs, ncpu=self.ncpu, skipdone=False)
		


	def measobscheckplot(self):
		
		catfilepaths = glob.glob(os.path.join(self.workdir, "*-meascat.pkl"))
	
		for catfilepath in catfilepaths:#[:1]:
			
			
			cat = megalut.tools.io.readpickle(catfilepath)
			
			plotfilepath = cat.meta["workprefix"] + "-measobscheckplot.png"
			
			plot.meascheck(cat, plotfilepath)
	
	
	def mixobscheckplot(self):
		
		catfilepaths = glob.glob(os.path.join(self.workdir, "*-meascat.pkl"))
		
	
		somefiles = random.sample(catfilepaths, 200)
		
		#print somefiles
		somecats = [megalut.tools.io.readpickle(f) for f in somefiles]
		for cat in somecats:
			cat.meta = {}
		
		cat = astropy.table.vstack(somecats, join_type="exact", metadata_conflicts="error")
		plot.meascheck(cat)
	
		#for cat in somecats:
		#plot.test(cat)
	
	
	def drawsims(self, simparams, n=10, ncat=1, nrea=1):
		
		
		drawcatkwargs = {"n":n, "stampsize":150}
		drawimgkwargs = {}
		
		megalut.sim.run.multi(self.workdir, simparams, drawcatkwargs, drawimgkwargs, 
			psfcat = None, ncat=ncat, nrea=nrea, ncpu=self.ncpu,
			savepsfimg=True, savetrugalimg=True)


	def meassims(self):
		pass
		

	
	def writeresults(self):
		
		"""
		catfilepaths = glob.glob(os.path.join(self.workdir, "*-meascat.pkl"))
		
		
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
	
	
	
		
	
