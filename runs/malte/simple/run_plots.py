
execfile("config.py")
import plots

cat = megalut.tools.io.readpickle(os.path.join(workdir, "GauShear1", "selfprecat.pkl"))

for col in ["pre_s1", "pre_s2", "snr"]:
	megalut.tools.table.addstats(cat, col)
megalut.tools.table.addrmsd(cat, "pre_s1", "tru_s1")
megalut.tools.table.addrmsd(cat, "pre_s2", "tru_s2")

print megalut.tools.table.info(cat)

megalut.tools.io.writepickle(cat, os.path.join(workdir, "GauShear1", "selfprecat.pkl"))


#plots.shear_true(cat)

#plots.shear_mes(cat)
