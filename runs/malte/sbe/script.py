
import matplotlib
matplotlib.use("AGG")

import megalut.sbe
import mymeasfct
import mysimparams
import mymlparams
import mymlparamsshear
import myplots
import mytests

import logging
#logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.INFO)


####### Configuration #######

run = megalut.sbe.run.Run(
	#sbedatadir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_high_SN",
	#workdir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_high_SN_workdir",
	#sbedatadir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_low_SN",
	#workdir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_low_SN_workdir",

	#sbedatadir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_low_SN_v2",
	#workdir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_low_SN_v2_workdir",
	
	sbedatadir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_low_SN_v3",
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_low_SN_v3_workdir",
	
	ncpu = 6
	)



####### Steps #######


#run.makecats(onlyn=None, sbe_sample_scale=0.05)

#run.makecats(onlyn=1, sbe_sample_scale=0.05)

#run.measobs(mymeasfct.default, stampsize=150, skipdone=False) # The SBE stampsize of 200 seems exagerated!


#run.groupobs()
#run.showmeasobsfrac()

#run.plotmixobscheck()
#run.plotobscheck() # This ones saves one png per file... not needed.


#######
"""
# Simulations for shape training:

simparams = mysimparams.SBE_v3_shapes()
simparams.set_low_sn()

#run.drawsims(simparams, n=2500, nc=50, ncat=10, nrea=200, stampsize=150)



run.meassims(simparams, mymeasfct.default, stampsize=150)
run.groupsimmeas(simparams, mymeasfct.default_groupcols, mymeasfct.default_removecols)


running up to here

#mlparams = mymlparamsshear.trainparamslist


"""


#######

# Simulations for shear training:

simparams = mysimparams.SBE_v3_shears()
simparams.set_low_sn()

run.drawsims(simparams, n=2500, nc=50, ncat=500, nrea=1, stampsize=150)
#run.drawsims(simparams, n=400, nc=10, ncat=10, nrea=1, stampsize=150) -> test

run.meassims(simparams, mymeasfct.default, stampsize=150)
run.groupsimmeas(simparams, mymeasfct.default_groupcols, mymeasfct.default_removecols)

#done, I am here

#mlparams = mymlparamsshear.trainparamslist










#run.drawsims(simparams, n=5000, nc=20, ncat=242, nrea=1, stampsize=150)

#run.drawsims(simparams, n=100, nc=10, ncat=20, nrea=1, stampsize=150)

#run.drawsims(simparams, n=1000, nc=10, ncat=500, nrea=1, stampsize=150)


#run.drawsims(simparams, n=50, ncat=4, nrea=1000, stampsize=150)

#run.meassims(simparams, mymeasfct.default, stampsize=150)

#run.groupsimmeas(simparams, mymeasfct.default_groupcols, mymeasfct.default_removecols)

#myplots.simobscompa(run, simparams, filepath="simobs.pdf")

#myplots.simobscompa(run, simparams, rea=-10)

#mytests.tru_s(run, simparams)

#run.prepbatches(simparams, bincolnames = ["tru_s1", "tru_s2"])



####run.avgsimmeas(simparams, mymeasfct.default_groupcols, mymeasfct.default_removecols)


#run.train(simparams, mlparams)

#run.traintenbilac(simparams, mlparams)

#run.traintenbilacshear(simparams, mlparams)


#run.predictsims(simparams, mlparams)

#run.analysepredsims()


#run.predictobs(mlparams)

#run.analysepredobs()

#run.writepredsbe()




#mytests.shearbias(run)

### Test plots


#name = "shear1"

#run.predictsims(simparams, mlparams)
#myplots.predsims(run, filepath="predsims_{name}.png".format(name=name), rea=-100)
#myplots.simbias(run, filepath="simbias_{name}.png".format(name=name), rea=-100)
#myplots.simbias(run, rea=-100)
#myplots.predsims(run, rea=-200)


#run.predictobs(mlparams)
#myplots.predsbe(run, filepath="predsbe_{name}.png".format(name=name))
#myplots.predsbe(run)


#mytests.newshearbias(run)
#mytests.groupshearbias(run, "groupshearbias.pdf")

#myplots.sbebias(run, filepath="sbebias_{name}.png".format(name=name))

#run.analysepredobs()



#run.analysepredsims()

#run.fakepredictobs()

#run.analysepredobs()


#run.writepredsbe_single()

#myplots.simbias(run)  #, "bias_high_sn_sims.pdf")
#myplots.sbebias(run, "bias_low_sn_sbe.pdf")
#run.analysepredsims()
#run.writepredsbe()
