import matplotlib
matplotlib.use("AGG")

import os
import simparams
import measfcts
import f2n
import subprocess
import megalut

import logging

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s',level=logging.INFO)


genworkdir = "/vol/fohlen11/fohlen11_1/mtewes/casereafig/"

name = "shear"
#name = "ellip"


ncas = 5
nrea = 6
stampsize = 50



sp = simparams.Simple1()
sp.snc_type = nrea
sp.sr = 0.0

workdir = os.path.join(genworkdir, name)
if not os.path.isdir(workdir):
	os.makedirs(workdir)
fitsimgpath = os.path.join(workdir, "img.fits")
catpath = os.path.join(workdir, "cat.pkl")
writecatpath = os.path.join(workdir, "writecat.txt")



cat = megalut.sim.stampgrid.drawcat(sp, n=ncas, nc=1, stampsize=stampsize)
print cat

if name == "ellip":
	for i in range(ncas):
		for j in range(nrea):
			cat[i*ncas + j]["tru_g1"] = cat[i*ncas]["tru_g1"]
			cat[i*ncas + j]["tru_g2"] = cat[i*ncas]["tru_g2"]
			


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



