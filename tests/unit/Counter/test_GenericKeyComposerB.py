import AlphaTwirl.Counter as Counter
import unittest
import logging

##__________________________________________________________________||
class MockEvent(object):
    pass

##__________________________________________________________________||
class MockBinningEcho(object):
    def __call__(self, val):
        return val

    def next(self, val):
        return val + 1

##__________________________________________________________________||
class MockBinningNone(object):
    def __call__(self, val):
        return None

    def next(self, val):
        return val + 1

##__________________________________________________________________||
class TestGenericKeyComposerB(unittest.TestCase):

    def test_call_1var(self):
        keyComposer = Counter.GenericKeyComposerB(('var1', ), (MockBinningEcho(), ))

        event = MockEvent()
        event.var1 = [ ]
        keyComposer.begin(event)

        event.var1[:] = [12, ]
        self.assertEqual(((12, ), ), keyComposer(event))

    def test_call_2vars(self):
        keyComposer = Counter.GenericKeyComposerB(('var1', 'var2'), (MockBinningEcho(), MockBinningEcho()))

        event = MockEvent()
        event.var1 = [ ]
        event.var2 = [ ]
        keyComposer.begin(event)

        event.var1[:] = [15, ]
        event.var2[:] = [22, ]
        self.assertEqual(((15, 22), ), keyComposer(event))

    def test_empty_key_1var(self):
        keyComposer = Counter.GenericKeyComposerB(('var1', ), (MockBinningNone(), ))

        event = MockEvent()
        event.var1 = [ ]
        keyComposer.begin(event)

        event.var1[:] = [12, ]
        self.assertEqual(( ), keyComposer(event))

    def test_empty_key_2vars_var1(self):
        keyComposer = Counter.GenericKeyComposerB(('var1', 'var2'), (MockBinningNone(), MockBinningEcho()))

        event = MockEvent()
        event.var1 = [ ]
        event.var2 = [ ]
        keyComposer.begin(event)

        event.var1[:] = [15, ]
        event.var2[:] = [22, ]
        self.assertEqual(( ), keyComposer(event))

    def test_empty_key_2vars_var2(self):
        keyComposer = Counter.GenericKeyComposerB(('var1', 'var2'), (MockBinningEcho(), MockBinningNone()))

        event = MockEvent()
        event.var1 = [ ]
        event.var2 = [ ]
        keyComposer.begin(event)

        event.var1[:] = [15, ]
        event.var2[:] = [22, ]
        self.assertEqual(( ), keyComposer(event))

    @unittest.skip("skip because of logging. assertLogs can be used here for Python 3.4")
    def test_empty_branch(self):
        keyComposer = Counter.GenericKeyComposerB(('var1', 'var2'), (MockBinningEcho(), MockBinningEcho()))

        event = MockEvent()
        event.var1 = [ ]
        keyComposer.begin(event)

        event.var1[:] = [15, ]
        self.assertEqual(( ), keyComposer(event))

    def test_indices_1(self):
        keyComposer = Counter.GenericKeyComposerB(('var1', ), (MockBinningEcho(), ), indices = (0, ))
        event = MockEvent()
        event.var1 = [ ]
        keyComposer.begin(event)

        event.var1[:] = [12, ]
        self.assertEqual(((12, ), ), keyComposer(event))

    def test_indices_2(self):
        keyComposer = Counter.GenericKeyComposerB(('var1', ), (MockBinningEcho(), ), indices = (1, ))
        event = MockEvent()
        event.var1 = [ ]
        keyComposer.begin(event)

        event.var1[:] = [12, 8, 6]
        self.assertEqual(((8, ), ), keyComposer(event))

        event.var1[:] = [3, ]
        self.assertEqual(( ), keyComposer(event))

    def test_indices_3(self):
        keyComposer = Counter.GenericKeyComposerB(('var1', 'var2', 'var3'), (MockBinningEcho(), MockBinningEcho(), MockBinningEcho()), indices = (1, None, 2))
        event = MockEvent()
        event.var1 = [ ]
        event.var2 = [ ]
        event.var3 = [ ]
        keyComposer.begin(event)

        event.var1[:] = [12, 8, 6]
        event.var2[:] = [232, ]
        event.var3[:] = [111, 222, 333]
        self.assertEqual(((8, 232, 333), ), keyComposer(event))

    def test_indices_inclusive_1(self):
        keyComposer = Counter.GenericKeyComposerB(('var1', ), (MockBinningEcho(), ), indices = ('*', ))
        event = MockEvent()
        event.var1 = [ ]
        keyComposer.begin(event)

        event.var1[:] = [12, 8, 6]
        self.assertEqual(((12, ), (8, ), (6, )), keyComposer(event))

    def test_indices_inclusive_2(self):
        keyComposer = Counter.GenericKeyComposerB(('var1', 'var2'), (MockBinningEcho(), MockBinningEcho()), indices = ('*', None))
        event = MockEvent()
        event.var1 = [ ]
        event.var2 = [ ]
        keyComposer.begin(event)

        event.var1[:] = [12, 8, 6]
        event.var2[:] = [5, ]
        self.assertEqual(((12, 5), (8, 5), (6, 5)), keyComposer(event))

    def test_indices_inclusive_3(self):
        keyComposer = Counter.GenericKeyComposerB(('var1', 'var2'), (MockBinningEcho(), MockBinningNone()), indices = ('*', None))
        event = MockEvent()
        event.var1 = [ ]
        event.var2 = [ ]
        keyComposer.begin(event)

        event.var1[:] = [12, 8, 6]
        event.var2[:] = [5, ]
        self.assertEqual(( ), keyComposer(event))

    def test_indices_inclusive_4(self):
        keyComposer = Counter.GenericKeyComposerB(('var1', 'var2'), (MockBinningEcho(), MockBinningEcho()), indices = ('*', '*'))
        event = MockEvent()
        event.var1 = [ ]
        event.var2 = [ ]
        keyComposer.begin(event)

        event.var1[:] = [12, 8, 6]
        event.var2[:] = [5, 2]
        self.assertEqual(((12, 5), (12, 2), (8, 5), (8, 2), (6, 5), (6, 2)), keyComposer(event))

##__________________________________________________________________||
