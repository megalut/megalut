"""
Helper class for GREAT3 that does the trivial tasks for the user.

This is only for the branches for which the PSF is variable.

It is very much inspired by great3.py

"""
import logging
logger = logging.getLogger(__name__)

import os
from astropy.table import Table, hstack, vstack
from astropy.io import ascii
import numpy as np

import utils
import io
import var_psf_utils
from .. import sim
from .. import tools
from .. import learn
from .. import meas

import glob
import shutil
import copy

class Run(utils.Branch):
    
    def __init__(self, experiment, obstype, sheartype, datadir=None, workdir=None,\
                  subfields=range(200)):
        
        utils.Branch.__init__(self,experiment, obstype, sheartype, datadir, workdir)

        self._mkdir(workdir)
        self.subfields=subfields
        
        # This is because we have to treat each tile differently for full & variable psf
        self.simsubfields = subfields

        logger.info("Starting new *tiled* GREAT3 branch %s-%s-%s" % (experiment, obstype, sheartype))
        
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

        
    def meas(self, imgtype, measfct, measfctkwargs, method_prefix="", simparams="",
             groupcols=None, removecols=None,overwrite=False,ncpu=1):
        """
        :param imgtype: Measure on observation or sim
        :type params: `obs` or `sim`
        :param measfct: method to use, it must be a user-defined function. The signature of the
            function must be function(img_fname,input_cat,stampsize)
        :param measfctkwargs: keyword arguments controlling the behavior of the measfct
        :type measfctkwargs: dict
        :param method_prefix: *deprecated*
        :param overwrite: `True` all measurements and starts again, `False` (default)
            if exists, then perfect, skip it
        :param ncpu: Maximum number of processes that should be used. Default is 1.
            Set to 0 for maximum number of available CPUs.
        :type ncpu: int
        :param groupcols: Passed to :func:`megalut.meas.avg.onsims`, 
            if groupcols=None default = galsim features
        :param removecols: Passed to :func:`megalut.meas.avg.onsims`
        
        
        .. note:: This typically should be inherited somehow.
        """
        # Assert imgtype is known:
        assert imgtype in ["obs","sim"]

        img_fnames=[]
        incat_fnames=[]

        # Making sure the stamp size is correct
        measfctkwargs["stampsize"]=self.stampsize()
            
        skipdone=not overwrite
        if imgtype=="obs":
        
            for subfield in self.subfields:
                for xt in range(self.ntiles()):
                    for yt in range(self.ntiles()):
                        input_cat = io.readgalcat(self, subfield,xt,yt)
                
                        # Prep the catalog
                        incat_fname=self.galinfilepath(subfield,imgtype,xt,yt) 
                        tools.io.writepickle(input_cat, incat_fname)
                
                        img_fname=self.galimgfilepath(subfield,xt,yt)
                        img_fnames.append(img_fname)
                        incat_fnames.append(incat_fname)
                
            meas.run.general(img_fnames, incat_fnames, 
                             self._get_path(imgtype), measfct, measfctkwargs,  
                             ncpu=ncpu, skipdone=skipdone)
        elif imgtype=="sim":
            for simsubfield in self.simsubfields:
                for xt in range(self.ntiles()):
                    for yt in range(self.ntiles()):
                        img_fname=self.simgalimgfilepath(simsubfield,xt,yt)
                        simdir=self._get_path(imgtype,"%03d" % (simsubfield),"%02dx%02d" % (xt,yt))

                        meas.run.onsims(simdir, simparams, simdir, measfct, measfctkwargs, ncpu, skipdone)
                        
                        if groupcols==None:
                            groupcols = [
                            "adamom_flux", "adamom_x", "adamom_y", "adamom_g1", "adamom_g2",
                            "adamom_sigma", "adamom_rho4",
                            "adamom_skystd", "adamom_skymad", "adamom_skymean", "adamom_skymed", "adamom_flag"
                            ]
        
                        if removecols==None:
                            removecols=[]
                        
                        avgcat = meas.avg.onsims(simdir, simparams,
                                        groupcols=groupcols,removecols=removecols,removereas=True)
                        for simd in meas.utils.simmeasdict(simdir, simparams):
                            fname = '%s_avg_galimg_meascat.pkl' % simd
                            tools.dirs.mkdir(os.path.join(simdir,"meas",simparams.name))
                            fname=os.path.join(simdir,"meas",simparams.name,fname)
                            tools.io.writepickle(avgcat,fname)
        else: raise ValueError("Unknown image type")
        
            
    def sim(self, simparams, n, overwrite=False, psf_selection=None,ncat=1,nrea=1,ncpu=1):
        """
        Does the simulation
        
        :param simparams: an (overloaded if needed) megalut.sim.params.Params instance
        :param n: square root of the number of simulation
        :param overwrite: *deprecated* if `True` and the simulation exist they are deleted and simulated.
        :param psf_selection: Which PSF(s) to use in the catalogue ? Chosen from a random pick
            into a eligible PSF catalogue.
        :param ncat: The number of catalogs to be generated.
        :type ncat: int
        :param nrea: The number of realizations per catalog to be generated.
        :type nrea: int
        :param ncpu: Maximum number of processes that should be used. Default is 1.
            Set to 0 for maximum number of available CPUs.
        :type ncpu: int
        
        .. note: for an example of simparams have a look at demo/gret3/demo_CGV.py
        """

        for simsubfield in self.simsubfields:
            for xt in range(self.ntiles()):
                for yt in range(self.ntiles()):

                    matched_psfcat=Table.read(self.starcatpath(simsubfield,xt,yt), format="ascii")
            
                    cat_fname=self._get_path("sim","galaxy_catalog-%03i.fits" % simsubfield)
                    img_fname=self.simgalimgfilepath(simsubfield)
            
                    simdir=self._get_path("sim","%03d" % simsubfield,"%02dx%02d" % (xt,yt))
                    tools.dirs.mkdir(simdir)
            
                    # figure out if we need to overwrite (if applicable)
                    if os.path.exists(cat_fname) and os.path.exists(img_fname):
                        if overwrite: 
                            logger.info("Sim of subfield %d, I'm told to overwrite..." % (simsubfield))
                            os.remove(cat_fname)
                        else: 
                            logger.info("Sim of subfield %d already exists, skipping..." % (simsubfield))
                            continue
                    elif os.path.exists(cat_fname):
                        os.remove(cat_fname)
                        logger.warning("catalog (subfield %d) only was found, removing it" % (simsubfield))
                    elif os.path.exists(img_fname):
                        os.remove(img_fname)
                        logger.warning("image (subfield %d) only was found, removing it" % (simsubfield))
                    
                    psfimg=tools.image.loadimg(self.psfimgfilepath(simsubfield,xt,yt))
                    
                    if psf_selection==None:
                        psf_selected=np.arange(len(matched_psfcat))
                    else:
                        psf_selected=psf_selection
                    psf_selected=np.random.choice(psf_selected,n*n)


                    matched_psfcat = matched_psfcat[psf_selected]
                    matched_psfcat.meta["stampsize"]=self.stampsize()

                    fname=self.starcatpath(simsubfield,xt,yt,folder=simdir)
                    matched_psfcat.write(fname,format="ascii.commented_header")                    
                        
                    drawcatkwargs = {"n":n, "stampsize":self.stampsize()}
                    drawimgkwargs = {"psfcat":matched_psfcat,'psfimg':psfimg,
                                     "psfxname":"x", "psfyname":"y"}
                    matched_psfcat["x"]+=1
                    matched_psfcat["y"]+=1

                    sim.run.multi(simdir, simparams,
                                  drawcatkwargs, drawimgkwargs, ncat, nrea, ncpu)

    def learn(self, learnparams, mlparams, simparam_name,suffix="_mean",
               method_prefix="", psf_features=None, overwrite=False):
        """
        A method that train any given algorithm.
        
        :param learnparams: an instance of megalut.learn.MLParams
        :param mlparams: an instance of megalut.learn.fannwrapper.FANNParams
        :param suffix: what suffix of the measurements to take ? Default: "_mean". 
        :param psf_features: optional features that will be used to remove the variability of the PSF
        :param method_prefix: *deprecated* the prefix of the features
        :param simparam_name: the name of the simulation to use
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
        slp=copy.deepcopy(learnparams)
        slp.features = [feature + suffix for feature in slp.features]
        
        # The PSF features don't need suffix 
        if psf_features is not None:
            slp.features.extend(psf_features)
            
        for simsubfield in self.simsubfields:  
            for xt in range(self.ntiles()):
                for yt in range(self.ntiles()):
                    lp=copy.deepcopy(slp)
                    ml = learn.ML(lp, mlparams,workbasedir=os.path.join(self.workdir, \
                                            "ml","%03d" % simsubfield,"%02dx%02d" % (xt,yt)))
                                
                    ml_dir=ml.get_workdir()
                    exists=True
                    if not os.path.exists(os.path.join(ml_dir,"ML.pkl")) :
                        exists=False
        
                    if exists and not overwrite:
                        logger.info("Learn of simsubfield %d already exists, skipping..." % (simsubfield))
                        continue
                    elif overwrite and exists:
                        logger.info("Learn of simsubfield %d, I'm told to overwrite..." % (simsubfield))
                        shutil.rmtree(ml_dir)
        
                    # This is a quick fix, only working with one catalog!
                    seapat=self._get_path("sim","%03d" % simsubfield, "%02dx%02d" % (xt,yt),"meas",
                                          "%s" % simparam_name,"*_meascat.pkl")
                    cats = glob.glob(seapat)
                    if len(cats)==0:
                        raise ValueError("No catalog found for subfield %d" % simsubfield)
                    elif len(cats)>1:
                        raise NotImplemented("I'm not foreseen to be that smart, calm down")
                    input_cat = tools.io.readpickle(cats[0])
                    simdir=self._get_path("sim","%03d" % simsubfield, "%02dx%02d" % (xt,yt))
                    
                    if psf_features is not None:
                        fname=self.starcatpath(simsubfield,xt,yt,folder=simdir)
                        psf_cat=Table.read(fname,format="ascii.commented_header") 
                        relevant_psf = psf_cat[psf_features]
                        
                        """
                        if 'tile_x_pos_deg' in psf_features and 'tile_y_pos_deg' in psf_features:
                            # Normalize position
                            relevant_psf['tile_x_pos_deg']/=(10./self.ntiles())
                            relevant_psf['tile_y_pos_deg']/=(10./self.ntiles())
                        """
                        input_cat=hstack([input_cat, relevant_psf])
                    
                    # Important: we don't want to train on badly measured data!
                    #TODO: This line is bad, because method_prefix will disappear!
                    # If we take a suffix, this means we took out the badly measured data already
                    if suffix=="":
                        input_cat = input_cat[input_cat[method_prefix+"flag"] == 0] 
 
                    ml.train(input_cat)
                    
                    # Removes the suffix from the ml params as we observe only once, and thus no average
                    for i, f in enumerate(ml.mlparams.features):
                        if not suffix in f: continue
                        ml.mlparams.features[i] = f[:-1*len(suffix)]
                    
                    # export the ML object:
                    tools.io.writepickle(ml, os.path.join(ml_dir,"ML.pkl"))
            
    def predict(self,method_prefix="adamom_",overwrite=False):
        """
        Predicts values according to the configuration of the ML pickles. 
        Predicts on all ML available.
        
        :param method_prefix: *deprecated* the prefix of the features
        :param overwrite: if `True` and the predictions exist they are deleted and re-predicted.
        """

                    
        for subfield in self.subfields:   
            for xt in range(self.ntiles()):
                for yt in range(self.ntiles()):  
                    """if self.sheartype == "constant":
                        simsubfield = subfield
                    elif self.sheartype == "variable":
                        simsubfield = int(subfield/20)*20"""
                    fpath =  os.path.join(self.workdir,"ml","%03d" % subfield, "%02dx%02d" % (xt,yt))
                    for root, dirs, files in os.walk(fpath):
                        if not "ML.pkl" in files: 
                            logger.warning("Nothing found in %s" % fpath)
                            continue
                        ml_name = root.split("/")[-1]
                        
                        cat_fname=self._get_path("pred","%s-%03d-%02dx%02d.fits" % (ml_name,subfield,xt,yt))
                        if os.path.exists(cat_fname) and overwrite:
                            logger.info("Pred of subfield %d, I'm told to overwrite..." % (subfield))
                            os.remove(cat_fname)
                        elif os.path.exists(cat_fname):
                            logger.info("Pred of subfield %d already exists, skipping..." % (subfield))
                            continue
                        
                        logger.info("Using %s to predict on subfield %03d - %02dx%02d" % (ml_name,subfield,xt,yt))
        
                        ml=tools.io.readpickle(os.path.join(root,"ML.pkl"))
                        
                        input_cat=self.galfilepath(subfield,"obs",xt=xt,yt=yt)
                        input_cat=tools.io.readpickle(input_cat)
                        """
                        # Normalize position
                        input_cat['tile_x_pos_deg']/=(10./self.ntiles())
                        input_cat['tile_y_pos_deg']/=(10./self.ntiles())
                        """

                        # We predict everything, we will remove flags later
                        predicted=ml.predict(input_cat)

                        
                        #TODO: This line is bad, because method_prefix will disappear!
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
            for xt in range(self.ntiles()):
                for yt in range(self.ntiles()):
                    cat = Table.read(self._get_path("pred","%s-%03d-%02dx%02d.fits" % (ml_name,subfield,xt,yt))) 
                    if xt == 0 and yt == 0:
                        input_cat=cat["ID","pre_g1","pre_g2"]
                        var_psf_utils.generalise_catalogs(input_cat)
                    else:
                        var_psf_utils.generalise_catalogs(cat)
                        input_cat=vstack([input_cat, cat["ID","pre_g1","pre_g2"]])
                    
                    
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
