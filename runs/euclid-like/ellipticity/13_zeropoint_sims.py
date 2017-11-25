import os
import shutil

import megalut.sim
import megalut.meas
import measfcts
import simparams

import config
import numpy as np
import pylab as plt 
import logging
logger = logging.getLogger(__name__)

simdir = config.zpsimdir

# Let's train for ellipticity
# We do not need Shape Noise Cancellation and no shear needeed

n = 10#0
nc = 10#0
ncat = 1
nrea = 1
zeropoint = 25.6

match_snr = False

psfcat = megalut.tools.io.readpickle(os.path.join(config.psfdir, "psf_meascat.pkl"))

res = []

while not match_snr:
	
	if os.path.exists(simdir): 
		shutil.rmtree(simdir)
	
	sp = simparams.Calc_Zerop(zeropoint)
	
	print 'TRYING', zeropoint, 'mag'
	
	megalut.sim.run.multi(
		simdir=simdir,
		simparams=sp,
		drawcatkwargs={"n":n, "nc":nc, "stampsize":config.stampsize, "pixelscale":config.pixelscale},
		drawimgkwargs={}, 
		psfcat=psfcat, psfselect="random",
		ncat=ncat, nrea=nrea, ncpu=config.ncpu,
		savepsfimg=False, savetrugalimg=False
		)
	
	megalut.meas.run.onsims(
		simdir=simdir,
		simparams=sp,
		measdir=simdir,
		measfct=measfcts.default,
		measfctkwargs={"stampsize":config.stampsize, "gain":config.gain},
		ncpu=config.ncpu,
		skipdone=True
		)
	
	cat = megalut.meas.avg.onsims(
		measdir=simdir, 
		simparams=sp,
		task="group",
		groupcols=measfcts.default_groupcols, 
		removecols=measfcts.default_removecols
		)
	
	
	
	megalut.tools.table.keepunique(cat)
	megalut.tools.io.writepickle(cat, os.path.join(simdir, sp.name, "groupmeascat.pkl"))
	
	cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_g1", "tru_g2", "tru_g", "tru_flux", "tru_rad"])
	megalut.tools.table.keepunique(cat)
	megalut.tools.io.writepickle(cat, os.path.join(simdir, sp.name, "groupmeascat_cases.pkl"))
	
	len_valid_data = np.size(np.where((cat["snr"]).mask == False)[0])
	len_data = np.size(cat["snr"])
	
	print np.ma.mean(cat["snr"]), np.median(cat["snr"])
	
	res.append([zeropoint, np.ma.mean(cat["snr"]), np.ma.std(cat["snr"])/np.sqrt(1.0*len_valid_data)])
	
	if len_valid_data == 0:
		print 'No valid data, increasing zeropoint'
	
	zeropoint += 0.1

	if zeropoint > 25.8:
		match_snr = True
		
res = np.array(res)
megalut.tools.io.writepickle(res, os.path.join(config.workdir, "zeropoint_meas.pkl"))

plt.figure()
plt.errorbar(res[:,0], res[:,1], yerr=res[:,2])
plt.show()
