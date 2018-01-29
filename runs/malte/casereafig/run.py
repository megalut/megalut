import matplotlib
matplotlib.use("AGG")

import os
import simparams
import measfcts
import f2n
import subprocess
import megalut
import numpy as np

import logging

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s',level=logging.INFO)



#### Parameters ###################

genworkdir = "/vol/fohlen11/fohlen11_1/mtewes/casereafig/"

name = "shearw"
#name = "shear"
#name = "ellip"

ncas = 5
nrea = 6
stampsize = 50

####################################




if name in ["shear", "ellip"]:
	sp = simparams.Simple1()
	sp.snc_type = nrea
elif name in ["shearw"]:
	sp = simparams.Simple2()
	sp.snc_type = 0
sp.sr = 0.0

workdir = os.path.join(genworkdir, name)
if not os.path.isdir(workdir):
	os.makedirs(workdir)
fitsimgpath = os.path.join(workdir, "img.fits")
catpath = os.path.join(workdir, "cat.pkl")
writecatpath = os.path.join(workdir, "writecat.txt")

nc = 1
n = ncas

if name is "shearw":
 	# We no longer use SNC for training weights!
	# nc = int(float(nrea)/2.0)
	# n = nc * ncas
	nc = nrea
	n = nrea * ncas

cat = megalut.sim.stampgrid.drawcat(sp, n=n, nc=nc, stampsize=stampsize)

#exit()


if name == "ellip": # We give each rea the same ellipticity
	for i in range(ncas):
		g1 = cat[i*nrea]["tru_g1"]
		g2 = cat[i*nrea]["tru_g2"]
		print (g1, g2)
		for j in range(nrea):
			pass
			cat[i*nrea + j]["tru_g1"] = g1
			cat[i*nrea + j]["tru_g2"] = g2
			

if name == "shearw": # We give each case a different shear
	# No, in fact this looks weird. Better give zero or almost zero shear.
	for i in range(ncas):
		tru_s = 0.1
		tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)
		(tru_s1, tru_s2) = (tru_s * np.cos(2.0 * tru_theta), tru_s * np.sin(2.0 * tru_theta))
		for j in range(nrea):
			cat[i*nrea + j]["tru_s1"] = tru_s1
			cat[i*nrea + j]["tru_s2"] = tru_s2

print cat["tru_g", "tru_g1", "tru_g2"]
print megalut.tools.table.info(cat)
#exit()

megalut.sim.stampgrid.drawimg(cat, simgalimgfilepath=fitsimgpath, simtrugalimgfilepath=None, simpsfimgfilepath=None)
#subprocess.Popen("ds9 {}".format(fitsimgpath), shell=True)


cat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
	fitsimgpath,
	xname="x",
	yname="y",
	stampsize=stampsize,
	pixelscale=1.0
	)

cat = megalut.meas.galsim_adamom.measfct(cat, stampsize=stampsize, variant="wider")
cat = megalut.meas.skystats.measfct(cat, stampsize=stampsize)
cat = megalut.meas.snr.measfct(cat, gain=1.0)

if name == "shear" or name == "ellip":
	
	cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_flux"])
	megalut.tools.table.addstats(cat, "snr")
	megalut.tools.io.writepickle(cat, catpath)
	print megalut.tools.table.info(cat)
	writecat = cat["tru_flux", "snr_mean"]
	print writecat
	writecat.write(writecatpath, format="ascii")

if name == "shearw":
	
	
	megalut.tools.io.writepickle(cat, catpath)
	print megalut.tools.table.info(cat)
	writecat = cat["x", "y", "snr"]
	print writecat
	writecat.write(writecatpath, format="ascii")



for icas in range(ncas):

	myimage = f2n.fromfits(fitsimgpath)
	myimage.crop(0, stampsize*nrea, icas*stampsize, (icas+1)*stampsize)
	
	#myimage.setzscale(-0.1, 3)
	#myimage.makepilimage("log", negative = False)
	myimage.setzscale(-0.3, 1.0)
	myimage.makepilimage("lin", negative = False)
	
	
	myimage.upsample(5)
	pngimgpath = os.path.join(workdir, "case_{}.png".format(icas))
	myimage.tonet(pngimgpath)

	subprocess.Popen("display {}".format(pngimgpath), shell=True)



