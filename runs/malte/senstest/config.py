


import megalut
import megalut.learn
import os
import numpy as np

import logging

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s',level=logging.INFO)

workdir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/senstest"

sampledir = os.path.join(workdir, "sample_data_2017-03-29") 
sampleprods = os.path.join(sampledir, "prods")


truedistdir = os.path.join(workdir, "true_distribs_2017-04-18") 
truedistpath = os.path.join(truedistdir, "table.pkl")

psfdir = os.path.join(workdir, "psf_2017-04-18") 
psfcatpath = os.path.join(psfdir, "psf.cat") 


simdir = os.path.join(workdir, "megalut", "sims")
simmeasdir = os.path.join(workdir, "megalut", "simmeas")


stampsize = 64
drawstampsize = stampsize # Used for drawing

imgnos = [0]


