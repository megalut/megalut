import megalut
import includes
import measfcts
import glob
import os
import numpy as np
import astropy

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt
import simparams

import logging
logger = logging.getLogger(__name__)

def find_nearest(array,value):
	''' Find nearest value is an array '''
	idx = (np.abs(array-value)).argmin()
	return idx

#--------------------------------------------------------------------------------------------------
# Parameters

# traindir
traindir = os.path.join(includes.workdir, "train_simple")

# If interested in s1:
#component = "1"
#main_pred = "s{}".format(component)
#main_feat = Feature("tru_{}".format(main_pred))
component = "1"
main_pred = "s{}".format(component)
main_feat = Feature("tru_{}".format(main_pred))

# Name of the simparam class
simparamname = "Ellipticity"

# Threshold for outlier biases (in per thousand)
mld_thr = 2

#--------------------------------------------------------------------------------------------------

incatfilepaths = sorted(glob.glob(os.path.join(includes.simvaldir, simparamname, "*_cat.pkl")))

build_dict = False
if build_dict:
	tru_s1_list = []

	for ifn in incatfilepaths:
		local_cat = megalut.tools.io.readpickle(ifn)
		tru_s1_list.append(local_cat["tru_s1"][0])
	tru_s1_list = np.array(tru_s1_list)

	globsimvaldir = megalut.meas.utils.simmeasdict(includes.simvaldir, simparams.Ellipticity())

	megalut.tools.io.writepickle([globsimvaldir, tru_s1_list], os.path.join(includes.simvaldir, simparamname, "dict_s1.pkl"))
else:
	globsimvaldir, tru_s1_list = megalut.tools.io.readpickle(os.path.join(includes.simvaldir, simparamname, "dict_s1.pkl"))

#--------------------------------------------------------------------------------------------------

outdirplots = os.path.join(traindir, "plots")
if not os.path.exists(outdirplots):
	os.mkdir(outdirplots)
valprecatpath = os.path.join(traindir, "valprecat.pkl")


cat = megalut.tools.io.readpickle(valprecatpath)
#simvalcat = megalut.tools.io.readpickle(os.path.join(includes.simvaldir, simparamname, "groupmeascat.pkl"))
#print simvalcat.meta#["img"].xname

print megalut.tools.table.info(cat)


cat["pre_g1"] = cat["pre_g1_adamom"]
#cat["pre_g1"] = cat["pre_g1_fourier"]

megalut.tools.table.addstats(cat, "pre_g1")
megalut.tools.table.addrmsd(cat, "pre_g1", "tru_s1")
megalut.tools.table.addstats(cat, "snr")


cat["adamom_frac"] = np.sum(cat["adamom_g1"].mask, axis=1)/float(cat["adamom_g1"].shape[1])

assert len(incatfilepaths) == len(cat)

mykwargs = {"histtype":"stepfilled", "bins":100, "alpha":0.5, "ec":"none", "color":"black"}
mykwargs2 = {"histtype":"stepfilled", "bins":100, "alpha":0.5, "ec":"none", "color":"red"}

count = 0
errs_rad = []
errs_flux = []
for did in range(len(cat)):#dirtyids:
	#print cat["pre_g{}_bias".format(component)][did], cat["tru_rad"][did], np.amin(cat["adamom_sigma"][did]), np.median(cat["adamom_sigma"][did]), np.amax(cat["adamom_sigma"][did]), cat["tru_flux"][did] , np.amin(cat["adamom_flux"][did]), np.median(cat["adamom_flux"][did]), np.amax(cat["adamom_flux"][did])

	if cat["adamom_frac"][did] > 0.005 or np.mean(cat["snr"][did]) <45:#>15:# < 45: 
		continue

	if np.abs(np.round(cat["pre_g1_bias"][did]*1e3,1)) < mld_thr: 
		continue

	ids1 = find_nearest(tru_s1_list, cat["tru_s1"][did])

	tfname = incatfilepaths[ids1]
	tfname = (tfname.split("/")[-1]).split("_cat.pkl")[0]

	meascatfname = os.path.join(includes.simvaldir, simparamname, "{}_0_galimg_meascat.pkl".format(tfname))
	local_cat = megalut.tools.io.readpickle(meascatfname)
	
	assert local_cat["tru_rad"][0] == cat["tru_rad"][did]
	assert local_cat["tru_flux"][0] == cat["tru_flux"][did]
	assert local_cat["tru_s1"][0] == cat["tru_s1"][did]
	assert local_cat["tru_s2"][0] == cat["tru_s2"][did]
	
	print tfname, np.amax(cat["adamom_flag"][did]), cat["adamom_frac"][did], np.amax(cat["skyflag"][did]), 
	print np.round(cat["pre_g1_bias"][did]*1e3,1), np.round(np.std(cat["adamom_flux"][did]), 3), np.round(np.std(cat["adamom_sigma"][did]), 3),
	print np.mean(cat["snr"][did]), cat["tru_g"][did], cat["tru_rad"][did], 

	if np.abs(np.round(cat["pre_g1_bias"][did]*1e3,1)) > mld_thr:
		print "!"
		count += 1
		errs_rad.append(cat["tru_rad"][did])
		errs_flux.append(cat["tru_flux"][did])
	else:
		print	

	"""
	continue
	fig = plt.figure(figsize=(12, 4))
	ax = fig.add_subplot(1, 3, 1)
	ax.hist(cat["adamom_flux"][did], **mykwargs)
	#ax.axvline(cat["tru_flux"][did], lw=2, c='k')

	ax = fig.add_subplot(1, 3, 2)
	ax.hist(cat["adamom_sigma"][did], **mykwargs)
	#ax.axvline(cat["tru_rad"][did] / np.pi * 2.35, lw=2, c='k')

	#dx = (((cat["adamom_x"][did] - 0.5) / (includes.stampsize / 2.) - 1.) % 2) * (includes.stampsize / 2.)
	dx = (cat["adamom_x"][did] - cat["x"][did])
	dy = (cat["adamom_y"][did] - cat["y"][did])

	ax = fig.add_subplot(1, 3, 3)
	cb = ax.scatter(dx, dy, c=cat["snr"][did])
	plt.colorbar(cb)
	ax.axvline(0, lw=2, c='k')
	ax.axhline(0, lw=2, c='k')

	plt.show()
	"""
print
print count, "<<< counts"
fig = plt.figure(figsize=(8, 4))
ax = fig.add_subplot(1, 2, 1)
histrange = (np.amin(cat["tru_rad"]), np.amax(cat["tru_rad"]))
ax.hist(cat["tru_rad"], range=histrange, **mykwargs)
ax.hist(errs_rad, range=histrange, **mykwargs2)
plt.xlabel("tru_rad")

ax = fig.add_subplot(1, 2, 2)
histrange = (np.amin(cat["tru_flux"]), np.amax(cat["tru_flux"]))
ax.hist(cat["tru_flux"], range=histrange, **mykwargs)
ax.hist(errs_flux, range=histrange, **mykwargs2)
plt.xlabel("tru_flux")
plt.show()

