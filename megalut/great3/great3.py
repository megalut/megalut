"""
Helper class for GREAT3 that does the trivial tasks for the user.

.. todo::

 (most pressing at the top)

* make this inherit a generic run class

"""
import logging
logger = logging.getLogger(__name__)

import os

import utils
import io
from .. import meas
from .. import gsutils
from .. import utils as mutils

class Run(utils.Branch):
    
    def __init__(self, experiment, obstype, sheartype, datadir=None, workdir=None,\
                  subfields=range(200)):
        
        utils.Branch.__init__(self,experiment, obstype, sheartype, datadir, workdir)

        self._mkdir(workdir)
        self.subfields=subfields
        logger.info("Starting new GREAT3 branch %s-%s-%s" % (experiment, obstype, sheartype))
        
    def _mkdir(self, workdir):
        """
        Creates the working directories. Outputs a warning if the directories already exist
        
         .. note:: This typically should be inherited somehow.
        """

        if workdir==None: workdir="./%s" % (self.get_branchacronym()) 
        
        mutils.mkdir(workdir)
            
        # Now must create the sub-directories:
        for subfolder in ["obs","sim","ml","pred","out"]:
            mutils.mkdir(os.path.join(workdir,subfolder))
            
        self.workdir=workdir
        
    def meas(self, imgtype, method=meas.galsim_adamom):
        """
        :param imgtype: Measure on observation or sim
        :type params: `obs` or `sim`
        :param method: method to use, it must be of the form megalut.meas.galsim_adamom
        
        .. note:: This typically should be inherited somehow.
        """

        for subfield in self.subfields:
            if imgtype=="obs":
                img_fname=self.galimgfilepath(subfield)
            elif imgtype=="sim":
                pass                                
            else: raise ValueError("Unknown image type")
            
            # First get the input cat
            input_cat = io.readgalcat(self,subfield)
            
            # See issue #28 about this:
            if method==meas.galsim_adamom:
                img = gsutils.loadimg(img_fname)
                meas_cat = meas.galsim_adamom.measure(img, input_cat, \
                                                      stampsize=self.stampsize())
            else: # TODO: implement here
                raise NotImplemented()
            
            # Save the meas cat
            cat_fname=self.galfilepath(subfield,imgtype)
            meas_cat.write(cat_fname,format="fits")
            
            
            exit()            