import matplotlib
matplotlib.use("AGG")

import os

import megalut.learn

import config

import logging
logger = logging.getLogger(__name__)

import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("snrcut", type=int, help="<S/N>-cut to apply to the training cases")
parser.add_argument("target", type=str, help="Target shear (s) or ellipticity (e)")
args = parser.parse_args()

logger.info("Recieved arguments snrcut:{} and target:{}".format(args.snrcut, args.target))
	

# Getting the path to the correct directories
measdir = os.path.join(config.simmeasdir, config.datasets["tp"])
traindir = os.path.join(config.traindir, config.datasets["tp"])
	
# And to the catalogue
traincatpath = os.path.join(measdir, "groupmeascat.pkl")
cat = megalut.tools.io.readpickle(traincatpath)
#print megalut.tools.table.info(cat)


if args.target is "e":
	cat["tru_s1"] = cat["tru_g1"]
	cat["tru_s2"] = cat["tru_g2"]
elif args.target is "s":
	pass
else:
	raise ValueError("Unknown type")


select=True
if select:
	logger.warning("Selection of cases is activated!")
	megalut.tools.table.addstats(cat, "snr")
	s = megalut.tools.table.Selector("snrcut", [
		#("max", "adamom_failfrac", 0.01),
		("min", "snr_mean", args.snrcut),
	])
	cat = s.select(cat)



# Running the training
dirnames = megalut.learn.tenbilacrun.train(cat, config.shearconflist, traindir)


