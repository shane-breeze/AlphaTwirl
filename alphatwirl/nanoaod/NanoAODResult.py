# Tai Sakuma <tai.sakuma@gmail.com>

##__________________________________________________________________||
import os
import re

from Component import Component

##__________________________________________________________________||
class NanoAODResult(object):
    """A NanoAOD result

    Args:
        path (str): the path to the Heppy result
        component_names (list, optional): the list of the names of the components to read. If not given, all components except the ones listed in `excludeList` will be read.
        exclude_list (list, optional): a list of the names of the directory in the nanoAOD result directory which are to be excluded to be considered as component.
    """

    def __init__(self, path,
                 component_names=None,
                 exclude_list=[],
    ):
        self.path = os.path.normpath(path)
        component_names["name"] = component_names[["Dataset","Era"]].apply(
                "_".join,
                axis=1,
                )
        component_names["path"] = component_names[["EventType","Dataset","Era"]].apply(
                lambda x: os.path.join(self.path, '/'.join(x)),
                axis=1
                )

        for path in component_names["path"]:
            if not os.path.exists(path):
                raise ValueError("Path does not exists: {}".format(path))

        self.components_df = component_names

    def __getattr__(self, name):
        if name not in self.components_df:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
        return os.path.join(self.path, name)

    def components(self):
        return [Component(name=row.name, path=row.path)
                for row in self.components_df.itertuples()]

##__________________________________________________________________||
