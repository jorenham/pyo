from _core import *

######################################################################
### MIDI
######################################################################                                       
class Midictl(PyoObject):
    """
    Get the current value of a MIDI channel controller.
    
    Get the current value of a controller and optionally map it inside a specified range.
    
    Parameters:
    
    ctlnumber : int
        Midi channel. Available at initialization time only.
    minscale : float, optional
        Low range value for mapping. Available at initialization time only.
    maxscale : float, optional
        High range value for mapping. Available at initialization time only.
        
    Notes:
    
    The out() method is bypassed. Midictl's signal can not be sent to audio outs.

    """
    def __init__(self, ctlnumber, minscale=0, maxscale=1, mul=1, add=0):
        self._mul = mul
        self._add = add
        ctlnumber, minscale, maxscale, mul, add, lmax = convertArgsToLists(ctlnumber, minscale, maxscale, mul, add)
        self._base_objs = [Midictl_base(wrap(ctlnumber,i), wrap(minscale,i), wrap(maxscale,i), wrap(mul,i), wrap(add,i)) for i in range(lmax)]

    def out(self, chnl=0, inc=1):
        pass

    #def demo():
    #    execfile("demos/Midictl_demo.py")
    #demo = Call_example(demo)

    def args():
        return("Midictl(ctlnumber, minscale=0, maxscale=1, mul=1, add=0)")
    args = Print_args(args)

class Notein(PyoObject):
    """
    Generates MIDI notes messages.
    
    From a MIDI device, takes the notes in the range defined with `first` and `last` parameters,
    and outputs `poly` noteon - noteoff streams in the `scale` format (MIDI, hertz or transpo).
    
    Parameters:
    
    poly : int, optional
        Number of streams of polyphony generated. Defaults to 10.
    scale : int, optional
        Pitch output format. 0 = MIDI, 1 = Hertz, 2 = transpo. In the transpo mode, the central key
        (the key where there is no transposition) is (`first` + `last`) / 2.
    first : int, optional
        Lowest MIDI value. Defaults to 0.
    last : int, optional
        Highest MIDI value. Defaults to 127.
        
    Notes:
    
    Pitch and velocity are two separated set of streams. The user should call :
    
    Notein['pitch'] to retrieve pitch streams.
    Notein['velocity'] to retrieve velocity streams.    

    Velocity is automatically scaled between 0 and 1.
    
    The out() method is bypassed. Notein's signal can not be sent to audio outs.
    
    """
    def __init__(self, poly=10, scale=0, first=0, last=127, mul=1, add=0):
        self._pitch_dummy = None
        self._velocity_dummy = None
        self._poly = poly
        self._scale = scale
        self._first = first
        self._last = last
        self._mul = mul
        self._add = add
        mul, add, lmax = convertArgsToLists(mul, add)
        self._base_handler = MidiNote_base(self._poly, self._scale, self._first, self._last)
        self._base_objs = []
        for i in range(lmax * poly):
            self._base_objs.append(Notein_base(self._base_handler, i, 0, 1, 0))
            self._base_objs.append(Notein_base(self._base_handler, i, 1, wrap(mul,i), wrap(add,i)))

    def __del__(self):
        for obj in self._base_objs:
            obj.deleteStream()
            del obj
        self._base_handler.deleteStream()
        del self._base_handler

    def __getitem__(self, str):
        if str == 'pitch':
            if self._pitch_dummy == None:
                self._pitch_dummy = Dummy([self._base_objs[i*2] for i in range(self._poly)])
            return self._pitch_dummy
        if str == 'velocity':
            if self._velocity_dummy == None:
                self._velocity_dummy = Dummy([self._base_objs[i*2+1] for i in range(self._poly)])
            return self._velocity_dummy
                        
    def play(self):
        self._base_handler.play()
        self._base_objs = [obj.play() for obj in self._base_objs]
        return self

    def out(self, chnl=0, inc=1):
        return self
    
    def stop(self):
        self._base_handler.stop()
        [obj.stop() for obj in self._base_objs]

    #def demo():
    #    execfile("demos/Notein_demo.py")
    #demo = Call_example(demo)

    def args():
        return("Notein(poly=10, scale=0, first=0, last=127, mul=1, add=0)")
    args = Print_args(args)