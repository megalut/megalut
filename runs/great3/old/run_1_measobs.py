import multiprocessing
import datetime
import numpy as np
import astropy.table

import megalut.tools as tools
import megalut.meas as meas

import megalutgreat3 as mg3

import config
import g3measfct as measfct

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create an instance of the GREAT3 class
great3 = mg3.great3.Great3("control", "ground", "constant",
	datadir = config.datadir,
	workdir = config.workdir,
	subfields = config.subfields)
great3.save_config()

# Preparing the different parameters for the workers
wslist = [[great3, subfield] for subfield in great3.subfields]

#--------------------------------------------------------------------------------------------------

def _worker(wparams):
	# We don't bother reading the starcat, and just make one
	great3, subfield = wparams
	
	stars = []
	for i in range(3):
		for j in range(3):
			stars.append( [0.5 + great3.stampsize()/2.0 + i*great3.stampsize(), 0.5 + great3.stampsize()/2.0 + j*great3.stampsize()] )
	stars = np.array(stars)
	
	starcat = astropy.table.Table([stars[:,0], stars[:,1]], names=('psfx', 'psfy'))
	#print starcat
	
	# To measure the stars, we attach the image:
	starcat.meta["img"] = tools.imageinfo.ImageInfo(
		filepath=great3.starimgfilepath(subfield),
		xname="psfx",
		yname="psfy",
		stampsize=great3.stampsize(),
		workdir=great3.get_path("obs", "star_%i_measworkdir" % subfield)
		)

	starcat = measfct.psf(starcat, branch=great3)
	
	#print starcat
	
	tools.io.writepickle(starcat, great3.get_path("obs", "star_%i_meascat.pkl" % subfield))
			
	
	# Lists that we will pass to meas.run.general():
	incatfilepaths = []
	outcatfilepaths = []
			
	
	incat = mg3.io.readgalcat(great3, subfield)
	
	# We add PSF info to this field. PSFs are already measured, and we just take the first one:
	
	starcat = tools.io.readpickle(great3.get_path("obs", "star_%i_meascat.pkl" % subfield))
	starcat.meta = {} # Dump the "img" entry
	matchedstarcat = starcat[np.zeros(len(incat), dtype=int)]
	assert len(incat) == len(matchedstarcat)
	for colname in incat.colnames:
		if colname in matchedstarcat.colnames:
			raise RuntimeError("colname %s appears twice" % colname)
	
	incat = astropy.table.hstack([incat, matchedstarcat], join_type="exact", metadata_conflicts="error")
	
	#print incat.colnames
	
	# Add the reference to the img and psf stamps:
	
	incat.meta["img"] = tools.imageinfo.ImageInfo(
		filepath=great3.galimgfilepath(subfield),
		xname="x",
		yname="y",
		stampsize=great3.stampsize(),
		workdir=great3.get_path("obs", "img_%i_measworkdir" % subfield)
		)

	incat.meta["psf"] = tools.imageinfo.ImageInfo(
		filepath=great3.starimgfilepath(subfield),
		xname="psfx",
		yname="psfy",
		stampsize=great3.stampsize(),
		workdir=None
		)

	# Write the input catalog
	incatfilepath = great3.get_path("obs", "img_%i_incat.pkl" % subfield)
	tools.io.writepickle(incat, incatfilepath)
	incatfilepaths.append(incatfilepath)
	
	# Prepare the filepath for the output catalog
	outcatfilepath = great3.get_path("obs", "img_%i_meascat.pkl" % subfield)
	outcatfilepaths.append(outcatfilepath)

	# We pass some kwargs for the measfct
	measfctkwargs = {"branch":great3}

	# And we run all this, there's only 1 page per subfield, so ncpu = 1
	meas.run.general(incatfilepaths, outcatfilepaths, measfct.galaxies, measfctkwargs=measfctkwargs,
					ncpu=1, skipdone=config.skipdone)

	
#--------------------------------------------------------------------------------------------------

if config.ncpu == 0:
	try:
		ncpu = multiprocessing.cpu_count()
	except:
		logger.warning("multiprocessing.cpu_count() is not implemented!")
		ncpu = 1
else:
	ncpu = config.ncpu
	
starttime = datetime.datetime.now()

logger.info("Starting the measurement on %i subfields using %i CPUs" % (len(wslist), ncpu))

if ncpu == 1: # The single process way (MUCH MUCH EASIER TO DEBUG...)
	map(_worker, wslist)

else:
	pool = multiprocessing.Pool(processes=ncpu)
	pool.map(_worker, wslist)
	pool.close()
	pool.join()

endtime = datetime.datetime.now()
logger.info("Done, the total measurement time for all subfields was %s" % (str(endtime - starttime)))
		