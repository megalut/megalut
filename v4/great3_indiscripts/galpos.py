import numpy as np
import os
from datetime import datetime
import asciidata
import pylab as plt

datadir = "/obs/EPFL_GREAT3/"
workdir = "/scratch/kuntzer/varpsf"
branch = ["variable_psf", "ground", "variable"]
version= "full"


class PlotGalPos(object):
	def __init__(self, datadir, workdir, branch, version, SNR=50):
		self.datadir = datadir
		self.workdir = workdir
		self.branch = branch
		self.version = version
		self.SNR=SNR

		self.savedir = os.path.join(workdir,branch[0],"-".join(self.branch) + "-%s" % (version))

		if not os.path.isdir(self.savedir):
			os.makedirs(self.savedir)

	def branchdir(self): # This is where the GREAT3 data is
		return os.path.join(self.datadir, "/".join(self.branch))

	def obspsfimgfilepath(self, subfield, epoch=0):
		return os.path.join(self.branchdir(), "starfield_image-%03i-%i.fits" % (subfield, epoch)) # This is set by GREAT3

	def obsstarcatpath(self, subfield):
		return os.path.join(self.branchdir(), 'star_catalog-%03i.txt' % subfield) # This is set by GREAT3

	def obsstarsexpath(self, subfield):
		return os.path.join(self.savedir, 'star_catalog-%03i.txt' % subfield) # This is set by GREAT3

	def obscatfilepath(self, subfield):
		return os.path.join(self.branchdir(), "star_catalog-%03i.txt" % (subfield)) # This is set by GREAT3

	def obscatfilepath(self, subfield):
		return os.path.join(self.branchdir(), "galaxy_catalog-%03i.txt" % (subfield)) # This is set by GREAT3

	
	def load_gal_in_field(self, field):
		subfield_ini=field*20
		subfield_end=(field+1)*20
		print subfield_ini, subfield_end

		fields=None
		for subfield in range(subfield_ini, subfield_end):
			sub = np.loadtxt(self.obscatfilepath(subfield))[:,[2,7,8]]
			if fields==None:
				fields=sub
			else:
				fields = np.append(fields,sub,axis=0)

		return fields




	

	def plot(self,field):


		field = self.load_gal_in_field(field)
		plt.figure()
		plt.plot(field[:,1],field[:,2],'+')
		plt.xlim([0,1])
		plt.ylim([0,1])
		

if __name__ == "__main__":
	run=PlotGalPos(datadir,workdir,branch,version)
	for i in range(10):
		run.plot(i)
	plt.show()

