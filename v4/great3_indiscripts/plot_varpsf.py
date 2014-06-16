import numpy as np
import os
from datetime import datetime
import asciidata

datadir = "/obs/EPFL_GREAT3/"
workdir = "/scratch/kuntzer/varpsf"
branch = ["variable_psf", "ground", "variable"]
version= "full"


class PlotPSFField(object):
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

	def measstar(self, skipdone=True):
		for subfield in self.subfieldrange:
			print '---- Subfield %i' % (subfield)
			if skipdone and os.path.exists(self.obsstarsexpath(subfield)):
				print "Skipping %s ..." % (self.obsstarsexpath(subfield))
				continue

			# Load all the galaxies & stars
			fname_stars = self.obsstarcatpath(subfield)

			fname_gal = self.obscatfilepath(subfield)
			positions_stars = np.loadtxt(fname_stars)[:,6:]
			positions_tile_stars = np.loadtxt(fname_stars)[:,:2]
			index_star = np.arange(np.shape(positions_stars)[0])
			stars=np.zeros([np.shape(positions_stars)[0],3])
			stars[:,0:2]=positions_tile_stars
			stars[:,2]=index_star

			sexcatfilepath = os.path.join(self.savedir, "sex-%03i.cat" % (subfield))
			fname=os.path.join(self.savedir, "assoc-%03i.txt" % subfield)
			np.savetxt(fname,stars)

			starttime = datetime.now()	
	
			sexparamsdir = os.path.join(os.path.dirname(__file__),"sexparams")
			settings_sex = os.path.join(sexparamsdir, "stars.sex")
			settings_param = os.path.join(sexparamsdir, "stars.param")
			settings_conv = os.path.join(sexparamsdir, "default.conv")
			imgfilepath=self.obspsfimgfilepath(subfield)

			cmd = "nice -n 19 sex %s -c %s -PARAMETERS_NAME %s -FILTER_NAME %s -CATALOG_NAME %s -ASSOC_NAME %s" % ( imgfilepath, 
			settings_sex, settings_param, settings_conv, sexcatfilepath, fname)
			print "Running SExtractor on image %s ..." % imgfilepath

			os.system(cmd)
	
			endtime = datetime.now()
			print "This SExtractor run took %s" % (str(endtime - starttime))
			##### READOUT #####################################################
			print "Reading catalog..."
			starttime = datetime.now()	

			sexcat = asciidata.open(sexcatfilepath)
			print "We have %i stars in the sextractor catalog %s" % (sexcat.nrows, sexcatfilepath)
			#print sexcat.info()
	
			print "Identifying stars..."

		
			sindexes = sexcat['VECTOR_ASSOC2'].tonumpy() # Keep it as numpy
	
			notfound = 0
			nstars = 0
			for (sindex, s) in enumerate(stars):
				try:
					i = np.where(sindexes == sindex)[0][0]
				except IndexError:
					notfound += 1
					#print "Couldn't find galaxy %s !" % (str(g));exit();
					continue
				stars[i] = sexcat["FLUX_AUTO"][i]/sexcat["FLUXERR_AUTO"][i]
				stars[:,0:2]=positions_stars
				nstars+=1
	
			fname=self.obsstarsexpath(subfield)
			np.savetxt(fname,stars)
			print 'Wrote %s' % fname
			endtime = datetime.now()
			print "I could identify %.2f%% of the galaxies (%i out of %i are missing)." % (100.0 * float(nstars-notfound) / float(nstars), notfound, nstars)
			print "This catalog-readout took %s" % (str(endtime - starttime))
	

	def plot(self,snr_limit,show_gal=True,skipdone=True,save=False):
		import pylab as plt
		from matplotlib.ticker import NullFormatter

		# definitions for the axes
		left, width = 0.1, 0.8
		bottom, height = 0.1, 0.65
		bottom_h = left_h = 0.05#left+width+0.02

		rect_scatter = [left, 0.3, width, height]
		rect_histx 	 = [left, 0.05, width, 0.2]

		for subfield in self.subfieldrange:

			pos_star = np.loadtxt(self.obsstarsexpath(subfield))
