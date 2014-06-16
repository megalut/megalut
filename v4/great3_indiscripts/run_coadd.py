import coadd_multiepoch
import megalut
import os

run = megalut.great3.run.Run(
	datadir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3/",
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/MegaLUT_GREAT3/",
	branch = ["multiepoch", "space", "variable"],
	version = "v0.1"
)



sim_dir = run.branchdir()
work_dir = os.path.join(run.workdir, "obs-" + "-".join(run.branch) + "-coadd-" + run.version)

if run.branch[1] == "space":
	upsampling = 2
elif run.branch[1] == "ground":
	upsampling = 1
else:
	raise RuntimeError("Error")

if not os.path.isdir(work_dir):
	os.makedirs(work_dir)

for field in range(200):
#for field in range(1):
	
	print "Coadding field %i ..." % (field)
	for stars in [True, False]:
		coadd_multiepoch.main(
			field=field,
			sim_dir=sim_dir,
			work_dir = work_dir,
			upsampling = upsampling,
			stars = stars,
			n_split = 4,
			border = 4,
		)
