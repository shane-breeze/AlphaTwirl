# Tai Sakuma <tai.sakuma@gmail.com>
from .FactoryDispatcher import FactoryDispatcher

##__________________________________________________________________||
def AllFactory(path_cfg_list, name = None,  **kargs):

    ret = kargs['AllClass'](name = name)
    ret.set_args(kargs)

    for path_cfg in path_cfg_list:
        ret.add(FactoryDispatcher(path_cfg, **kargs))

    return ret

##__________________________________________________________________||
