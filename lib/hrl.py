### Imports ###

import numpy as np
import pygame as pg
import os
import csv


### HRL Class ###

class HRL:
    """
    HRL (High Resoultion Luminance) is a class which interfaces with a set of
    devices for assembling a psychophysics experiment. The sorts of devices are
    graphics devices for driving display, inputs for reading input from a
    subject, and photometers for calibration. For more information about these
    components, see the relevant help files.

    An optional aspect of HRLs functionality is the ability to automatically
    read design matrices, and print out result matrices.  While this
    functionality is little more than a reexportation of python's csv package,
    it can still simplify the code of many experiment scripts. These features
    can be activated with the appropriate hrl initializaiton arguments. When
    activated, the corresponding HRL instance has the fields 'designs' and
    'results' added to it. hrl.designs is an iterator over the lines of the
    design matrix and can be used for example in a for loop - 'for dsgn in
    hrl.designs:'.  hrl.results is a dictionary which is written to the result
    matrix file when hrl.writeResultLine() is called.
    """


    ## Core methods ##


    def __init__(self
                ,graphics='gpu'
                ,inputs='keyboard'
                ,photometer=None
                ,wdth=1024,hght=768,bg=0.0
                ,fs=False,db=True,scrn=0
                ,dfl=None,rfl=None,rhds=None
                ,lut=None):
        """
        Initialize an HRL object.

        Parameters
        ----------

        graphics : The graphics device to use. Available: 'gpu','datapixx',
            None. Default: 'gpu'
        inputs : The input device to use. Available: 'keyboard', 'responsepixx',
            None. Default: 'keyboard'
        photometer : The graphics device to use. Available: 'optical', 'minolta', None.
            Default: None
        wdth : The desired width of the screen. Default: 1024
        hght : The desired height of the screen. Default: 768
        bg : The background luminance on a scale from 0 to 1. Default: 0.0
        fs : Whether or not to run in Fullscreen.Default: False
        db : Whether or not to use double buffering. Default: True
        scrn: Which monitor to use. Numbered 0,1... Default: 0
        dfl : The read location of the design matrix. Default: None
        rfl : The write location of the result matrix. Default: None
        rhds : A list of the string names of the headers for the Result
            Matrix. The string names should be without spaces, e.g.
            'InputLuminance'. If rfl != None, rhds must be provided.
            Default: None
        lut : The lookup table. Default: None
        
        Returns
        -------
        hrl instance. Comes with a number of methods required to run an
        experiment.
        """

        ### Load Config ###
        #data_files=[(os.path.expanduser('~/.config'), ['misc/hrlrc'])]
        #cfg = cp.RawConfigParser()
        #cfg.read([os.path.expanduser('~/.config/hrlrc')])
        
        #######
        # 30.Aug 2020: this command is commented as it doesnt work in newer versions of linux
        # in newer versions, default screen numbering is ':1'
        # in older versions (including lab computer), it is  ':0.1'
        #os.environ['DISPLAY'] = ':0.' + str(scrn)
        #
        print ("OS display number (default): %s" % os.environ['DISPLAY'])
        
        if len(os.environ['DISPLAY'])>2:
            os.environ['DISPLAY'] = ':0.' + str(scrn)
        else: # legacy option for older configs
            os.environ['DISPLAY'] = ':' + str(scrn)
        
        print ("OS display number (now used): %s" % os.environ['DISPLAY'])

        #######
        
        ## Load Datapixx ##

        if (graphics == 'datapixx') or (inputs == 'responsepixx'):

            import datapixx as dpx

            # Open datapixx.
            self.datapixx = dpx.open()

            # set videomode: Concatenate Red and Green into a 16 bit luminance
            # channel.
            self.datapixx.setVidMode(dpx.DPREG_VID_CTRL_MODE_M16)

            # Demonstrate successful initialization.
            self.datapixx.blink(dpx.BWHITE | dpx.BBLUE | dpx.BGREEN
                        | dpx.BYELLOW | dpx.BRED)

        else:

            self.datapixx = None


        ## Load Graphics Device ##
        
        if graphics == 'gpu':

            from graphics.gpu import GPU
            self.graphics = GPU(wdth,hght,bg,fs,db,lut)

        elif graphics == 'datapixx':

            from graphics.datapixx import DATAPixx
            self.graphics = DATAPixx(wdth,hght,bg,fs,db,lut)

        else:

            self.graphics = None


        ## Load Input Device ##

        if inputs == 'keyboard':

            from inputs.keyboard import Keyboard
            self.inputs = Keyboard()

        elif inputs == 'responsepixx':

            from inputs.responsepixx import RESPONSEPixx
            self.inputs = RESPONSEPixx(self.datapixx)

        else:

            self.inputs = None


        ## Load Photometer ##

        if photometer == 'optical':

            from photometer.optical import OptiCAL
            self.photometer = OptiCAL('/dev/ttyUSB0')
        if photometer == 'minolta':

            from photometer.minolta import Minolta
            self.photometer = Minolta('/dev/ttyUSB0')

        else:

            self.photometer = None

      
        ## Results file ##
        self._rfl = None
        if rfl != None:
            # check if the file exists,,, if so then check how many trials have been made, 
            # then opens file in 'a' mode, and do not write the header
            if os.path.exists(rfl):
                # checks how many trials have been run
                r  = open(rfl,'rb')
                reader = csv.DictReader(r, delimiter=' ')
                l = list(reader)
                r.close()
                # length of list is the number of rows that has been written (without counting the header)
                self.starttrial = len(l) 
                
                
                self._rfl = open(rfl,'ab')
                self._rwtr = csv.DictWriter(self._rfl,rhds,delimiter=' ')
                
                
            # if it doesnt exist, open in 'wb' mode and write the header    
            else:
                self._rfl = open(rfl,'wb')
                self._rwtr = csv.DictWriter(self._rfl,rhds,delimiter=' ')
                self._rfl.write(' '.join(rhds) + '\r\n')  # writes header   
                self.starttrial = 0               

            # initalizing empty results dict (for trial-based saving)
            self.results = {}
    
        ## Design matrix file ##
        self._dfl = None
        if dfl != None:
            self._dfl = open(dfl,'rb')
            self.designs = csv.DictReader(self._dfl,delimiter=' ',skipinitialspace=True)
            # skip trials already done
            for i in range(self.starttrial):
                self.designs.next()
            
            

    def close(self):
        """
        Closes all the devices and systems maintained by the HRL object.
        This should be called at the end of the program.
        """
        if self.datapixx != None: self.datapixx.close()
        if self._rfl != None: self._rfl.close()
        if self._dfl != None: self._dfl.close()
        pg.quit()


    ## File methods ##


    def writeResultLine(self,dct=None):
        """
        Given an appropriate dicitonary of values, writes the line to
        the result file. The dictionary must include all the names given
        to the hrl instance when it was initialized. i.e. if the
        rhds=['Input','Output'] then dct must have elements dct['Input']
        and dct['Output'].

        By default, hrl uses the dictionary hrl.results, but the dictionary
        can be given directly if desired.

        Parameters
        ----------
        dct : The dictionary of results in the current trial.
        """
        if dct is None:
            self._rwtr.writerow(self.results)
        else:
            self._rwtr.writerow(dct)
