"""
Script/module to run on Nicolas' simulations
"""

import argparse
import astropy
import megalut
import megalut.learn
import galsim
import numpy as np
import os
import copy

#import config # No, doesn't use config!
import nicoconfig.measfcts as measfcts

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s',level=logging.INFO)


def define_parser():
	"""Defines the command line arguments
	"""
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--imgpath', required=True, help="Path to input FITS image")
	parser.add_argument('--incatpath', required=False, default=None, help="Path to input catalog")
	parser.add_argument('--outcatpath', required=True, help="Path to where the output catalog should be written")
	parser.add_argument('--workdir', required=True, help="Path to a working directory for intermediary files. Will be created if it doesn't exist yet.")
	parser.add_argument("--traindir", required=True, help="Path to the directory containing the training")
	
	parser.add_argument("-p", "--plots", help="Draw some check-plots into the workdir. Requires matplotlib.", action="store_true")
	parser.add_argument("--skipdone", help="Skips the measurement (slow) part, IF a measurement is already available in the given workdir", action="store_true")
	
	parser.add_argument('--stampsize', type=int, default=64, help='Size of stamps, in pixels')
	parser.add_argument('--nside', type=int, default=100, help='Size of stampgrid, in stamps')
	
	return parser
	

def readNico(catpath, onlybright=True):
	"""Read input catalog from Nicolas
	"""
	cat = astropy.io.ascii.read(catpath, names=["Nx1", "Ny1", "Nx2", "Ny2", "Nmag", "Nsersicn", "Nrad", "Nflux", "Ne1", "Ne2", "Na", "Nb", "Nc"])
	logger.info("Read {}, {} lines".format(catpath, len(cat)))
	
	if onlybright:
		bright = megalut.tools.table.Selector("bright", [("max", "Nmag", 24.5)])
		cat = bright.select(cat)
		if len(cat) != 10000:
			raise RuntimeError("Fishy!")
	
	# MegaLUT centering conventions
	cat["x"] = cat["Nx2"] + 0.5 # This is the center of the stamp.
	cat["y"] = cat["Ny2"] + 0.5
	
	# Adding "g" in addition to "e"
	cat["Ng1"] = cat["Ne1"] # temporary
	cat["Ng2"] = cat["Ne2"]
	for row in cat:
		s = galsim.Shear(e1=row["Ne1"], e2=row["Ne2"])
		row["Ng1"] = s.getG1()
		row["Ng2"] = s.getG2()
		
	return cat

def writeNico(cat, catpath, cols=None):
	"""Writes an output catalog in ASCII
	"""
	
	cat = copy.deepcopy(cat)
	
	if cols != None:
		cat.keep_columns(cols)
		
	astropy.io.ascii.write(cat, catpath)


def makeblankcat(stampsize, nside):
	"""Make a blank catalog with only x and y on a grid of nside-by-nside stamps, respecting MegaLUT centering conventions
	"""
	gals = []
	for i in range(nside):
		for j in range(nside):
			gals.append( [0.5 + stampsize/2.0 + i*stampsize, 0.5 + stampsize/2.0 + j*stampsize] )
	gals = np.array(gals)
	cat = astropy.table.Table([gals[:,0], gals[:,1]], names=('x', 'y'))
	logger.info("Made blank catalog of {} sources".format(len(cat)))
	return cat
	

def checkplot(cat, outpath):
	"""Saves a quick diagnostic check plot into the outpath
	"""
	import megalut.plot
	from megalut.tools.feature import Feature
	import matplotlib.pyplot as plt
	
	
	x = Feature("x")
	y = Feature("y")
	Nflux = Feature("Nflux")
	Nrad = Feature("Nrad")
	Nsersicn = Feature("Nsersicn")
	Nmag = Feature("Nmag")
	Ne1 = Feature("Ne1")
	Ne2 = Feature("Ne2")
	Ng1 = Feature("Ng1")
	Ng2 = Feature("Ng2")
	
	adamom_flux = Feature("adamom_flux")
	adamom_sigma = Feature("adamom_sigma")
	adamom_rho4 = Feature("adamom_rho4")
	adamom_g1 = Feature("adamom_g1")
	adamom_g2 = Feature("adamom_g2")
	snr = Feature("snr")
	
	pre_s1_adamom = Feature("pre_s1_adamom")
	pre_s2_adamom = Feature("pre_s2_adamom")
	pre_s1_fourier = Feature("pre_s1_fourier")
	pre_s2_fourier = Feature("pre_s2_fourier")
	

	cat["xerr"] = cat["adamom_x"] - cat["x"]
	cat["yerr"] = cat["adamom_y"] - cat["y"]
	xerr = Feature("xerr", -5, 5)
	yerr = Feature("yerr", -5, 5)


	fig = plt.figure(figsize=(17, 12))
	ax = fig.add_subplot(3, 3, 1)
	#megalut.plot.scatter.scatter(ax, cat, Nflux, adamom_flux, Nsersicn, showidline=True)
	megalut.plot.scatter.scatter(ax, cat, xerr, yerr, sidehists=True)
	
	
	ax = fig.add_subplot(3, 3, 2)
	megalut.plot.scatter.scatter(ax, cat, Nmag, snr, sidehists=True)

	ax = fig.add_subplot(3, 3, 3)
	megalut.plot.scatter.scatter(ax, cat, Ne1, adamom_g1, sidehists=True)
	
	ax = fig.add_subplot(3, 3, 4)
	megalut.plot.scatter.scatter(ax, cat, adamom_g1, pre_s1_adamom, sidehists=True)
	
	ax = fig.add_subplot(3, 3, 5)
	megalut.plot.scatter.scatter(ax, cat, Ng1, pre_s1_adamom, snr, showidline=True)
	
	ax = fig.add_subplot(3, 3, 6)
	megalut.plot.bin.res(ax, cat, Ng1, pre_s1_adamom, Nmag)
	
	ax = fig.add_subplot(3, 3, 7)
	megalut.plot.scatter.scatter(ax, cat, adamom_g2, pre_s2_adamom, sidehists=True)
	
	ax = fig.add_subplot(3, 3, 8)
	megalut.plot.scatter.scatter(ax, cat, Ng2, pre_s2_adamom, snr, showidline=True)
	
	ax = fig.add_subplot(3, 3, 9)
	megalut.plot.bin.res(ax, cat, Ng2, pre_s2_adamom, Nmag)
	
	
	plt.tight_layout()
	plt.savefig(outpath)
	plt.close(fig) # Helps releasing memory when calling in large loops.


	
