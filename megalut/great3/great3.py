"""
Helper class for GREAT3 that does the trivial tasks for the user.

Todo list
---------
* make this inherit a generic run class

"""
import logging
logger = logging.getLogger(__name__)

import os
from astropy.table import Table
import numpy as np

import utils
import io
from .. import sim
from .. import tools
from .. import learn
from .. import meas

import shutil

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
        
        tools.dirs.mkdir(workdir)
        self.workdir=workdir
        
        # Now must create the sub-directories:
        for subfolder in ["obs","sim","ml","pred","out"]:
            tools.dirs.mkdir(self._get_path(subfolder))

        
    def meas(self, imgtype, measfct, measfctkwargs, method_prefix="", simparams="",overwrite=False,ncpu=1):
        """
        :param imgtype: Measure on observation or sim
        :type params: `obs` or `sim`
        :param measfct: method to use, it must be a user-defined function. The signature of the
            function must be function(img_fname,input_cat,stampsize)
        :param measfctkwargs: keyword arguments controlling the behavior of the measfct
        :type measfctkwargs: dict
        :param method_prefix: DEPRECATED
        :param overwrite: `True` all measurements and starts again, `False` (default)
            if exists, then perfect, skip it
        :param ncpu: Maximum number of processes that should be used. Default is 1.
            Set to 0 for maximum number of available CPUs.
        :type ncpu: int
        
        .. note:: This typically should be inherited somehow.
        """
        # Assert imgtype is known:
        assert imgtype in ["obs","sim"]

        img_fnames=[]
        incat_fnames=[]
        for subfield in self.subfields:
            if imgtype=="obs":
                img_fname=self.galimgfilepath(subfield)
                input_cat = io.readgalcat(self, subfield)
                
                # Prep the catalog
                incat_fname=self.galinfilepath(subfield,imgtype)  
                tools.io.writepickle(input_cat, incat_fname)
                
                img_fnames.append(img_fname)
                incat_fnames.append(incat_fname)
            elif imgtype=="sim":
                img_fname=self.simgalimgfilepath(subfield)
                #input_cat = self._get_path("sim","galaxy_catalog-%03i.fits" % subfield)
                #input_cat =  Table.read(input_cat)
            else: raise ValueError("Unknown image type")
            
            cat_fname=self.galfilepath(subfield,imgtype,method_prefix)  
            
            # figure out if we need to overwrite (if applicable)
            if os.path.exists(cat_fname):
                if overwrite: 
                    logger.info("Analysis of %s (subfield %d) prefix %s, I'm told to overwrite..."
                                 % (imgtype,subfield,method_prefix))
                    os.remove(cat_fname)
                else: 
                    logger.info("Analysis of %s (subfield %d) prefix %s already exists, skipping..."
                                 % (imgtype,subfield,method_prefix))
                    continue
            

        measdir=self._get_path(imgtype)

        # Making sure the stamp size is correct
        measfctkwargs["stampsize"]=self.stampsize()
            
        skipdone=not overwrite

        if imgtype=="obs":
            meas.run.general(img_fnames, incat_fnames, 
                             measdir, measfct, measfctkwargs,  
                             ncpu=ncpu, skipdone=skipdone)
        else:
            meas.run.onsims(self._get_path("sim"), simparams, measdir, 
                            measfct, measfctkwargs, ncpu, skipdone)
            
    def sim(self, simparams, n, overwrite=False, psf_selection=[4],ncat=1,nrea=1,ncpu=1):
        """
        Does the simulation
        
        :param simparams: an (overloaded if needed) megalut.sim.params.Params instance
        :param n: square root of the number of simulation
        :param overwrite: DEPREACTED / if `True` and the simulation exist they are deleted and simulated.
        :param psf_selection: Which PSF(s) to use in the catalogue ? Chosen from a random pick
            into a eligible PSF catalogue. Default: the center (ie 4th) PSF.
        :param ncat: The number of catalogs to be generated.
        :type ncat: int
        :param nrea: The number of realizations per catalog to be generated.
        :type nrea: int
        :param ncpu: Maximum number of processes that should be used. Default is 1.
            Set to 0 for maximum number of available CPUs.
        :type ncpu: int
        
        .. note: for an example of simparams have a look at demo/gret3/demo_CGV.py
        """
        
        for subfield in self.subfields:
            
            matched_psfcat=Table.read(self.starcatpath(subfield), format="ascii")
            
            cat_fname=self._get_path("sim","galaxy_catalog-%03i.fits" % subfield)
            img_fname=self.simgalimgfilepath(subfield)
            
            # figure out if we need to overwrite (if applicable)
            if os.path.exists(cat_fname) and os.path.exists(img_fname):
                if overwrite: 
                    logger.info("Sim of subfield %d, I'm told to overwrite..." % (subfield))
                    os.remove(cat_fname)
                else: 
                    logger.info("Sim of subfield %d already exists, skipping..." % (subfield))
                    continue
            elif os.path.exists(cat_fname):
                os.remove(cat_fname)
                logger.warning("catalog (subfield %d) only was found, removing it" % (subfield))
            elif os.path.exists(img_fname):
                os.remove(img_fname)
                logger.warning("image (subfield %d) only was found, removing it" % (subfield))
                
            psf_selection=np.random.choice(psf_selection,n*n)
            matched_psfcat = matched_psfcat[psf_selection]
            matched_psfcat.meta["stampsize"]=self.stampsize()
            
            psfimg=tools.image.loadimg(self.psfimgfilepath(subfield))
                
            drawcatkwargs = {"n":n, "stampsize":self.stampsize()}
            drawimgkwargs = {"psfcat":matched_psfcat,'psfimg':psfimg,
                             "psfxname":"col1", "psfyname":"col2"}

            sim.run.multi(self._get_path("sim"), simparams, drawcatkwargs, 
                          drawimgkwargs, ncat, nrea, ncpu)
            
    def learn(self, learnparams, mlparams, method_prefix="", overwrite=False):
        """
        A method that train any given algorithm.
        
        :param learnparams: an instance of megalut.learn.MLParams
        :param mlparams: an instance of megalut.learn.fannwrapper.FANNParams
        :param method_prefix: the prefix of the features
        :param overwrite: if `True` and the output ML file exist they are deleted and re-trained.
        
        
        Example usage::
        
            >>> learnparams = megalut.learn.MLParams(
                    name = "demo",
                    features = ["gs_g1", "gs_g2", "gs_flux"],
                    labels = ["tru_g1","tru_g2"],
                    predlabels = ["pre_g1","pre_g2"],
                    )
            
            >>> fannparams=megalut.learn.fannwrapper.FANNParams(
                    hidden_nodes = [20, 20],
                    max_iterations = 500,
                )
                
            >>> great3.learn(learnparams=learnparams, mlparams=fannparams, method_prefix="gs_")
        """
        # TODO: how to merge different measurements together ?
        for subfield in self.subfields:            
            ml = learn.ML(learnparams, mlparams,workbasedir=os.path.join(self.workdir
                                                                         ,"ml","%03d" % subfield))
                        
            ml_dir=ml.get_workdir()
            exists=True
            if not os.path.exists(os.path.join(ml_dir,"ML.pkl")) :
                exists=False

            if exists and not overwrite:
                logger.info("Learn of subfield %d already exists, skipping..." % (subfield))
                continue
            elif overwrite and exists:
                logger.info("Learn of subfield %d, I'm told to overwrite..." % (subfield))
                shutil.rmtree(ml_dir)

            input_cat=self.galfilepath(subfield,"sim",method_prefix)
            input_cat=Table.read(input_cat)
            
            # Important: we don't want to train on badly measured data!
            input_cat = input_cat[input_cat[method_prefix+"flag"] == 0] 

            ml.train(input_cat)
            
            # export the ML object:
            tools.io.writepickle(ml, os.path.join(ml_dir,"ML.pkl"))
            
    def predict(self,method_prefix,overwrite=False):
        """
        Predicts values according to the configuration of the ML pickles. 
        Predicts on all ML available.
        
        :param method_prefix: the prefix of the features
        :param overwrite: if `True` and the predictions exist they are deleted and re-predicted.
        """
        
        for subfield in self.subfields:    
            for root, dirs, files in os.walk(os.path.join(self.workdir,"ml","%03d" % subfield)):
                if not "ML.pkl" in files: continue
                ml_name = root.split("/")[-1]
                cat_fname=self._get_path("pred","%s-%03d.fits" % (ml_name,subfield))
                
                if os.path.exists(cat_fname) and overwrite:
                    logger.info("Pred of subfield %d, I'm told to overwrite..." % (subfield))
                    os.remove(cat_fname)
                elif os.path.exists(cat_fname):
                    logger.info("Pred of subfield %d already exists, skipping..." % (subfield))
                    continue
                
                logger.info("Using %s to predict on subfield %03d" % (ml_name,subfield))

                ml=tools.io.readpickle(os.path.join(root,"ML.pkl"))
                
                input_cat=self.galfilepath(subfield,"obs",method_prefix)
                input_cat=Table.read(input_cat)
                
                # We predict everything, we will remove flags later
                predicted=ml.predict(input_cat)
                
                failed=predicted[method_prefix+"flag"]>0
                count_failed=0
                for p in predicted[failed]:
                    # TODO: Better and faster way to do this ?
                    p["pre_g1"]=20.
                    p["pre_g2"]=20.
                    count_failed+=1
                    
                logger.info("Predicted on %d objects, %d failed" % (len(input_cat),count_failed))
                
                predicted.write(cat_fname,format="fits")
                
    def writeout(self, ml_name):
        """
        Write the shear catalog out
        
        :param ml_name: the name of the ML to use (from train & predict)
        """
        for subfield in self.subfields:  
            input_cat = Table.read(self._get_path("pred","%s-%03d.fits" % (ml_name,subfield)))
            
            input_cat=input_cat["ID","pre_g1","pre_g2"]
            input_cat.write(self._get_path("out","%03d.cat" % subfield),
                            format="ascii.commented_header")
            logger.info("Wrote shear cat for subfield %03d" % subfield)
            
    def presubmit(self, corr2path=".", use_weights=False):
        """
        :param corr2path: The directory containing the Michael Jarvis's corr2 code, 
                which can be downloaded from http://code.google.com/p/mjarvis/.
        :param use_weights: is the shear catalogue using weights?
        
        :requires: presubmission files in the megalut/great3/presubmission_script directory.
                Those files can be downloaded from https://github.com/barnabytprowe/great3-public.
        """
        presubdir = os.path.join(os.path.dirname(__file__), "presubmission_script")
        presubscriptpath = os.path.join(presubdir, "presubmission.py")
        catpath = self._get_path("out", "*.cat")
        branchcode = self.branchcode()
        corr2path = os.path.join(corr2path, 'corr2')
        outfilepath=self._get_path("out", "%s.cat" % branchcode)

        if use_weights:
            cmd = "python %s %s -b %s -w 3 -c2 %s -o %s" % (presubscriptpath, catpath, 
                                                                branchcode, corr2path, outfilepath)
        else:
            logger.info("I am NOT using weights !")
            cmd = "python %s %s -b %s -c2 %s -o %s" % (presubscriptpath, catpath, branchcode,
                                                            corr2path, outfilepath)
                
        os.system(cmd)

    def _get_path(self,*args):
        """
        A helper function that returns the filepath
        
        :param args: must be in order of the filepath, similar to os.path.join()
        
        Example usage::
        
            >>> self._get_path("obs","catalogue_000.fits")
            
        will return the filepath: self.workdir/obs/catalogue_000.fits
        """
        return os.path.join(self.workdir,"/".join(args))