#			pos_gal = np.loadtxt(self.obscatfilepath(subfield))

			show=np.where(pos_star[:,2]>snr_limit)
			print "Number of selected stars for subfield %i :" % subfield, np.shape(show)[1], "/", np.shape(pos_star)[0]


			# start with a rectangular Figure
			plt.figure(1, figsize=(8,10))


			axScatter = plt.axes(rect_scatter)
			axHistx = plt.axes(rect_histx)
		
			# the scatter plot:

			if show_gal:
				galpos=np.loadtxt(self.obscatfilepath(subfield))[:,[2,7,8]]
				axScatter.plot(galpos[:,1],galpos[:,2],'r.',markersize=2)

			name="-".join(self.branch)
			axScatter.set_title("%s - Subfield %i" % (name,subfield))
			axScatter.plot(pos_star[show,0],pos_star[show,1], 'b+')

			# This is useless, galaxies are on a grid
			axScatter.set_xlabel("Position x in field [deg]")
			axScatter.set_ylabel("Position y in field [deg]")

			# SNR plot
			n, bins, patches= axHistx.hist(pos_star[:,2],bins=50)
			
			axHistx.grid()
			axHistx.set_xlabel("SNR star")

			axHistx.plot([snr_limit,snr_limit],[0,np.amax(n)],'r--', lw=2)
			axHistx.arrow( snr_limit, np.amax(n)*0.95, 10, 0.0, fc="r", ec="r",head_width=np.amax(n)/15, head_length=10 )
			axHistx.annotate('%i stars' % np.shape(show)[1], xy=(1.02*snr_limit, np.amax(n)*0.82))

			if save:
				filepath = os.path.join(self.savedir,'stars_%03i-%03i.png' % (snr_limit,subfield))
				plt.savefig(filepath)
				print "Wrote %s" % (filepath)
			else:
				plt.show()
			plt.close()

	def plot_per_field(self,snr_limit=200,skipdone=True,save=False):
		import pylab as plt
		from matplotlib.ticker import NullFormatter

		# definitions for the axes
		left, width = 0.1, 0.8
		bottom, height = 0.1, 0.65
		bottom_h = left_h = 0.05#left+width+0.02

		rect_scatter = [left, 0.3, width, height]
		rect_histx 	 = [left, 0.05, width, 0.2]

		for field in self.fieldrange:
			stars_in_field = []
			all_stars = []
			for subfield in range(field*20,(field+1)*20):
				pos_star = np.loadtxt(self.obsstarsexpath(subfield))
				#show=np.where(pos_star[:,2]>snr_limit)
				for s in pos_star:
					if s[2]>snr_limit: stars_in_field.append(s)
					all_stars.append(s)
			stars_in_field=np.asarray(stars_in_field)
			all_stars=np.asarray(all_stars)

			print "Number of selected stars for field %i :" % field, np.shape(stars_in_field)[0], "/", np.shape(pos_star)[0]


			# start with a rectangular Figure
			plt.figure(figsize=(8,10))


			axScatter = plt.axes(rect_scatter)
			axHistx = plt.axes(rect_histx)
		
			# the scatter plot:
			name="-".join(self.branch)
			axScatter.set_title("%s - Field %i" % (name,field))
			axScatter.plot(stars_in_field[:,0],stars_in_field[:,1], 'b+')

			# This is useless, galaxies are on a grid
			axScatter.set_xlabel("Position x in field [deg]")
			axScatter.set_ylabel("Position y in field [deg]")

			# SNR plot
			n, bins, patches= axHistx.hist(all_stars[:,2],bins=50)
			
			axHistx.grid()
			axHistx.set_xlabel("SNR star")

			axHistx.plot([snr_limit,snr_limit],[0,np.amax(n)],'r--', lw=2)
			axHistx.arrow( snr_limit, np.amax(n)*0.95, 10, 0.0, fc="r", ec="r",head_width=np.amax(n)/15, head_length=10 )
			axHistx.annotate('%i stars' % np.shape(stars_in_field)[0], xy=(1.02*snr_limit, np.amax(n)*0.82))

			if save:
				filepath = os.path.join(self.savedir,'stars_field_%03i-%03i.png' % (snr_limit,subfield))
				plt.savefig(filepath)
				print "Wrote %s" % (filepath)
			else:
				plt.show()
			plt.close()

if __name__ == "__main__":
	run=PlotPSFField(datadir,workdir,branch,version)
	run.subfieldrange = range(20)
	run.fieldrange = range(10)
#	run.measstar()
	run.plot_per_field(snr_limit=200)
	run.plot(snr_limit=100,save=True)
