# Tai Sakuma <tai.sakuma@gmail.com>
from .FactoryDispatcher import FactoryDispatcher

##__________________________________________________________________||
def NotFactory(path_cfg, name = None,  **kargs):
    return kargs['NotClass'](selection = FactoryDispatcher(path_cfg, **kargs), name = name)

##__________________________________________________________________||
