"""
This files holds a user-defined measfct.

It's a very good idea to keep this function in a separate module and not in your
script, so that it can be imported by the multiprocessing pool workers that will call,
it without causing any trouble!
"""

import megalut.meas
import megalut.meas.sewfunc


def demo_great3_measfct(catalog, branch=None):
	"""
	This function is made to demo the MegaLUT GREAT3 wrapper.
	
	Given that measurement functions might need adjustments depending on the branch,
	it seems useful to pass the branch object.
	"""	

	# We run SExtractor on the "img" stamps:
	catalog = megalut.meas.sewfunc.measfct(catalog, runon="img", sexpath="sex")
	
	# We run galsim_adamom :
	catalog = megalut.meas.galsim_adamom.measfct(catalog, stampsize=branch.stampsize(), measuresky=True)
		
	return catalog


