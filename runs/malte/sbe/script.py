
#import matplotlib
#matplotlib.use("AGG")

import megalut.sbe
import mymeasfct
import mysimparams
import mymlparams
import myplots


import logging
#logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.INFO)


####### Configuration #######

run = megalut.sbe.run.Run(
	#sbedatadir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_high_SN",
	#workdir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_high_SN_workdir",
		
	sbedatadir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_low_SN",
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_low_SN_workdir",

	#sbedatadir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_low_SN_v2",
	#workdir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_low_SN_v2_workdir",

	#workdir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/test_low",
	
	ncpu = 10
	)


simparams = mysimparams.SBE_v1()
#simparams.set_high_sn() # This has only to be set when drawing simulations
simparams.set_low_sn()

#simparams.name = "SBE_tenbilac"
simparams.name = "SBE_tenbilac_1000"
#simparams.name = "SBE_tenbilac_test"


mlparams = mymlparams.trainparamslist



####### Steps #######


#run.makecats(onlyn=None, sbe_sample_scale=0.05)
#run.measobs(mymeasfct.default, stampsize=150, skipdone=False) # The SBE stampsize of 200 seems exagerated!


#run.groupobs()
#run.showmeasobsfrac()

#run.plotmixobscheck()
#run.plotobscheck() # This ones saves one png per file... not needed.


#run.drawsims(simparams, n=50, ncat=40, nrea=100, stampsize=150) # The big run, SBE_tenbilac

#run.drawsims(simparams, n=50, ncat=2, nrea=10, stampsize=150) # SBE_tenbilac_test

#run.drawsims(simparams, n=50, ncat=4, nrea=1000, stampsize=150) # SBE_tenbilac_1000

#run.meassims(simparams, mymeasfct.default, stampsize=150)


#myplots.simobscompa(run, simparams)




####run.avgsimmeas(simparams, mymeasfct.default_groupcols, mymeasfct.default_removecols)


#run.groupsimmeas(simparams, mymeasfct.default_groupcols, mymeasfct.default_removecols)


#run.train(simparams, mlparams)

#run.traintenbilac(simparams, mlparams)


#run.predictsims(simparams, mlparams)

### Test plots


name = "nh7mb5_msrb"

run.predictsims(simparams, mlparams)
myplots.predsims(run, filepath="predsims_{name}.png".format(name=name))
myplots.simbias(run, filepath="simbias_{name}.png".format(name=name))

run.predictobs(mlparams)
myplots.sbebias(run, filepath="sbebias_{name}.png".format(name=name))




#run.analysepredsims()

#run.fakepredictobs()

#run.analysepredobs()


#run.writepredsbe_single()

#myplots.simbias(run)  #, "bias_high_sn_sims.pdf")
#myplots.sbebias(run, "bias_low_sn_sbe.pdf")
#run.analysepredsims()
#run.writepredsbe()
