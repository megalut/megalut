"""
This is for the shear-training !

"""


import megalut.learn

# What to train:

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
	mbsize=50, mbloops=5, max_iterations=50, startidentity=True,
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=True, autoplot=True)


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


# Combining this:

"""
trainparamslist = [
	(g1mlparams, shear1)
]

trainparamslist = [
	(g2mlparams, shear1)
]
"""
"""
trainparamslist = [
	(g1mlparams, shear1msb)
]
"""
trainparamslist = [
	(g1mlparams, shear1),
	(g2mlparams, shear1)
]

