
import megalut.learn

g1ada3 = megalut.learn.MLParams(name = "g1ada3",
	inputs = ["adamom_g1", "adamom_sigma", "adamom_rho4"],
	targets = ["tru_g1"],
	predictions = ["pre_g1_adamom"])

g2ada3 = megalut.learn.MLParams(name = "g2ada3",
	inputs = ["adamom_g2", "adamom_sigma", "adamom_rho4"],
	targets = ["tru_g2"],
	predictions = ["pre_g2_adamom"])


net = megalut.learn.tenbilacwrapper.TenbilacParams("Net")

trainparamslist = [
	(g1ada3, net),
	(g2ada3, net)
]

