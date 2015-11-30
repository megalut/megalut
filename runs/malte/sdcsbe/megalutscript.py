"""
Script to run MegaLUT on SBE data in a highly automated way, as one single step.
Designed for performance tests in SDCs (and not to assess measurement quality).

Run

	python megalutscript.py -h

...for help on how to use this.

Note that the code and the associated MegaLUT and Tenbilac packages are not public.
Malte Tewes, November 2015
"""

# Standard library imports
import logging
import argparse

# MegaLUT-specific imports

# On my (Malte) machines:
import megalut
import tenbilac
import megalutsbe

# The config



parser = argparse.ArgumentParser()
parser.add_argument("sbedatadir", help="path to the SBE data directory")
parser.add_argument("configdir", help="path to the config directory")
parser.add_argument("workdir", help="path to an empty directory where results and intermediate files can be stored")
parser.add_argument("--ncpu", help="number of cpus to use (default is 1)", type=int, default=1)
parser.add_argument("--onlyn", help="if set, it will run only on the 'onlyn' first files (default is to run on all)", type=int, default=None)

#parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
args = parser.parse_args()

# Setting up the logging:
logging.basicConfig(format='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s',level=logging.INFO)
#logging.basicConfig(filename='example.log',level=logging.INFO)

# We build a list of "workers" (i.e., jobs to be done, one per SBE image):
workers = megalutsbe.auto.buildworkers(args.sbedatadir, args.configdir, args.workdir, n=args.onlyn)

# And run those, usign a multiprocessign pool:
megalutsbe.auto.run(workers, ncpu=args.ncpu)

