"""
Reusable sets of Machine Learning parameters
"""
import megalut.learn



# The usual features provided by adamom:

adamom_features = ["adamom_flux_mean", "adamom_skymad_mean", "adamom_g1_mean", "adamom_g2_mean", "adamom_sigma_mean", "adamom_rho4_mean"]
adamom_features_rea0 = ["adamom_flux_0", "adamom_skymad_0", "adamom_g1_0", "adamom_g2_0", "adamom_sigma_0", "adamom_rho4_0"]


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


# Same but training on the first rea:
rea0_g = megalut.learn.MLParams(
	name="rea0_g",
	features=adamom_features_rea0,
	labels=["tru_g1","tru_g2"],
	predlabels=["pre_g1","pre_g2"],
	)
rea0_rad = megalut.learn.MLParams(
	name="rea0_rad",
	features=adamom_features_rea0,
	labels=["tru_rad"],
	predlabels=["pre_rad"],
	)
rea0_sersicn = megalut.learn.MLParams(
	name="rea0_sersicn",
	features=adamom_features_rea0,
	labels=["tru_sersicn"],
	predlabels=["pre_sersicn"],
	)
rea0_flux = megalut.learn.MLParams(
	name="rea0_flux",
	features=adamom_features_rea0,
	labels=["tru_flux"],
	predlabels=["pre_flux"],
	)



# Standard FANN neural net configurations

doubletwenty = megalut.learn.fannwrapper.FANNParams(name="doubletwenty", hidden_nodes=[20, 20], max_iterations=1000)
doubleten = megalut.learn.fannwrapper.FANNParams(name="doubleten", hidden_nodes=[10, 10], max_iterations=1000)
simpleten = megalut.learn.fannwrapper.FANNParams(name="simpleten", hidden_nodes=[10], max_iterations=1000)


# And combinations of these settings

default_doubletwenty = [(default_g, doubletwenty), (default_rad, doubletwenty), (default_sersicn, doubletwenty), (default_flux, doubletwenty)]
default_doubleten = [(default_g, doubleten), (default_rad, doubleten), (default_sersicn, doubleten), (default_flux, doubleten)]
default_simpleten = [(default_g, simpleten), (default_rad, simpleten), (default_sersicn, simpleten), (default_flux, simpleten)]

rea0_doubletwenty = [(rea0_g, doubletwenty), (rea0_rad, doubletwenty), (rea0_sersicn, doubletwenty), (rea0_flux, doubletwenty)]
