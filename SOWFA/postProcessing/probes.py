"""
Class for reading in 'probes' type OpenFOAM sampling

written by Eliot Quon (eliot.quon@nrel.gov)

"""
from __future__ import print_function
import os
import numpy as np
from datatools.SOWFA.postProcessing.reader import Reader

class Probe(Reader):
    """Stores a time array (t), and field arrays as attributes. The
    fields have shape:
        (Nt, N[, Nd])
    where N is the number of probes and Nt is the number of samples.
    Vectors have an additional dimension to denote vector components.
    Symmetric tensors have an additional dimension to denote tensor components (xx, xy, xz, yy, yz, zz).

    Sample usage:

        from SOWFA.postProcessing.probes import ProbeNew

        # read all probes
        probe = ProbeNew('postProcessing/probe1/')

        # read specified probes only
        probe = ProbeNew('postProcessing/probe1/',fields=['U','T'])

        probe.to_csv('probe1.csv')

    """
    def __init__(self,dpath=None,**kwargs):
        super().__init__(dpath,**kwargs)

    def _processdirs(self,
                     tdirList,
                     varList=['U','T'],
                     trimOverlap=True
                    ):
        #Redefine _processdirs so that default
        #argument for varList can be specified
        super()._processdirs(tdirList,varList,trimOverlap)

    def _read_data(self,dpath,fname):
        fpath = dpath + os.sep + fname
        with open(fpath) as f:
            try:
                self._read_probe_positions(f)
            except IOError:
                print('unable to read '+fpath)
            else:
                array = self._read_probe_data(f)
        return array


    def _read_probe_positions(self,f):
        self.pos = []
        line = f.readline()
        while '(' in line and ')' in line:
            line = line.strip()
            assert(line[0]=='#')
            assert(line[-1]==')')
            iprobe = int(line.split()[2])
            i = line.find('(')
            pt = [ float(val) for val in line[i+1:-1].split() ]
            self.pos.append( np.array(pt) )
            line = f.readline()
        if len(self._processed) > 0: # assert that all fields have same number of probes
            assert(self.N == len(self.pos))
        else: # first field: set number of probes in self.N
            self.N = len(self.pos)
            assert(self.N == iprobe+1)
        self.pos = np.array(self.pos)


    def _read_probe_data(self,f):
        line = f.readline()
        assert(line.split()[1] == 'Time')
        out = []
        for line in f:
            line = [ float(val) for val in
                    line.replace('(','').replace(')','').split() ]
            out.append(line)
        return np.array(out)


    #============================================================================
    #
    # DATA I/O
    #
    #============================================================================

    def to_pandas(self,itime=None,fields=None,dtype=None):
        self.hLevelsCell = self.pos[:,2]
        return super().to_pandas(itime,fields,dtype)

    def to_netcdf(self,fname):
        fieldDescriptions = {'T': 'Potential temperature',
                      'Ux': 'U velocity component',
                      'Uy': 'V velocity component',
                      'Uz': 'W velocity component',
                      }
        fieldUnits = {'T': 'K',
                 'Ux': 'm s-1',
                 'Uy': 'm s-1',
                 'Uz': 'm s-1',
                }
        self.hLevelsCell = self.pos[:,2]
        super().to_netcdf(fname,fieldDescriptions,fieldUnits)
