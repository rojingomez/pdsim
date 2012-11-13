
#Other imports in _flow.pxd
import copy
import cPickle
from flow_models import PyFlowFunctionWrapper

from CoolProp.State import State as StateClass
from CoolProp.State cimport State as StateClass

from PDSim.core._containers import TubeCollection
from PDSim.core._containers cimport TubeCollection

from libc.stdlib cimport malloc, free, calloc

import cython

cpdef tuple sumterms_given_CV(bytes key, list Flows):
    """
    A function to sum all the mdot terms for a given control volume
    
    Searches the list of flows and for each element in the flows, checks whether
    the key matches one of upstream or downstream key
    
    Parameters
    ----------
    key: string
    Flows: FlowPathCollection instance 
    """
    cdef FlowPath Flow
    cdef double summer_mdot = 0.0, summer_mdoth = 0.0
    
    for Flow in Flows:

        if not Flow.exists or abs(Flow.mdot)<1e-12:
            continue
                
        if Flow.key_down == key:
            summer_mdot+=Flow.mdot
            summer_mdoth+=Flow.mdot*Flow.h_up
        
        elif Flow.key_up == key:
            summer_mdot-=Flow.mdot
            summer_mdoth-=Flow.mdot*Flow.h_up
            
        else:
            continue
        
    return summer_mdot, summer_mdoth

class struct(object):
    def __init__(self,d):
        self.__dict__.update(d)
 
@cython.final
cdef class FlowPathCollection(list):
    
    cpdef update_existence(self, Core):
        """
        A function to update the pointers for the flow path as well as check existence
        of the states on either end of the path
        
        This is required whenever the existence of any of the CV or tubes 
        changes.  Calling this function will update the pointers to the states
        
        Parameters
        ----------
        Core : PDSimCore instance or derived class thereof
        
        """
        cdef FlowPath FP
        cdef dict Tube_Nodes = Core.Tubes.get_Nodes()
        cdef list exists_keys = Core.CVs.exists_keys
        cdef list flow_paths = self
        
        for FP in flow_paths:
            ## Update the pointers to the states for the ends of the flow path
            if FP.key1 in exists_keys:
                CV = Core.CVs[FP.key1]
                FP.State1=CV.State
                FP.key1_exists = True
                FP.ikey1 = exists_keys.index(FP.key1)
            elif FP.key1 in Tube_Nodes:
                FP.State1 = Tube_Nodes[FP.key1]
                FP.key1_exists = False
                if Core.Tubes[FP.key1].key1 == FP.key1:
                    FP.ikey1 = Core.Tubes[FP.key1].i1
                else:
                    FP.ikey1 = Core.Tubes[FP.key1].i2
            else:
                FP.exists=False
                FP.key1_exists = False
                FP.mdot = 0.0
                #Doesn't exist, go to next flow
                continue
            
            if FP.key2 in exists_keys:
                CV = Core.CVs[FP.key2]
                FP.State2=CV.State
                FP.key2_exists = True
                FP.ikey2 = exists_keys.index(FP.key2)
            elif FP.key2 in Tube_Nodes:
                FP.State2=Tube_Nodes[FP.key2]
                FP.key2_exists = False
                if Core.Tubes[FP.key2].key1 == FP.key2:
                    FP.ikey2 = Core.Tubes[FP.key2].i1
                else:
                    FP.ikey2 = Core.Tubes[FP.key2].i2
            else:
                FP.exists=False
                FP.key2_exists = False
                FP.mdot = 0.0
                #Doesn't exist, go to next flow
                continue
            
            #Made it this far, so both states exist
            FP.exists = True
    
    cpdef calculate(self, arraym harray):
        """
        Run the code for each flow path to calculate the flow rates
        
        Parameters
        ----------
        harray : arraym, optional
            Arraym that maps index to enthalpy - CVs+Tubes
        """
        cdef FlowPath FP
        cdef list flow_paths = self
                
        for FP in flow_paths:
            if FP.exists:
                FP.calculate(harray)
        
    @property
    def N(self):
        return self.__len__()
        
    @cython.cdivision(True)
    cpdef tuple sumterms(self, Core):
        """
        Sum all the mass flow and mdot*h for each CV in existence at a given 
        step for the derivatives in the ODE solver
        
        Meant to be called by PDSimCore.derivs()
        
        Parameters
        ----------
        Core: PDSimCore instance
            
        """
        cdef list exists_keys = Core.CVs.exists_keys
        cdef double omega = Core.omega
        cdef arraym summerdm_array, summerdT_array
        cdef double mdot, h_up
        cdef int I_up,I_down
        cdef FlowPath Flow
        cdef int N = len(exists_keys)
        
        # calloc initializes the values to zero
        cdef double *summerdm = <double*> calloc(N, sizeof(double))
        cdef double *summerdT = <double*> calloc(N, sizeof(double))
        
        for Flow in self:
            #One of the chambers doesn't exist if it doesn't have a mass flow term
            if not Flow.exists:
                continue
            else:
                #Do these once for each flow path to cut down on lookups
                mdot = Flow.mdot
                h_up = Flow.h_up
            
            #Flow must exist then
            
            #If the upstream node is a control volume 
            if Flow.key_up_exists:
                #Flow is leaving the upstream control volume
                summerdm[Flow.ikey_up] -= mdot/omega
                summerdT[Flow.ikey_up] -= mdot/omega*h_up
                
            #If the downstream node is a control volume
            if Flow.key_down_exists:
                #Flow is entering the downstream control volume
                summerdm[Flow.ikey_down] += mdot/omega
                summerdT[Flow.ikey_down] += mdot/omega*h_up
    
        # Create the arraym instances and copy the data over to them
        summerdT_array = arraym()
        summerdT_array.set_data(summerdT,N)
        summerdm_array = arraym()
        summerdm_array.set_data(summerdm,N)
        
