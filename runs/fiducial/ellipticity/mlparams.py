import megalut.learn


g1ada4 = megalut.learn.MLParams(name = "g1ada4",
	inputs = ["adamom_g1", "adamom_sigma", "adamom_flux", "adamom_rho4"],
	targets = ["tru_g1"],
	predictions = ["pre_g1_adamom"])

g1ada2 = megalut.learn.MLParams(name = "g1ada2",
	inputs = ["adamom_g1", "adamom_sigma"],
	targets = ["tru_g1"],
	predictions = ["pre_g1_adamom"])

net = megalut.learn.tenbilacwrapper.TenbilacParams("mlconfig/Net.cfg")

trainparamslist = [
	(g1ada2, net)
]