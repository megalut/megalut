"""
Script to run MegaLUT on SBE data in a highly "automated" way, as one single step.
Designed for performance tests in SDCs (and not to assess measurement quality).

See the README.txt for help.

Note that the code and the associated MegaLUT and Tenbilac packages are not public.
Malte Tewes, November 2015
"""

# Standard library imports
import logging
import argparse

# We add megalutpkgs to the path
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "megalutpkgs"))

# MegaLUT-specific imports
import megalutsbe

parser = argparse.ArgumentParser()
parser.add_argument("sbedatadir", help="path to the SBE data directory")
parser.add_argument("configdir", help="path to the config directory")
parser.add_argument("workdir", help="path to a directory where logs and intermediate files can be stored")
parser.add_argument("outdir", help="path to a directory where resulting FITS catalogs should be written, using the same structure as the sbedatadir")

parser.add_argument("--ncpu", help="number of cpus to use (default is 1)", type=int, default=1)
parser.add_argument("--onlyn", help="if specified, it will run only on the ONLYN first files (default is to run on all)", type=int, default=None)
parser.add_argument("--nolog", help="do not write log files", action="store_true")
args = parser.parse_args()

# Setting up the logging. For the default stream handler, we only want to see logs from megalutsbe.auto, to see progress.
logging.basicConfig(format='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s',level=logging.INFO)
toplogger = logging.getLogger()
toplogger.handlers[0].addFilter(logging.Filter(name='megalutsbe.auto'))

# We gather some settings related to the wrapper
settings = {
	"nolog":args.nolog,
	"sbestampsize":200, # if needed, make these command line arguments as well...
	"sbestampn":32,
	"sbesamplescale":0.05 
}

# We build a list of "workers" (i.e., jobs to be done, one per SBE image):
workers = megalutsbe.auto.buildworkers(args.sbedatadir, args.configdir, args.workdir, args.outdir, settings, n=args.onlyn)

# And run those, usign a multiprocessign pool:
megalutsbe.auto.run(workers, ncpu=args.ncpu)

