# Tai Sakuma <tai.sakuma@gmail.com>
import os

import ROOT

from ..roottree import EventBuilderConfig

##__________________________________________________________________||
class EventBuilderConfigMaker(object):
    def __init__(self, tree_name):
        self.tree_name = tree_name

    def create_config_for(self, dataset, files, start, length):
        config = EventBuilderConfig(
            inputPaths = files,
            treeName = self.tree_name,
            maxEvents = length,
            start = start,
            name = dataset.name, # for the progress report writer
        )
        return config

    def file_list_in(self, dataset, maxFiles = -1):
        files = [os.path.join(dataset.path,p) for p in os.listdir(dataset.path) if ".root" in p]
        #files = [os.path.join(dataset.path), "*.root"]
        if maxFiles < 0:
            return files
        return files[:min(maxFiles, len(files))]

    def nevents_in_file(self, path):
        file = ROOT.TFile.Open(path)
        tree = file.Get(self.treeName)
        return tree.GetEntries() # GetEntries() is slow. call only as
                                 # many times as necessary

##__________________________________________________________________||
