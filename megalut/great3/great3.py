"""
Helper class for GREAT3 that does the trivial tasks for the user.

.. todo::

 (most pressing at the top)

* make this inherit a generic run class

"""
import logging
logger = logging.getLogger(__name__)

import utils
import io
from .. import meas

class Run(object):
    
    def __init__(self, experiment, obstype, sheartype, datadir=None, workdir=None, subfields=range(200)):
        
        self.branch=utils.Branch(experiment, obstype, sheartype, datadir, workdir)
        self.subfields=subfields
        logger.info("Starting new GREAT3 branch %s-%s-%s" % (experiment, obstype, sheartype))
        
    def meas(self, imgtype, method=meas.galsim_adamom):
        """
        :param imgtype: Measure on observation or sim
        :type params: `obs` or `sim`
        :param method: method to use, it must be of the form megalut.meas.galsim_adamom
        
        .. note:: This typically should be inherited somehow.
        """
        
        for subfield in self.subfields:
            # First get the input cat
            input_cat = io.readgalcat(self.branch, subfield)
            
            