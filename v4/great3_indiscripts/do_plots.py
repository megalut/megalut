import megalut.utils as utils
import numpy as np
import pylab as plt
import figures
import os

figures.set_fancy()

fig=plt.figure()
ax = fig.add_subplot(111)
for i in range(200):
	obspickle = 'obs-control-ground-constant-v4_hn_gcircp7_mp/obs-%03i.pkl' % i
	truth = '/scratch/kuntzer/GREAT3_DATA/truth/control/ground/constant/shear_params-%03i.txt' % i

	galaxies = utils.readpickle(obspickle)
	true_shear = np.loadtxt(truth)

	g1 = []
	g2 = []
	for g in galaxies:
		g1.append([g.mes_gs_g1, g.mes_g1, g.pre_g1])
		g2.append([g.mes_gs_g2, g.mes_g2, g.pre_g2])
	g1=np.asarray(g1)
	g2=np.asarray(g2)

	print '%i -------------------' % i
	print 'GS', np.mean(g1[:,0]), np.mean(g2[:,0])
	print 'SE', np.mean(g1[:,1]), np.mean(g2[:,1])
	print 'ML', np.mean(g1[:,2]), np.mean(g2[:,2])
	print 'TR', true_shear



	if i==0:
		plt.plot(np.mean(g1[:,0])-true_shear[0], np.mean(g2[:,0])-true_shear[1], 'd', color='k',label='GalSim')
		plt.plot(np.mean(g1[:,1])-true_shear[0], np.mean(g2[:,1])-true_shear[1], 'x', color='b',label='SExtractor')
		plt.plot(np.mean(g1[:,2])-true_shear[0], np.mean(g2[:,2])-true_shear[1], '*', color='r',label='MegaLUT')
	else:
		plt.plot(np.mean(g1[:,0])-true_shear[0], np.mean(g2[:,0])-true_shear[1], 'd', color='k')
		plt.plot(np.mean(g1[:,1])-true_shear[0], np.mean(g2[:,1])-true_shear[1], 'x', color='b')
		plt.plot(np.mean(g1[:,2])-true_shear[0], np.mean(g2[:,2])-true_shear[1], '*', color='r')

	if np.abs(np.mean(g1[:,2])-true_shear[0])>0.01 or np.abs(np.mean(g2[:,2])-true_shear[1])>0.01:
		xx=np.mean(g1[:,2])-true_shear[0]
		yy=np.mean(g2[:,2])-true_shear[1]
		ax.annotate('%03d' % i, xy=(xx,yy),xytext=(xx+0.002,yy+0.001))
		print '!!!!!! Field %03d is horrible' % i

plt.grid()

plt.xlabel(r'$g_\mathrm{1,mes}-g_\mathrm{1,true}$')
plt.ylabel(r'$g_\mathrm{2,mes}-g_\mathrm{2,true}$')

plt.legend(loc='best')
figures.savefig('CGC_v4_hn_gcircp7_mp',fig,fancy=True)
plt.show()


