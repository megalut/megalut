import megalut.utils as utils
import numpy as np
import pylab as plt
import figures
import pyfits

figures.set_fancy()
fig=plt.figure()
for i in range(200):
	print '%03d ----------------' % i
	obspickle = '../../v112/obs-control-space-variable-v4-comite/obs-%03i.pkl' % i
	fname = '/scratch/kuntzer/GREAT3_DATA/truth/control/space/variable/galaxy_catalog-%03d.fits' % i

	galaxies = utils.readpickle(obspickle)

	hdulist = pyfits.open(fname)
	table = hdulist[1].data
	IDs= np.asarray(hdulist[1].data['ID'])
	tg1 = np.asarray(hdulist[1].data['g1'])+np.asarray(hdulist[1].data['g1_intrinsic'])
	tg2 = np.asarray(hdulist[1].data['g2'])+np.asarray(hdulist[1].data['g2_intrinsic'])


	g1 = []
	g2 = []
	for g in galaxies:
		g1.append([g.mes_gs_g1,g.mes_g1, g.pre_g1])
		g2.append([g.mes_gs_g2,g.mes_g2, g.pre_g2])
	g1=np.asarray(g1)
	g2=np.asarray(g2)
	"""
	plt.figure()
	plt.plot(g1[:,0],g1[:,1],'.')
	plt.figure()
	plt.plot(g2[:,0],g2[:,1],'.')
	"""
	
	#plt.plot(g1[:,0]-tg1, g2[:,0]-tg2, 'kd')
	#plt.plot(g1[:,1]-tg1, g2[:,1]-tg2, 'bx')
	#plt.plot(g1[:,2]-tg1, g2[:,2]-tg2, 'r*')
	"""
	dg1=g1[:,0]-tg1
	dg2=g2[:,0]-tg2
	if i == 0:
		plt.errorbar(np.mean(dg1), np.mean(dg2), xerr=np.std(dg1), yerr=np.std(dg2),color='k',label='GalSim')
	else:
		plt.errorbar(np.mean(dg1), np.mean(dg2), xerr=np.std(dg1), yerr=np.std(dg2),color='k')
	print '%03d ----------------' % i
	print 'GalSim :', np.mean(dg1), '+/-', np.std(dg1), np.mean(dg2), '+/-', np.std(dg2)

	dg1=g1[:,1]-tg1
	dg2=g2[:,1]-tg2
	if i == 0:
		plt.errorbar(np.mean(dg1), np.mean(dg2), xerr=np.std(dg1), yerr=np.std(dg2),color='b',label='SExtractor')
	else:
		plt.errorbar(np.mean(dg1), np.mean(dg2), xerr=np.std(dg1), yerr=np.std(dg2),color='b')

	print 'Sex :', np.mean(dg1), '+/-', np.std(dg1), np.mean(dg2), '+/-', np.std(dg2)
	"""
	dg1=g1[:,2]-tg1
	dg2=g2[:,2]-tg2
	plt.plot(np.mean(dg1),np.mean(dg2),'r*')
"""
	if i == 0:
		plt.errorbar(np.mean(dg1), np.mean(dg2), xerr=np.std(dg1), yerr=np.std(dg2),color='r',label='MegaLUT')
	else:
		plt.errorbar(np.mean(dg1), np.mean(dg2), xerr=np.std(dg1), yerr=np.std(dg2),color='r')

	print 'MegaLUT :', np.mean(dg1), '+/-', np.std(dg1), np.mean(dg2), '+/-', np.std(dg2)

plt.legend(loc='best')
"""	

plt.xlabel(r'$\bar{g}_\mathrm{1,mes}-\bar{g}_\mathrm{1,true}$')
plt.ylabel(r'$\bar{g}_\mathrm{2,mes}-\bar{g}_\mathrm{2,true}$')

plt.grid()
figures.savefig('CSV_v4_comite_ML-only',fig,fancy=True)
plt.show()
