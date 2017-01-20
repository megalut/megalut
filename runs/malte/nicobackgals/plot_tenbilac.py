import tenbilac
import matplotlib.pyplot as plt




ten = tenbilac.com.Tenbilac("/users/mtewes/fohlen/backgals-megalut/train_Nico4nn/ada4g1_sum55/2017-01-20T09-11-57.cfg")
ten = tenbilac.com.Tenbilac("/users/mtewes/fohlen/backgals-megalut/train_Nico4nn/ada4g1_mult44free/2017-01-19T20-55-05.cfg")

ten._readmembers()


print ten.committee[0]

exit()

fig = plt.figure(figsize=(8, 6))
ax = plt.subplot(1, 1, 1)
	
#tenbilac.plot.summaryerrevo(ten.committee, ax=ax)
#tenbilac.plot.paramsevo(ax, ten.committee[0])
#tenbilac.plot.errevo(ax, ten.committee[0])


#plt.tight_layout()
plt.show()

