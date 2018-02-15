#!/usr/bin/env python
# Tai Sakuma <tai.sakuma@gmail.com>
import os
import argparse


import alphatwirl
import alphatwirl.heppyresult as HeppyResult
HeppyResult.componentHasTheseFiles[:] = ['roctree']

##__________________________________________________________________||
parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outDir', default = os.path.join('tbl', 'out'))
parser.add_argument('-n', '--nevents', default = -1, type = int, help = 'maximum number of events to process for each component')
parser.add_argument('--max-events-per-process', default = -1, type = int, help = 'maximum number of events per process')

configurer = alphatwirl.AlphaTwirlConfigurerFromArgs()
configurer.add_arguments(parser)

args = parser.parse_args()

cfg = configurer.configure(args)
alphaTwirl = alphatwirl.AlphaTwirl(config = cfg)

##__________________________________________________________________||
analyzerName = 'roctree'
fileName = 'tree.root'
treeName = 'tree'

##__________________________________________________________________||
tbl_xsec_path = os.path.join(args.outDir, 'tbl_xsec.txt')
tblXsec = heppyresult.TblComponentConfig(
    outPath = tbl_xsec_path,
    columnNames = ('xsec', ),
    keys = ('xSection', ),
)
alphaTwirl.addComponentReader(tblXsec)

tbl_nevt_path = os.path.join(args.outDir, 'tbl_nevt.txt')
tblNevt = heppyresult.TblCounter(
    outPath = tbl_nevt_path,
    columnNames = ('nevt', 'nevt_sumw'),
    analyzerName = 'skimAnalyzerCount',
    fileName = 'SkimReport.txt',
    levels = ('All Events', 'Sum Weights')
)
alphaTwirl.addComponentReader(tblNevt)

##__________________________________________________________________||
from alphatwirl.binning import RoundLog
tblcfg = [
    dict(
        keyAttrNames = ('met_pt', ),
        binnings = (RoundLog(0.1, 10), ),
        keyOutColumnNames = ('met', ),
     )
]

tableConfigCompleter = alphatwirl.configure.TableConfigCompleter(
    defaultSummaryClass = alphatwirl.summary.Count,
    defaultOutDir = args.outDir,
    createOutFileName = alphatwirl.configure.TableFileNameComposer()
)
tblcfg = [tableConfigCompleter.complete(c) for c in tblcfg]

reader_collector_pair = [alphatwirl.configure.build_counter_collector_pair(c) for c in tblcfg]
reader = alphatwirl.loop.ReaderComposite()
collector = alphatwirl.loop.CollectorComposite(alphaTwirl.progressMonitor.createReporter())
for r, c in reader_collector_pair:
    reader.add(r)
    collector.add(c)
eventLoopRunner = alphatwirl.loop.MPEventLoopRunner(alphaTwirl.communicationChannel)
eventBuilder = alphatwirl.heppyresult.EventBuilder(analyzerName, fileName, treeName, args.nevents)
eventReader = alphatwirl.loop.EventsInDatasetReader(eventBuilder, eventLoopRunner, reader, collector, args.max_events_per_process)
alphaTwirl.addComponentReader(eventReader)

alphaTwirl.run()
alphaTwirl.end()

##__________________________________________________________________||
import pandas as pd

##__________________________________________________________________||
d1 = pd.read_table(os.path.join(args.outDir, 'tbl_process.txt'), delim_whitespace = True)
d2 = pd.read_table(os.path.join(args.outDir, 'tbl_xsec.txt'), delim_whitespace = True)

d = pd.merge(d1, d2)
d = d[['phasespace', 'xsec']].drop_duplicates()

f = open(os.path.join(args.outDir, 'tbl_xsec.txt'), 'w')
d.to_string(f, index = False)
f.write("\n")
f.close()

##__________________________________________________________________||
