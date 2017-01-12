import os
import logging

logging.basicConfig(format='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s',level=logging.INFO)

workdir = "./ellpt"

stampsize = 48

ncpu = 6

simdir = os.path.join(workdir, "sim")
psfimgpath = os.path.join(workdir, "psf.fits")
psfcatpath = os.path.join(workdir, "psfcat.pkl")