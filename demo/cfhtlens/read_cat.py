import megalut
import megalut.cfhtlens

import logging
logging.basicConfig(level=logging.INFO)

"""
catfile = "/vol/fohlen11/fohlen11_1/hendrik/data/CFHTLenS/release_cats/W1m0m0_izrgu_release_mask.cat"

imgfile = "/vol/braid1/vol1/thomas/SHEARCOLLAB/Bonn/W1m0m0/i/coadd_V2.2A/W1m0m0_i.V2.2A.swarp.cut.fits"

field = "W1m0m0"

cat = megalut.cfhtlens.utils.readcat(catfile)
testcat = cat[:1000]
megalut.utils.writepickle(testcat, "testcat.pkl")
"""


cat = megalut.utils.readpickle("testcat.pkl")

megalut.cfhtlens.utils.removejunk(cat)




#megalut.utils.writepickle(cat, "after.pkl")

