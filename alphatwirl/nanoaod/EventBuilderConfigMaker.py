# Tai Sakuma <tai.sakuma@gmail.com>
import os

import ROOT

from ..roottree import EventBuilderConfig as BaseEventBuilderConfig
from .EventBuilderConfig import EventBuilderConfig as NanoAODEventBuilderConfig

##__________________________________________________________________||
class EventBuilderConfigMaker(object):
    def __init__(self, treeName):
        self.treeName = treeName

    def create_config_for(self, dataset, files, start, length):
        base_config = BaseEventBuilderConfig(
            inputPaths = files,
            treeName = self.treeName,
            maxEvents = length,
            start = start,
            name = dataset.name, # for the progress report writer
        )
        config = NanoAODEventBuilderConfig(
            base = base_config,
            component = dataset # for scribblers
        )
        return config

    def file_list_in(self, dataset, maxFiles = -1):
        #files = [os.path.join(dataset.path,p) for p in os.listdir(dataset.path) if ".root" in p]
        #files = [os.path.join(dataset.path), "*.root"]
        if maxFiles < 0:
            return dataset.files
        return dataset.files[:min(maxFiles, len(files))]

    def nevents_in_file(self, path):
        file = ROOT.TFile.Open(path)
        tree = file.Get(self.treeName)
        return tree.GetEntries() # GetEntries() is slow. call only as
                                 # many times as necessary

##__________________________________________________________________||