def run(imgpath, incatpath, outcatpath, workdir, traindir, stampsize=60, nside=100, plots=False, skipdone=False):
	"""Top-level function to run measurement and predictions on one image (no multiprocessing inside).
	"""

	# We get an input catalog
	if incatpath != None:
		cat = readNico(incatpath)
	else:
		cat = makeblankcat(args.stampsize, args.nside)
	
	# We attach the image
	cat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
		filepath=imgpath,
		xname="x",
		yname="y",
		stampsize=stampsize,
		workdir=workdir
		)

	# Save the input catalog
	incatfilepath = os.path.join(workdir, "incat.pkl")
	meascatfilepath = os.path.join(workdir, "meascat.pkl")
	if not os.path.exists(workdir):
		os.makedirs(workdir)
	megalut.tools.io.writepickle(cat, incatfilepath)

	# And we run the measurements on a SINGLE cpu
	megalut.meas.run.general([incatfilepath], [meascatfilepath], measfcts.default, measfctkwargs={"stampsize":stampsize}, ncpu=1, skipdone=skipdone)

	# Perform the preditions: THIS PART IS HARD-CODED!
	scriptdir = os.path.split(os.path.realpath(__file__))[0] # The directory containing the present script
	confdir = os.path.join(scriptdir, "nicoconfig", "2017-01-24")
	
	conflist = [
		(os.path.join(confdir, "ada4g1.cfg"), os.path.join(traindir, "ada4g1_sum55")),
		(os.path.join(confdir, "ada4g2.cfg"), os.path.join(traindir, "ada4g2_sum55")),
		(os.path.join(confdir, "fh4g1.cfg"), os.path.join(traindir, "fh4g1_sum55")),
		(os.path.join(confdir, "fh4g2.cfg"), os.path.join(traindir, "fh4g2_sum55"))
	]

	cat = megalut.tools.io.readpickle(meascatfilepath)
	predcatfilepath = os.path.join(workdir, "predcat.pkl")
	cat = megalut.learn.tenbilacrun.predict(cat, conflist)
	megalut.tools.io.writepickle(cat, predcatfilepath)

	#print megalut.tools.table.info(cat)
	cat["pre_s1_adamom"] = cat["pre_g1_adamom"]
	cat["pre_s2_adamom"] = cat["pre_g2_adamom"]
	cat["pre_s1_fourier"] = cat["pre_g1_fourier"]
	cat["pre_s2_fourier"] = cat["pre_g2_fourier"]
	

	# Write the output in plain text
	if incatpath != None:
		colstowrite = ["Nx1", "Ny1", "Nx2", "Ny2", "pre_s1_adamom", "pre_s2_adamom", "pre_s1_fourier", "pre_s2_fourier"]
		#colstowrite = ["Nx1", "Ny1", "Nx2", "Ny2", "pre_s1_adamom", "pre_s2_adamom"]
		
	else:
		colstowrite = None
	writeNico(cat, outcatpath, colstowrite)
	
	# Close with a checkplot
	if plots:
		cat = megalut.tools.table.shuffle(cat)
		plotpath = os.path.join(workdir, "checkplot.png")
		checkplot(cat, plotpath)



def main(args):
	"""Executed when run as script
	"""
	
	logger.info("Running with args {}".format(args))
		
	run(args.imgpath, args.incatpath, args.outcatpath, args.workdir, args.traindir, stampsize=args.stampsize, nside=args.nside, plots=args.plots, skipdone=args.skipdone)
	
	return 0


if __name__ == '__main__':
	parser = define_parser()
	args = parser.parse_args()
	status = main(args)
	exit(status)
