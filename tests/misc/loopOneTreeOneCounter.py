#!/usr/bin/env python
# Tai Sakuma <tai.sakuma@gmail.com>
import ROOT
import argparse

import alphatwirl

##__________________________________________________________________||
ROOT.gROOT.SetBatch(1)

##__________________________________________________________________||
default_input = '/afs/cern.ch/work/s/sakuma/public/cms/c150130_RA1_data/80X/MC/20160811_B01/ROC_MC_SM/TTJets_HT800to1200_madgraphMLM/roctree/tree.root'

##__________________________________________________________________||
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', default = default_input, help = 'path to the input file')
parser.add_argument("-n", "--nevents", default = -1, type = int, help = "maximum number of events to process")
parser.add_argument("-t", "--tree", default = 'tree', help = "the name of the tree")
args = parser.parse_args()

##__________________________________________________________________||
file = ROOT.TFile.Open(args.input)
tree = file.Get(args.tree)
events = alphatwirl.roottree.BEvents(tree, args.nevents)

keyAttrNames = ('nJet40', 'nBJet40')
binnings = (alphatwirl.binning.Echo(), alphatwirl.binning.Echo())
keyValueComposer = alphatwirl.summary.KeyValueComposer(keyAttrNames, binnings)
summary = alphatwirl.summary.Count()
summarizer = alphatwirl.summary.Summarizer(keyValueComposer, summary)

summarizer.begin(events)
for event in events:
    summarizer.event(event)
summarizer.end()

print summarizer.results().results()

##__________________________________________________________________||
