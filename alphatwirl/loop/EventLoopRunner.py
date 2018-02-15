# Tai Sakuma <tai.sakuma@gmail.com>
from ..progressbar import NullProgressMonitor

##__________________________________________________________________||
class EventLoopRunner(object):
    """This class runs instances of `EventLoop` and keeps the results. It
    will return the results when `end()` is called.

    """
    def __init__(self, progressMonitor=None):
        if progressMonitor is None: progressMonitor = NullProgressMonitor()
        self.progressReporter = progressMonitor.createReporter()
        self.results = [ ]

    def __repr__(self):
        return '{}(progressReporter={!r}, results={!r})'.format(
            self.__class__.__name__,
            self.progressReporter,
            self.results
        )

    def begin(self):
        self.results = [ ]

    def run(self, eventLoop):
        self.results.append(eventLoop(progressReporter=self.progressReporter))

    def run_multiple(self, eventLoops):
        for eventLoop in eventLoops:
            self.run(eventLoop)

    def end(self):
        return self.results

##__________________________________________________________________||
