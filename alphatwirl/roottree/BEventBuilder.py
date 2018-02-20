# Tai Sakuma <tai.sakuma@gmail.com>
#import ROOT
from rootpy.io import root_open
from .BEvents import BEvents

##__________________________________________________________________||
class BEventBuilder(object):
    def __init__(self, config):
        self.config = config

    def __repr__(self):
        return '{}({!r})'.format(
            self.__class__.__name__,
            self.config
        )

    def __call__(self):
        #chain = ROOT.TChain(self.config.treeName)
        #for path in self.config.inputPaths:
        #    chain.Add(path)
        if len(self.config.inputPaths)>1:
            raise ValueError("Too many input paths. Implementation only works for 1 file per process")
        file_ = root_open(self.config.inputPaths[0])
        chain = file_.Get(self.config.treeName)
        events = BEvents(chain, self.config.maxEvents, self.config.start)
        events.config = self.config
        return events

##__________________________________________________________________||
