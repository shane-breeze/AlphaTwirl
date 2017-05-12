# Tai Sakuma <tai.sakuma@cern.ch>
from .EventSelectionModules.basic import All
from .EventSelectionModules.basic import Any
from .EventSelectionModules.basic import Not
from .EventSelectionModules.LambdaStr import LambdaStr
from .EventSelectionFactories.FactoryDispatcher import FactoryDispatcher

import os, sys

##__________________________________________________________________||
thisDir = os.path.dirname(os.path.realpath(__file__))
if not thisDir in sys.path: sys.path.append(thisDir)

##__________________________________________________________________||
def build_selection(**kargs):

    if 'aliasDict' not in kargs: kargs['aliasDict'] = { }

    if 'AllClass' not in kargs: kargs['AllClass'] = All
    if 'AnyClass' not in kargs: kargs['AnyClass'] = Any
    if 'NotClass' not in kargs: kargs['NotClass'] = Not
    if 'LambdaStrClass' not in kargs: kargs['LambdaStrClass'] = LambdaStr

    return FactoryDispatcher(**kargs)

##__________________________________________________________________||
