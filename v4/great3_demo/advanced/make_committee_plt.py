import megalut
import numpy as np
import math

run = megalut.great3.run.Run(
	datadir = "/scratch/kuntzer/GREAT3_DATA/",
	workdir = "/scratch/kuntzer/v112/",
	branch = ["control", "ground", "variable"],
	version = "hn",
)

run.obssubfields = range(1)#range(0, 200, 20)
run.simsubfields = range(1)#range(0, 200, 20)

run.use_galsim = True
run.use_acf = True

run.nsimimages = 1

params = [(megalut.ml.MLParams(
	name = "g",
	features = ["mes_gs_g1", "mes_gs_g2","mes_acf_g1", "mes_acf_g2", "mes_gs_flux", "mes_gs_sigma", "mes_gs_rho4", "mes_rad30", "mes_rad50", "mes_rad70"],
	labels = ["tru_g1", "tru_g2"],
	predlabels = ["pre_g1", "pre_g2"],
	nb_committee = 10
), megalut.fannwrapper.FANNParams(
	nhid = [20, 20, 20],
	max_iterations = 3000
))]

run.committee_plots(params,mlplotparam={'g1':['fann','g',[-0.4,0.6], [-0.1,0.6]],'g2':['fann','g',None, None]},save=False)
# mlplotparam is a dictonary with :
# label of feature to plot : {megalut.ml.MLParams.toolname,megalut.ml.MLParams.name,range in x, range in y}
# note the range are not used for the stddev plot
