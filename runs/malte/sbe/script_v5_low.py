
#import matplotlib
#matplotlib.use("AGG")

import megalut.sbe
import mymeasfct
import mysimparams_v5 as mysimparams
import mymlparams_v5 as mymlparams
import myplots

import logging

#logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.INFO)


####### Configuration #######

run = megalut.sbe.run.Run(
	
	sbedatadir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_low_SN_v3",
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_low_SN_v3_workdir",
	
	ncpu = 4
	)


simparams = mysimparams.SBE_v5()
simparams.set_low_sn()

mlparams = mymlparams.trainparamslist


#shearsimparams = mysimparams.SBE_v3_shears()
#shearsimparams.name = "SBE_v3_shears_morerea"  # Warning, this is huge (and not necessary, it seems)
#shearsimparams.set_low_sn()
#shearsimparams.name = "SBE_v3_shears_morecase"
#shearmlparams = mymlparamsshear.trainparamslist


# Testing the v5 sims

"""
simparams.name = "quicktest"
run.drawsims(simparams, n=100, nc=50, ncat=6, nrea=1, stampsize=150)
run.meassims(simparams, mymeasfct.default, stampsize=150)
run.groupsimmeas(simparams, mymeasfct.default_groupcols, mymeasfct.default_removecols)
#myplots.measfails(run, simparams)
myplots.simobscompa(run, simparams, rea=1)
"""

#run.drawsims(simparams, n=50, nc=10, ncat=5000, nrea=1, stampsize=150) # An attempt with not that many galaxies per case. # DONE

#simparams.name = "SBE_v3_shears_morecase" # corresponds to run.drawsims(simparams, n=500, nc=10, ncat=5000, nrea=1, stampsize=150)
# but slow, 12 gigs of ram...


