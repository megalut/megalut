


import megalut
import megalut.learn
import os
import numpy as np

import logging
loggerformat='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m'
#loggerformat='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s'
logging.basicConfig(format=loggerformat,level=logging.INFO)

workdir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/senstest"

#sampledir = os.path.join(workdir, "sample_data_2017-03-29") 
#sampleprods = os.path.join(sampledir, "prods")

obsdir = os.path.join(workdir, "sensitivity_testing_1/extracted") 
obsproddir = os.path.join(workdir, "megalut", "obs_1")

truedistdir = os.path.join(workdir, "true_distribs_2017-04-18") 
truedistpath = os.path.join(truedistdir, "table.pkl")

psfdir = os.path.join(workdir, "sensitivity_testing_1/psfs") 


simdir = os.path.join(workdir, "megalut", "sims")
simmeasdir = os.path.join(workdir, "megalut", "simmeas")
traindir = os.path.join(workdir, "megalut", "train")
valdir = os.path.join(workdir, "megalut", "val")

usecodes = True # If false, we use filesnames without any codes.
pcode = "pp0" # PSF
ecode = "ep0" # p(e)
scode = "sp0" # sky level
codestr = "{}_{}_{}".format(pcode, ecode, scode)
if usecodes:
	simdir = os.path.join(simdir, codestr)
	simmeasdir = os.path.join(simmeasdir, codestr)
	traindir = os.path.join(traindir, codestr)
	valdir = os.path.join(valdir, codestr)
	psfcatpath = os.path.join(psfdir, "psfcat_{}.pkl".format(pcode))
	
for code in [pcode, ecode, scode]: # Just a check agains typos
	assert code[1:] in ["m2", "m1", "p0", "p1", "p2"]

# Making dirs:
for d in [valdir, obsproddir]:
	if not os.path.exists(d):
		os.makedirs(d)

stampsize = 64
drawstampsize = stampsize # Used for drawing

imgnos = [0]


datasets = {
	
#	"train-shear":"ts-ln-1",
	"train-shear":"ts-ln-1-large", # <---- sim-ts
#	"train-shear":"ts-hn-1-large",
#	"train-shear":"ts-fn-1",
#	"train-shear":"ts-fn-1-failfrac05",
	
#	"valid-shear":"vs-1",
	"valid-shear":"vs-1-large",

#	"train-weight":"tw-1",
#	"train-weight":"tw-1-minmag22",
#	"train-weight":"tw-1-sheargroup4",
#	"train-weight":"tw-1-sheargroup4-large",
#
#	"train-weight":"tw-2-nsnc-small",
#	"train-weight":"tw-2-nsnc",
	"train-weight":"tw-2-nsnc-bigrea", # <---- sim-tw
#	"train-weight":"tw-3-nsnc",

#	"valid-overall":"val-1",
# 	"valid-overall":"tw-1-sheargroup4-large",
	"valid-overall":"vo-mimicdata-6",
	
	"simobscompa":"simobscompa",
}


shearconflist = [
	("mlconfig/ada4s1.cfg", "mlconfig/sum55.cfg"), # Uncomment a line to run on only one component
	("mlconfig/ada4s2.cfg", "mlconfig/sum55.cfg")
	
]

weightconflist = [
	#("mlconfig/ada2s1w.cfg", "mlconfig/sum55w_test3.cfg"),
	#("mlconfig/ada5s1w.cfg", "mlconfig/sum55w_test4.cfg"),
	
	#("mlconfig/ada5s1w.cfg", "mlconfig/sum55w_test3.cfg"),
	#("mlconfig/ada5s2w.cfg", "mlconfig/sum55w_test.cfg"),
	
	("mlconfig/ada5s1w.cfg", "mlconfig/sum55w_huge1.cfg"),#  <--- i guess we want those 
	("mlconfig/ada5s2w.cfg", "mlconfig/sum55w_huge1.cfg"),

	#("mlconfig/ada5s1w.cfg", "mlconfig/sum55w_tw3.cfg"),#  <--- i guess we want those 
	#("mlconfig/ada5s2w.cfg", "mlconfig/sum55w_tw3.cfg"),
	
	#("mlconfig/ada5s1w.cfg", "mlconfig/sum55w_huge1iden.cfg"),
	#("mlconfig/ada5s1w.cfg", "mlconfig/sum55w_huge1idennomb.cfg"),
	
]
