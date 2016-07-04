"""
Reusable sets of Machine Learning parameters
"""
import megalut.learn



# The usual features provided by adamom:

adamom_features = ["adamom_flux_mean", "skymad_mean", "adamom_g1_mean", "adamom_g2_mean", "adamom_sigma_mean", "adamom_rho4_mean"]
adamom_features_rea0 = ["adamom_flux_0", "skymad_0", "adamom_g1_0", "adamom_g2_0", "adamom_sigma_0", "adamom_rho4_0"]


# Standard MLParams based on these features

default_g = megalut.learn.MLParams(
	name="default_g",
	inputs=adamom_features,
	targets=["tru_g1","tru_g2"],
	predictions=["pre_g1","pre_g2"],
	)
default_rad = megalut.learn.MLParams(
	name="default_rad",
	inputs=adamom_features,
	targets=["tru_rad"],
	predictions=["pre_rad"],
	)
default_sersicn = megalut.learn.MLParams(
	name="default_sersicn",
	inputs=adamom_features,
	targets=["tru_sersicn"],
	predictions=["pre_sersicn"],
	)
default_flux = megalut.learn.MLParams(
	name="default_flux",
	inputs=adamom_features,
	targets=["tru_flux"],
	predictions=["pre_flux"],
	)


# Same but training on the first rea:
rea0_g = megalut.learn.MLParams(
	name="rea0_g",
	inputs=adamom_features_rea0,
	targets=["tru_g1","tru_g2"],
	predictions=["pre_g1","pre_g2"],
	)
rea0_rad = megalut.learn.MLParams(
	name="rea0_rad",
	inputs=adamom_features_rea0,
	targets=["tru_rad"],
	predictions=["pre_rad"],
	)
rea0_sersicn = megalut.learn.MLParams(
	name="rea0_sersicn",
	inputs=adamom_features_rea0,
	targets=["tru_sersicn"],
	predictions=["pre_sersicn"],
	)
rea0_flux = megalut.learn.MLParams(
	name="rea0_flux",
	inputs=adamom_features_rea0,
	targets=["tru_flux"],
	predictions=["pre_flux"],
	)



# Standard FANN neural net configurations
tripletwenty = megalut.learn.fannwrapper.FANNParams(name="tripletwenty", hidden_nodes=[20, 20, 20], max_iterations=10000)
doubletwenty = megalut.learn.fannwrapper.FANNParams(name="doubletwenty", hidden_nodes=[20, 20], max_iterations=1000)
doubleten = megalut.learn.fannwrapper.FANNParams(name="doubleten", hidden_nodes=[10, 10], max_iterations=1000)
simpleten = megalut.learn.fannwrapper.FANNParams(name="simpleten", hidden_nodes=[10], max_iterations=1000)


# And combinations of these settings
default_tripletwenty = [(default_g, tripletwenty), (default_rad, tripletwenty), (default_sersicn, tripletwenty), (default_flux, tripletwenty)]
default_doubletwenty = [(default_g, doubletwenty), (default_rad, doubletwenty), (default_sersicn, doubletwenty), (default_flux, doubletwenty)]
default_doubleten = [(default_g, doubleten), (default_rad, doubleten), (default_sersicn, doubleten), (default_flux, doubleten)]
default_simpleten = [(default_g, simpleten), (default_rad, simpleten), (default_sersicn, simpleten), (default_flux, simpleten)]

rea0_doubletwenty = [(rea0_g, doubletwenty), (rea0_rad, doubletwenty), (rea0_sersicn, doubletwenty), (rea0_flux, doubletwenty)]
