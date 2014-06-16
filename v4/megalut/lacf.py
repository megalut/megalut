'''
@author: T. Kuntzer
'''

import utils
import numpy as np
import time

###################################################################################################
class Data(object):
    '''
    Class which manages the two images (the observation and its ACF). 
    For now only one method is available to compute the ACF from the data. (See ComputeACF() )
    This class is not to be used directly as it is inherited by ACF measurements methods!
    This feature may disappear in the future as a measurement method become proheminent.
    '''
    
    def __init__(self, image, verbose=True, show=True):
        ''' Polymorphic constructor takes 3 arguments (one is mandatory):
            
            @param image: (mandatory) Either the path to the image or a numpy array containing the data.
            @param verbose: (optional) if True prints a few information about the computations.
            @param show: (optional) allows the system to show images.
        '''
        if type(image)==str: self.data = utils.fromfits(image)
        else: self.data = np.asarray(image)
        self.show = show
        self.verbose = verbose
        self.ACF = None
        self.g1 = None
        self.g2 = None
        self.a = None
        self.b = None
        self.phi=None
                
    def SaveACF(self, fname, region=None):
        ''' Saves the ACF to a specifed filename. The region argument is a list/numpy vector of [rx, ry] 
            which precises the region (rectangular) of ACF to be saved around the centre. 

            @raise RuntimeError: Raise an exception if the ACF is not computed 
        '''
        if self.ACF == None: 
            raise RuntimeError('cannot save %s, ACF not computed!' % fname)
        else: 
            if region == None:
                x0 = y0 = 0
                xf, yf = np.shape(self.ACF)
                dx = xf
                dy=yf
            else:
                cx, cy = np.shape(self.ACF)
                cx /= 2
                cy /= 2
                dx, dy = region
                x0 = cx - dx/2
                y0 = cy - dy/2
                xf = cx + dx/2
                yf = cy + dy/2
            
            ACF = self.ACF[x0:xf,y0:yf]
            ACF[dx/2,dx/2]=0.
            ACF[dx/2,dx/2]=np.amax(ACF)
            utils.tofits(ACF, fname)
        if self.verbose: print 'Wrote ACF to %s' % fname
        
    def ComputeACF(self,weights=None, clip=False, **kwargs):
        ''' Computes the ACF from the data using FFT by the equation
            ACF = F^-1 ( F(weights.data).(F(weights.data))* )
            where F is the Fourier transform, F^-1 its inverse and * the complex conjugate, the operator . denotes multiplication
            
            This function takes two optional arguments:
            @param weigthts: can be None (no weighting of the data), "gaussian" (2D gaussian function 
            aligned to a first guess of the shape by SExtractor) or "tophat" same as gaussian, but once
            the shape is estimated, the Gaussian is replaced by a top-hat.
            @param clip: clip the data to [0, data_max]
        '''
        from numpy.fft import fft2, ifft2, fftshift   
        
        if weights == 'gaussian' or weights == 'acfgaussian' or weights == 'tophat':
            if self.verbose: t0 = time.time()
            if ('x_obj' in kwargs and 'y_obj' in kwargs and 'radius' in kwargs and 'a' in kwargs and 'b' in kwargs and 'theta' in kwargs):
                weights_params = [kwargs['x_obj'], kwargs['y_obj'], kwargs['radius'], kwargs['a'], kwargs['b'],kwargs['theta']]
                weights_params = np.array([weights_params])
            else:
                weights_params = None
            if self.verbose: print 'Weights params : \n', weights_params
            weights_map = self._BuildWeightMap(self.data, weights_type = weights, weights_params=weights_params)
            data=self.data*weights_map
            if self.verbose: print 'Needed to build weight map [s]', time.time()-t0
        else:
            data = self.data
            
        data = data+0.j
        if self.verbose: t0 = time.time()
        dataFT = fft2(data)
        self.ACF = fftshift(ifft2(dataFT * np.conjugate(dataFT))).real
        
        weights_map = self._BuildWeightMap(self.ACF, weights_type = weights, weights_params=weights_params)
        self.ACF=self.ACF*weights_map
        if clip:
            self.ACF = np.clip(self.ACF, 0., np.amax(self.ACF))
        
        if self.verbose: print 'Needed to compute ACF [s]', time.time()-t0
        
    def ShowACF(self, fname=None, title=None, zoom = 1):
        ''' Shows the image of the data and the ACF with the estimation of the ellipticity if already computed.
        
        @param fname: (optional) if a filename is specified, the graph is saved.
        @param title: (optional) Adds a title to the graph
        @param zoom: (optional) changes the size of the ellipse drawn on top of the ACF
        
        @raise RuntimeError: Raise an exception if the ACF is not computed 
        @requires: Pylab
        '''
        
        if self.ACF == None: 
            raise RuntimeError('cannot save %s, ACF not computed!' % fname)
        
        import pylab as plt

        plt.figure(figsize=(24, 12))
        
        plt.subplot(121)
        plt.imshow(self.data, origin='lower', interpolation='nearest',cmap=plt.cm.gray, vmin = np.amin(self.data)*0.999, vmax = np.amax(self.data)*1.001)
        plt.title('Data')
        
        ax=plt.subplot(122)
        plt.imshow(self.ACF,origin='lower', interpolation='nearest', vmin = np.amin(self.ACF)*0.999, vmax = np.amax(self.ACF)*1.001)
        if not (self.a == None and self.b == None and self.phi==None): 
            from matplotlib.patches import Ellipse
            cx, cy = np.shape(self.ACF)
            cx /= 2
            cy /= 2
            e=Ellipse(xy=[cx, cy], width=self.a*zoom, height=self.b*zoom, angle=self.phi/np.pi*180., facecolor='None',lw=2)
            ax.add_artist(e)
        plt.title('ACF')
        
        if not fname==None: plt.savefig(fname)
        plt.show()
        
    def ClearMeasures(self):
        ''' Resets all the ellipticity parameters to None '''
        self.g1 = None
        self.g2 = None
        self.a = None
        self.b = None
        self.phi = None

    def Set_data(self, a):
        ''' SET method for the data 
        @param a: numpy array of the data
        '''
        self.data=a
    
    def Set_ACF(self, a):
        ''' SET method for the ACF 
        @param a: numpy array of the ACF
        '''
        self.ACF=a
        
    def Get_ACF(self):
        ''' GET method for the ACF '''
        return self.ACF
        
    def Get_Shear(self):
        ''' Returns g1 and g2 estimates 
            @raise RuntimeError: if g1,g2 are not yet computed
        '''
        if self.g1 == None or self.g2== None: raise RuntimeError('g1/g2 not computed yet!')
        else: return self.g1, self.g2
        
    def Find_Obj(self, data):
        ''' Runs Sextractor on the specifed data.
        @param data: numpy array with data
        @return: Catalogue as generated by SExtractor and according the parameters below
        @requires: pysex
        @requires: SExtractor 
        '''
        import pysex
        params = ['XWIN_IMAGE', 'YWIN_IMAGE','FLUX_RADIUS','AWIN_IMAGE','BWIN_IMAGE','THETAWIN_IMAGE']
        config = {'DETECT_MINAREA':5, 'DETECT_THRESH':2., 'VERBOSE_TYPE':'QUIET'}
        cat = pysex.run(data, params=params, conf_args=config)

        return np.array(zip(cat[params[0]], cat[params[1]], cat[params[2]], cat[params[3]], cat[params[4]], cat[params[5]]))
    
    def _BuildWeightMap(self, data, weights_type,weights_params=None):
        ''' Creates the weights map for a given image according to a given weight type '''
        
        def gaussian(width_x, width_y, rotation):
            """Returns a gaussian function with the given parameters"""
            width_x = float(width_x)
            width_y = float(width_y)
 
            rotation = np.deg2rad(rotation)
 
            def rotgauss(x,y):
                xp = x * np.cos(rotation) - y * np.sin(rotation)
                yp = x * np.sin(rotation) + y * np.cos(rotation)
                g = np.exp(-((xp/width_x)**2+(yp/width_y)**2)/2.)
                return g
            return rotgauss
        
        def annulus(width):
            def ann(x,y):
                w = np.exp(-(x*x+y*y)/width/width+1.)* \
                np.exp(-width*width/(x*x+y*y)+1.)
                return w
            return ann
        
        def _create(weights,xf,yf,x_obj,y_obj, radius, ib, ia, iphi, weights_type):
            r = np.shape(self.data)[0]/2
           
            #if weights_type == 'acfgaussian':
            #   radius = self.save_radius
            #else:self.save_radius=radius
            #print weights_type, xf,yf,x_obj,y_obj, radius
            
            rx0 = int(x_obj)-r
            rxf = int(x_obj)+r
            ry0 = int(y_obj)-r
            ryf = int(y_obj)+r

            if rx0 < 0 : rx0=0
            if rxf >=xf: rxf=xf-1
            if ry0 < 0 : ry0=0
            if ryf >=xf: ryf=yf-1
            
            x = np.linspace(rx0,rxf-1,rxf-rx0)-x_obj
            y = np.linspace(ry0,ryf-1,ryf-ry0)-y_obj
            x,y = np.meshgrid(-x, y)
	    
	    

            if radius < 1e-9: 
                if self.verbose: pass
                print 'WARNING: object at %3.4f,%3.4f could not be treated. Ignoring...' % (x_obj, y_obj) 
            else:
                if weights_type == 'gaussian':
                    aa = gaussian(radius, ia/ib*radius, iphi)(x,y)
                elif weights_type == 'tophat':
                    aa[aa < 0.1] = 0.
                    aa[aa > 0] = 1.
                elif weights_type == 'annulus':   
                    aa = annulus(radius)(x,y)
                weights[ry0:ryf,rx0:rxf] += aa

            return 1
            
        try:
            if weights_params == None: cat = self.Find_Obj(data)
            else: cat = weights_params
            xf,yf=np.shape(data)

            x = np.linspace(0,xf-1,xf)#-x_obj
            y = np.linspace(0,yf-1,yf)#-y_obj
            x,y = np.meshgrid(x, y)
        
            weights = np.zeros_like(data)
            #np.asarray([_create(weights, xf,yf,x_obj,y_obj, radius, ia, ib, iphi, weights_type) for x_obj, y_obj, radius, ia, ib, iphi in cat])
            if weights_type == 'acfgaussian':
                np.asarray([_create(weights, xf,yf,xf/2+1,yf/2+1, radius, ia, ib, iphi, weights_type) for x_obj, y_obj, radius, ia, ib, iphi in cat])
            else:
                np.asarray([_create(weights, xf,yf,x_obj,y_obj, radius, 1, 1, 0., weights_type) for x_obj, y_obj, radius, ia, ib, iphi in cat])
            # Normalisation to 1
            weights /= np.sum(weights)

        except:
            weights = np.ones_like(data)
        return weights
