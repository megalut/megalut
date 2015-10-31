
#import matplotlib
#matplotlib.use("AGG")

import megalut.sbe
import mymeasfct
import mysimparams_v5 as mysimparams
import mymlparams_v5 as mymlparams
import myplots_v5 as myplots
import mysbeana_v5 as mysbeana

import logging


#logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.INFO)


####### Configuration #######

run = megalut.sbe.run.Run(
	
	sbedatadir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_high_SN_v3bis",
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_high_SN_v3bis_workdir",
	
	ncpu = 4
	)


#simparams = mysimparams.SBE_v5()
#simparams.set_high_sn()
#mlparams = mymlparams.trainparamslist


#run.makecats(onlyn=None, sbe_sample_scale=0.05)
#run.measobs(mymeasfct.default, stampsize=150, skipdone=True)
run.groupobs()
#run.showmeasobsfrac()
