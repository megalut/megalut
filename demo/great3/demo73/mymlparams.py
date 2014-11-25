"""
Reusable sets of Machine Learning parameters
"""
import megalut.learn


# A simple prediction of g1 and g2 based on adamom

simple_g = megalut.learn.MLParams(
	name = "simple_g",
	features = ["adamom_g1", "adamom_g2", "adamom_flux", "adamom_size"],
	labels = ["tru_g1","tru_g2"],
	predlabels = ["pre_g1","pre_g2"],
	)


# A multi-purpose FANN neural net configuration:

two_twenty = megalut.learn.fannwrapper.FANNParams(
	name = "two_twenty"
	hidden_nodes = [20, 20],
	max_iterations = 500,
	)