#        # Convert c-array to list
#        summerdm_list = [summerdm[i] for i in range(N)]
#        summerdT_list = [summerdT[i] for i in range(N)]
        
        #Free the memory that was allocated
        free(summerdm)
        free(summerdT)
        
        return summerdT_array, summerdm_array
    
    def __reduce__(self):
        return rebuildFPC,(self[:],)
    
    cpdef get_deepcopy(self):
        """
        Using this method, the link to the mass flow function is broken
        """
        return [Flow.get_deepcopy() for Flow in self]

def rebuildFPC(d):
    """
    Used with cPickle to recreate the (empty) flow path collection class
    """
    FPC = FlowPathCollection()
    for Flow in d:
        FPC.append(Flow)
    return FPC

cdef class FlowPath(object):
    
    def __init__(self, key1='', key2='', MdotFcn=None, MdotFcn_kwargs={}):
        self.key1 = key1
        self.key2 = key2
        
        # You are passing in a pre-wrapped function - will be nice and fast since
        # all the calls will stay at the C++ layer
        if isinstance(MdotFcn, FlowFunctionWrapper):
            self.MdotFcn = MdotFcn
        else:
            # Add the bound method in a wrapper - this will keep the calls at
            # the Python level which will make them nice to deal with but slow
            self.MdotFcn = PyFlowFunctionWrapper(MdotFcn, MdotFcn_kwargs)
            
    cpdef dict __cdict__(self, AddStates=False):
        """
        Returns a dictionary with all the terms that are defined at the Cython level
        """
        
        cdef list items
        cdef list States
        cdef dict d={}
        cdef bytes item
        
        items=['mdot','h_up','T_up','p_up','p_down','key_up','key_down','key1','key2','Gas','exists']
        for item in items:
            d[item]=getattr(self,item)
        
        if AddStates:
            States=[('State1',self.State1),('State2',self.State2),('State_up',self.State_up),('State_down',self.State_down)]
            for k,State in States:
                if State is not None:
                    d[k]=State.copy()
        return d
    
    cpdef FlowPath get_deepcopy(self):
        cdef FlowPath FP = FlowPath()
        FP.Gas = self.Gas
        FP.exists = self.exists
        FP.mdot = self.mdot
        FP.h_up = self.h_up
        FP.T_up = self.T_up
        FP.p_up = self.p_up
        FP.p_down = self.p_down
        FP.key_up = self.key_up
        FP.key_down = self.key_down
        FP.key_up_exists = self.key_up_exists
        FP.key_down_exists = self.key_down_exists
        FP.A = self.A
        FP.key1_exists = self.key1_exists
        FP.key2_exists = self.key2_exists
        return FP
        
    cpdef calculate(self, arraym harray):
        """
        calculate
        """
        cdef double p1, p2
        cdef FlowFunctionWrapper FW
        #The states of the chambers
        p1=self.State1.get_p()
        p2=self.State2.get_p()
        
        if p1 > p2:
            # The pressure in chamber 1 is higher than chamber 2
            # and thus the flow is from chamber 1 to 2
            self.key_up=self.key1
            self.key_down=self.key2
            self.State_up=self.State1
            self.State_down=self.State2
            self.T_up=self.State1.get_T()
            self.h_up = harray.data[self.ikey1]
            self.p_up=p1
            self.p_down=p2
            self.key_up_exists = self.key1_exists
            self.key_down_exists = self.key2_exists
            self.ikey_up = self.ikey1
            self.ikey_down = self.ikey2
            self.Gas=self.State1.Fluid
        else:
            self.key_up=self.key2
            self.key_down=self.key1
            self.State_up=self.State2
            self.State_down=self.State1
            self.T_up=self.State2.get_T()
            self.h_up = harray.data[self.ikey2]                    
            self.p_up=p2
            self.p_down=p1
            self.key_up_exists = self.key2_exists
            self.key_down_exists = self.key1_exists
            self.ikey_up = self.ikey2
            self.ikey_down = self.ikey1
            self.Gas=self.State2.Fluid
            
        FW = self.MdotFcn
        self.mdot = FW.call(self)
        
    def __reduce__(self):
        return rebuildFlowPath,(self.__getstate__(),)
        
    def __getstate__(self):
        d={}
        d['MdotFcn']=cPickle.dumps(self.MdotFcn)
        d.update(self.__cdict__().copy())
        return d
        
    def __deepcopy__(self,memo):
        newFM=FlowPath()
        newdict = copy.copy(self.__dict__)
        newFM.__dict__.update(newdict)
        newFM.mdot=copy.copy(self.mdot)
        newFM.key_up=copy.copy(self.key_up)
        newFM.key_down=copy.copy(self.key_down)
        newFM.key1=copy.copy(self.key1)
        newFM.key2=copy.copy(self.key2)
        newFM.h_up=copy.copy(self.h_up)
        return newFM
        
def rebuildFlowPath(d):
    FP = FlowPath()
    FP.MdotFcn = cPickle.loads(d.pop('MdotFcn'))
    for item in d:
        setattr(FP,item,d[item])
    return FP
    