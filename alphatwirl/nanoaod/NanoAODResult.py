# Tai Sakuma <tai.sakuma@gmail.com>

##__________________________________________________________________||
import os
import re
import numpy as np

from Component import Component

##__________________________________________________________________||
class NanoAODResult(object):
    """A NanoAOD result

    Args:
        path (str): the path to the Heppy result
        component_names (list, optional): the list of the names of the components to read. If not given, all components except the ones listed in `excludeList` will be read.
        exclude_list (list, optional): a list of the names of the directory in the nanoAOD result directory which are to be excluded to be considered as component.
    """

    def __init__(self,
                 component_df=None,
                 exclude_list=[],
    ):
        component_df["name"] = component_df[["dataset","era"]].apply("_".join, axis=1)
        self.components_df = component_df

    #def __getattr__(self, name):
    #    if name not in self.components_df:
    #        raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
    #    return os.path.join(self.path, name)

    def components(self):
        comps = []
        for row in self.components_df.itertuples():
            comp_dict = {}
            comp_dict["name"] = row.name
            comp_dict["eventtype"] = row.eventtype
            comp_dict["dataset"] = row.dataset
            comp_dict["era"] = row.era
            comp_dict["nevents"] = row.nevents
            comp_dict["nfiles"] = row.nfiles
            comp_dict["files"] = row.files

            # MC stuff
            try:
                comp_dict["cross_section"] = row.cross_section
            except AttributeError:
                comp_dict["cross_section"] = np.nan

            comps.append(Component(**comp_dict))
        return comps

##__________________________________________________________________||
