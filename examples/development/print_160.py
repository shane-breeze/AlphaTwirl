#!/usr/bin/env python
# Tai Sakuma <tai.sakuma@cern.ch>
import os
import argparse
from AlphaTwirl import EventBuilder, CombineIntoPandasDataFrame, WritePandasDataFrameToFile
from AlphaTwirl.HeppyResult import HeppyResult
from AlphaTwirl.Counter import Counts, GenericKeyComposer, Counter
from AlphaTwirl.Binning import RoundLog
from AlphaTwirl.EventReader import Collector

##__________________________________________________________________||
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--heppydir', default = '/Users/sakuma/work/cms/c150130_RA1_data/c150130_01_PHYS14/201525_SingleMu', help = "Heppy results dir")
parser.add_argument('-o', '--outdir', default = 'tmp')
parser.add_argument("-n", "--nevents", default = -1, type = int, help = "maximum number of events to process for each component")
args = parser.parse_args()

analyzerName = 'treeProducerSusyAlphaT'
fileName = 'tree.root'
treeName = 'tree'
outPath = os.path.join(args.outdir, 'tbl_met.txt')

binning = RoundLog(0.1, 0)
keyComposer = GenericKeyComposer(('met_pt', ), (binning, ))
resultsCombinationMethod = CombineIntoPandasDataFrame()
deliveryMethod = WritePandasDataFrameToFile(outPath)
collector = Collector(resultsCombinationMethod, deliveryMethod)

eventBuilder = EventBuilder(analyzerName, fileName, treeName, args.nevents)

heppyResult = HeppyResult(args.heppydir)
for component in heppyResult.components():

    counts = Counts()
    counter = Counter(('met', ), keyComposer, counts)

    collector.addReader(component.name, counter)

    events = eventBuilder.build(component)
    for event in events:
        counter.event(event)

collector.collect()

##__________________________________________________________________||