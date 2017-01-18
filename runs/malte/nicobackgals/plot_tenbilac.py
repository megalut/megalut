import tenbilac
import matplotlib.pyplot as plt


ten = tenbilac.com.Tenbilac("/users/mtewes/fohlen/backgals-megalut/train_Nico4nn_g1ada5_mult55free/ML_Tenbilac_g1ada-4_MultNet/2017-01-17T11-03-11_MultNet.cfg")
ten._readmembers()

fig = plt.figure(figsize=(8, 6))
ax = plt.subplot(1, 1, 1)
	
#tenbilac.plot.summaryerrevo(ten.committee, ax=ax)
#tenbilac.plot.paramsevo(ax, ten.committee[0])
tenbilac.plot.errevo(ax, ten.committee[0])


#plt.tight_layout()
plt.show()

