"""
This is for the shear-training !

Do not forget:

normtargets = False
startidentity = False



"""


import megalut.learn



g1wmlparams = megalut.learn.MLParams(name = "g1w",
	inputs = ["adamom_sigma", "adamom_flux"],
	auxinputs = ["pre_g1"],
	targets = ["tru_s1"],
	predictions = ["pre_g1_w"])

g2wmlparams = megalut.learn.MLParams(name = "g2w",
	inputs = ["adamom_sigma", "adamom_flux"],
	auxinputs = ["pre_g2"],
	targets = ["tru_s2"],
	predictions = ["pre_g2_w"])


shear1 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "shear1", hidden_nodes = [7],
	errfctname="msbw", valfrac=0.25, shuffle=True,
	mbsize=50, mbloops=10, max_iterations=50, gtol=1e-15, startidentity=False, normtargets=False,
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=True, autoplot=True)



trainparamslist = [
	(g1wmlparams, shear1),
	(g2wmlparams, shear1)
]






# What was working ok in Leiden (v2):
"""

g1mlparams = megalut.learn.MLParams(name = "g1",
	features = ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	labels = ["tru_s1"],
	predlabels = ["pre_s1"])

g2mlparams = megalut.learn.MLParams(name = "g2",
	features = ["adamom_g2", "adamom_g1", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	labels = ["tru_s2"],
	predlabels = ["pre_s2"])






# Tenbilac settings:

shear1 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "shear1", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.25, shuffle=True,
	mbsize=50, mbloops=10, max_iterations=50, startidentity=True,
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=True, autoplot=True)

# hmm, fast convergence, then overfits. Trying a larger mbsize:

shear2 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "shear2", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.25, shuffle=True,
	mbsize=100, mbloops=10, max_iterations=50, startidentity=True,
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=True, autoplot=True)

"""


"""
# Taking over a previous shape training:
# Nope, did not work for some reason... maybe the very differnent normers ?
shear1to = megalut.learn.tenbilacwrapper.TenbilacParams(name = "shear1to", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.25, shuffle=True,
	mbsize=50, mbloops=5, max_iterations=50, startidentity=True,
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=True, autoplot=True)

shear1msb = megalut.learn.tenbilacwrapper.TenbilacParams(name = "shear1msb", hidden_nodes = [7],
	errfctname="msb", valfrac=0.25, shuffle=True,
	mbsize=50, mbloops=5, max_iterations=50, startidentity=True,
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=True, autoplot=True)
"""


