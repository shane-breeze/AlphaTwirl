# Tai Sakuma <tai.sakuma@gmail.com>

##__________________________________________________________________||
class MPEventLoopRunner(object):

    """This class (concurrently) runs instances of `EventLoop`.

    An instance of this class needs to be initialized with a
    communication channel with workers that actually run the
    `EventLoop`::

        runner = MPEventLoopRunner(communicationChannel)

    An example of a communication channel is an instance of
    `CommunicationChannel`.

    The method `begin()` does nothing in the current version::

        runner.begin()

    In older versions, multiple processes are forked in this method.

    Then, you can give an `EventLoop` with the method `run()`::

        runner.run(eventLoop1)

    This class will send the `EventLoop` to a worker through the
    communication channel. The worker, then, runs the `EventLoop`.

    You can call the method `run()` mutiple times::

        runner.run(eventLoop2)
        runner.run(eventLoop3)
        runner.run(eventLoop4)

    If workers are in the background, this method immediately returns.
    Worker are concurrently running the event loops in the background.
    If the worker is in the foreground, this method won't return until
    the worker finishes running the event loop. Whether workers are in
    the background or foreground depends on the communication channel
    with which this class is initialized.

    After giving all event loops that you need to run to this class,
    you need to call the method `end()`::

        results = runner.end()

    If workers are in the background, this method will wait until
    workers finish running all event loops. If the worker is in the
    foreground, this method immediately returns. This method returns
    the results, the list of the values eventLoops return, sorted in
    the order given with `run()`.

    """

    def __init__(self, communicationChannel):
        self.communicationChannel = communicationChannel
        self.nruns = 0

    def __repr__(self):
        return '{}(communicationChannel = {!r}'.format(
            self.__class__.__name__,
            self.communicationChannel
        )

    def begin(self):
        """does nothing.

        Older versions of this class had implementations.
        """
        pass

    def run(self, eventLoop):
        """run the event loop in the background.

        Args:
            eventLoop (EventLoop): an event loop to run

        """

        self.communicationChannel.put(eventLoop)
        self.nruns += 1

    def run_multiple(self, eventLoops):
        """run the event loops in the background.

        Args:
            eventLoops (list): a list of event loops to run

        """

        self.communicationChannel.put_multiple(eventLoops)
        self.nruns += len(eventLoops)

    def end(self):
        """wait until all event loops end and returns the results.

        """

        results, path = self.communicationChannel.receive()

        if self.nruns != len(results):
            import logging
            logger = logging.getLogger(__name__)
            # logger.setLevel(logging.DEBUG)
            logger.warning(
                'too few results received: {} results received, {} expected'.format(
                    len(results),
                    self.nruns
                ))

        return results, path

##__________________________________________________________________||