# END OF CLASS
###################################################################################################


class QuadrupoleMoments(Data):
    ''' ACF measurement class
        Uses quadrupole moments to measure the ellipticity
        Example usage:
            img = QuadrupoleMoments(image_filename, verbose=False)
            img.ComputeACF(clip=True, weights='gaussian')
            img.Measure(region=region)
            g1os, g2os = img.Get_Shear()
    '''
    def __init__(self, image, verbose=True, show=True): 
        Data.__init__(self, image, verbose, show)
        if self.verbose: print '*** Using %s ***' % (self.__class__.__name__)
    
    def Measure(self, region=None):
        if self.ACF == None:
            if self.verbose: print 'Error: cannot measure ellipticity, ACF not computed!'
        
        cx, cy = np.shape(self.ACF)
        cx /= 2
        cy /= 2
        
        if region == None:
            x0 = y0 = 0
            xf, yf = np.shape(self.ACF)
        else:
            dx, dy = region
            x0 = cx - dx/2
            y0 = cy - dy/2
            xf = cx + dx/2
            yf = cy + dy/2
            
        ACF = self.ACF[x0:xf,y0:yf]
        self.ACF = ACF
        
        
        den = np.sum(ACF)
        x = np.arange(x0,xf)-cx
        y = np.arange(y0,yf)-cy
        x,y = np.meshgrid(x, y)
        
        Ixx = np.sum(ACF * x*x) / den
        Iyy = np.sum(ACF * y*y) / den
        Ixy = np.sum(ACF * x*y) / den
        
        xi = (Ixx - Iyy + 2.j*Ixy) / (Ixx+Iyy) / 2
        self.g1 = xi.real
        self.g2 = xi.imag
        '''
        elli = abs(xi)
        q = (1.+elli)/(1.-elli)
        self.a = min(np.abs(Ixx),np.abs(Iyy))
        self.b = self.a * q
        self.phi = np.arctan2(2.*Ixy,(Ixx - Iyy))/2.+np.pi/2.
        '''
