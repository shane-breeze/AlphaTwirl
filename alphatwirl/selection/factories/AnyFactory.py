# Tai Sakuma <tai.sakuma@cern.ch>
from .FactoryDispatcher import FactoryDispatcher

##__________________________________________________________________||
def AnyFactory(path_cfg_list, name = None,  **kargs):

    ret = kargs['AnyClass'](name = name)
    ret.set_args(kargs)

    for path_cfg in path_cfg_list:
        ret.add(FactoryDispatcher(path_cfg, **kargs))

    return ret

##__________________________________________________________________||