run.meassims(simparams, mymeasfct.default, stampsize=150)
run.groupsimmeas(simparams, mymeasfct.default_groupcols, mymeasfct.default_removecols)
run.prepcases(simparams, groupcolnames = ["tru_s1", "tru_s2", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"])




#run.traintenbilacshear(simparams, mlparams)






"""
#myplots.simobscompa(run, shapesimparams, rea=1)
# First, the shapes


#run.drawsims(shapesimparams, n=2500, nc=50, ncat=10, nrea=200, stampsize=150)
#run.meassims(shapesimparams, mymeasfct.default, stampsize=150)
#run.groupsimmeas(shapesimparams, mymeasfct.default_groupcols, mymeasfct.default_removecols)

#run.traintenbilac(shapesimparams, shapemlparams)

#run.selfpredict(shapesimparams, shapemlparams)
#myplots.shapesimbias(run, shapesimparams, rea=-10)
#myplots.shapesimbias2(run, shapesimparams, rea=-10)


# Now, the shears

#run.drawsims(shearsimparams, n=500, nc=10, ncat=1000, nrea=1, stampsize=150) # done
#run.drawsims(shearsimparams, n=5000, nc=25, ncat=500, nrea=1, stampsize=150) # this is "_morerea"
#run.drawsims(shearsimparams, n=500, nc=10, ncat=5000, nrea=1, stampsize=150) # this is "_morecase"



#run.meassims(shearsimparams, mymeasfct.default, stampsize=150)
#run.groupsimmeas(shearsimparams, mymeasfct.default_groupcols, mymeasfct.default_removecols)

# Those two guys are currently running with morecase... done

# Up to here its independent from the other sims. Now you have to predict the shapes before going on, using the other sims.
#run.othersimpredict(shearsimparams, shapesimparams, shapemlparams)


#run.inspect(shearsimparams)
#run.prepcases(shearsimparams, groupcolnames = ["tru_s1", "tru_s2", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"])

#run.traintenbilacshear(shearsimparams, shearmlparams)

#run.selfpredictshear(shearsimparams, shearmlparams)

#myplots.shearsimbias2(run, shearsimparams, rea=-10)



#run.inspectshear(shearsimparams, shearmlparams)





#run.predictsbe(shapesimparams, shapemlparams, shearsimparams, shearmlparams)
#run.analysepredsbe()



"""

"""

### v3.4 : reas differ only in orientation and noise.###
### v3.4: sims and training for the shear estimates ###
#shearsimparams = mysimparams.SBE_v4_1()
#shearsimparams.set_low_sn()
#shearmlparams = mymlparamsshear.trainparamslist
#run.drawsims(shearsimparams, n=1, nc=1, ncat=1000, nrea=1, stampsize=150)
#run.meassims(shearsimparams, mymeasfct.default, stampsize=150)
#run.groupsimmeas(shearsimparams, mymeasfct.default_groupcols, mymeasfct.default_removecols)
#run.prepcases(shearsimparams, groupcolnames=['tru_sigma', 'tru_flux', 'tru_s1', 'tru_s2', 'tru_psf_g1', 'tru_psf_g2', 'tru_psf_sigma']) # any should work, as these are random floats...
#run.traintenbilacshear(shearsimparams, shearmlparams)
#run.selfpredictshear(shearsimparams, shearmlparams)
#myplots3p4.shearsimbias(run, rea="full")







#shearsimparams.name = "SBE_v3_shears_morerea"

#shearmlparams = mymlparamsshear.trainparamslist

####### Steps to measure SBE


#run.makecats(onlyn=None, sbe_sample_scale=0.05)

#run.makecats(onlyn=1, sbe_sample_scale=0.05)

#run.measobs(mymeasfct.default, stampsize=150, skipdone=False) # The SBE stampsize of 200 seems exagerated!


#run.groupobs()
#run.showmeasobsfrac()

#run.plotmixobscheck()
#run.plotobscheck() # This ones saves one png per file... not needed.


######## Simulations and shape training:


#run.drawsims(shapesimparams, n=2500, nc=50, ncat=10, nrea=200, stampsize=150)
#run.meassims(shapesimparams, mymeasfct.default, stampsize=150)
#run.groupsimmeas(shapesimparams, mymeasfct.default_groupcols, mymeasfct.default_removecols)

#run.traintenbilac(shapesimparams, shapemlparams)

#run.selfpredict(shapesimparams, shapemlparams)
#myplots.shapesimbias(run, rea=-10)
#myplots.shapesimbias2(run, rea=-10)


######## Simulations and shear training:


#run.drawsims(shearsimparams, n=2500, nc=50, ncat=500, nrea=1, stampsize=150)  # Orignial try, with random psfs for each rea
#run.drawsims(shearsimparams, n=400, nc=10, ncat=10, nrea=1, stampsize=150) # -> test
#run.drawsims(shearsimparams, n=500, nc=10, ncat=1000, nrea=1, stampsize=150) # done


#run.drawsims(shearsimparams, n=5000, nc=25, ncat=500, nrea=1, stampsize=150) # this is "_morerea"



#run.meassims(shearsimparams, mymeasfct.default, stampsize=150)
#run.groupsimmeas(shearsimparams, mymeasfct.default_groupcols, mymeasfct.default_removecols)


# Up to here its independent from the other sims. Now you have to predict the shapes before going on, using the other sims.
#run.othersimpredict(shearsimparams, shapemlparams)


#run.inspect(shearsimparams)
#run.prepcases(shearsimparams, bincolnames = ["tru_s1", "tru_s2", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"])

#myplots.shearsimbias(run, shearsimparams, rea="full") # -> no_weights_bias # OK, now we predict the weights.

#run.traintenbilacshear(shearsimparams, shearmlparams)


#run.selfpredictshear(shearsimparams, shearmlparams)

#myplots.shearsimbias2(run, rea="full")
#myplots.shearsimbias2(run, rea=-10)


######## Predicting and anylysing sbe

#run.predictsbe(shapemlparams, shearmlparams)

#run.analysepredsbe()




#simparams.name = "SBE_v3_shears_varipsfcases"
#run.prepbatches(simparams, bincolnames = ["tru_s1", "tru_s2"])



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
"""
