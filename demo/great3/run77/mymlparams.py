"""
Reusable sets of Machine Learning parameters
"""
import megalut.learn



# The usual features provided by adamom:

adamom_features = ["adamom_flux_mean", "adamom_skymad_mean", "adamom_g1_mean", "adamom_g2_mean", "adamom_sigma_mean", "adamom_rho4_mean"]


# Standard MLParams based on these features

default_g = megalut.learn.MLParams(
	name="default_g",
	features=adamom_features,
	labels=["tru_g1","tru_g2"],
	predlabels=["pre_g1","pre_g2"],
	)
default_rad = megalut.learn.MLParams(
	name="default_rad",
	features=adamom_features,
	labels=["tru_rad"],
	predlabels=["pre_rad"],
	)
default_sersicn = megalut.learn.MLParams(
	name="default_sersicn",
	features=adamom_features,
	labels=["tru_sersicn"],
	predlabels=["pre_sersicn"],
	)
default_flux = megalut.learn.MLParams(
	name="default_flux",
	features=adamom_features,
	labels=["tru_flux"],
	predlabels=["pre_flux"],
	)


# Standard FANN neural net configurations

doubletwenty = megalut.learn.fannwrapper.FANNParams(name="doubletwenty", hidden_nodes=[20, 20], max_iterations=1000)
doubleten = megalut.learn.fannwrapper.FANNParams(name="doubleten", hidden_nodes=[10, 10], max_iterations=1000)


# And combinations of these settings

default_doubletwenty = [(default_g, doubletwenty), (default_rad, doubletwenty), (default_sersicn, doubletwenty), (default_flux, doubletwenty)]
