#!/usr/bin/env python
# Tai Sakuma <tai.sakuma@gmail.com>
from alphatwirl.progressbar import ProgressReport, BProgressMonitor
from alphatwirl.progressbar import ProgressBar
from alphatwirl.progressbar import ProgressPrint
from alphatwirl.concurrently import CommunicationChannel, MultiprocessingDropbox
import sys
import time, random
import uuid

##__________________________________________________________________||
class Task(object):
    def __init__(self, name):
        self.name = name
    def __call__(self, progressReporter = None):
        n = random.randint(5, 1000000)
        taskid = uuid.uuid4()
        time.sleep(random.randint(0, 3))
        for i in range(n):
            time.sleep(0.0001)
            report = ProgressReport(name = self.name, done = i + 1, total = n, taskid = taskid)
            progressReporter.report(report)
        return None

##__________________________________________________________________||
progressBar = ProgressBar() if sys.stdout.isatty() else ProgressPrint()

##__________________________________________________________________||
progressMonitor = BProgressMonitor(presentation = progressBar)
dropbox = MultiprocessingDropbox(nprocesses = 10, progressMonitor = progressMonitor)
channel = CommunicationChannel(dropbox)
progressMonitor.begin()
channel.begin()
channel.put(Task("loop"))
channel.put(Task("another loop"))
channel.put(Task("more loop"))
channel.put(Task("loop loop loop"))
channel.put(Task("l"))
channel.put(Task("loop6"))
channel.put(Task("loop7"))
channel.put(Task("loop8"))
channel.put(Task("loop6"))
channel.receive()
channel.end()
progressMonitor.end()

##__________________________________________________________________||