# END OF CLASS
###################################################################################################
        
class WindowedMoments(Data):
    def __init__(self, image, verbose=True, show=True): 
        Data.__init__(self, image, verbose, show)
        if self.verbose: print '*** Using %s ***' % (self.__class__.__name__)
    
    '''def _get_half_radius(self, region=None):
        sky = np.median(self.ACF)
        ACF = self.ACF - sky
        flux = np.sum(ACF)
        #print 'total flux', flux
        cx, cy = np.shape(self.ACF)
        cx /= 2
        cy /= 2
        if region == None:
            x0 = y0 = 0
            xf, yf = np.shape(self.ACF)

        a = xf/2-x0/2
        b = yf/2-y0/2
        y,x = np.ogrid[-a:a, -b:b]
            
        for radius in range(1, np.shape(ACF)[0]):
            disk = x*x+y*y <= radius
            flux_aperture = np.sum(ACF[disk])
            #print 'flux in radius', radius, flux_aperture/flux
            if flux/2. <= flux_aperture: break
        return radius#/np.sqrt(8*np.log(2))
    '''
        
    def Measure(self, region=None, weights='acfgaussian'):
        #radius = self._get_half_radius()
        #if self.verbose: print 'The radius for the gaussian weight function is %d pixels' % radius
        cx = np.shape(self.ACF)[0] / 2
        cy = np.shape(self.ACF)[1] / 2
        if region == None:
            x0 = y0 = 0
            xf, yf = np.shape(self.ACF)
        else:
            dx, dy = region
            x0 = cx - dx/2
            y0 = cy - dy/2
            xf = cx + dx/2
            yf = cy + dy/2
            
        ACF = self.ACF[x0:xf,y0:yf]
        
        x = np.linspace(x0,xf,xf-x0,False)-cx
        y = np.linspace(y0,yf, yf-y0,False)-cy
        x,y = np.meshgrid(x, y)
        
        #weights = np.exp(-(x*x+y*y)/radius/radius/2*10000)
        if weights == None: weights = np.ones_like(ACF)
        else:weights = self._BuildWeightMap(ACF,weights_type=weights)
        den = np.sum(ACF*weights)
        
        Ixx = np.sum(ACF * x*x * weights) / den
        Iyy = np.sum(ACF * y*y * weights) / den
        Ixy = np.sum(ACF * x*y * weights) / den
        
        self.ACF = ACF*weights
        
        xi = (Ixx - Iyy + complex(0.,2.*Ixy)) / (Ixx+Iyy) / 2.
        self.g1 = xi.real
        self.g2 = xi.imag
        
        #elli = abs(xi/2)
        #q = (1.+elli)/(1.-elli)
        #self.a = radius
        #self.b = self.a * q
        #self.phi = np.arctan2(2.*Ixy,(Ixx - Iyy))/2.+np.pi/2.
    '''    
    def ShearCorrections(self,slope=None, intercept=None):
        '' 
        Linear correction of the measured shears according to what was given in input
        @param slope : numpy 2D vector of the slope for each g
        @param intercept : numpy 2D vector of the y0
        ''
        if slope == None:
            #slope = np.array([0.880976287992, 0.880773302041])
            slope = np.array([0.94572852109, 0.945258124765 ])
        if intercept == None:
            #intercept = np.array([-7.64943039698e-07,-1.48454046293e-06])
            intercept = np.array([3.66306870921e-07,-4.18173708392e-08])
        
        self.g1 = (self.g1-intercept[0])/slope[0]
        self.g2 = (self.g2-intercept[1])/slope[1]
    '''
# END OF CLASS
###################################################################################################

class EllipticityGradients(Data):
    ''' ACF measurement class
        Uses quadrupole moments to measure the ellipticity
        Example usage:
            img = QuadrupoleMoments(image_filename, verbose=False)
            img.ComputeACF(clip=True, weights='gaussian')
            img.Measure(region=region)
            g1os, g2os = img.Get_Shear()
    '''
    def __init__(self, image, verbose=True, show=True): 
        Data.__init__(self, image, verbose, show)
        if self.verbose: print '*** Using %s ***' % (self.__class__.__name__)
    
    def Measure(self):
        if self.ACF == None:
            if self.verbose: print 'Error: cannot measure ellipticity, ACF not computed!'
        
        dy,dx = np.gradient(self.ACF)
        delta = 0
        
        self.g1= -np.mean(dx*dx - dy*dy)/np.mean(dx*dx + dy*dy+delta)/2.
        self.g2= -np.mean(dx*dy)/np.mean(dx*dx + dy*dy+delta)#*2.
        
        
        