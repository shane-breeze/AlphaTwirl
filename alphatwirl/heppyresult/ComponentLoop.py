# Tai Sakuma <tai.sakuma@gmail.com>

from alphatwirl.datasetloop import DatasetLoop

##__________________________________________________________________||
class ComponentLoop(object):

    def __init__(self, heppyResult, reader):
        self.reader = reader
        self.heppyResult = heppyResult
        self.components = self.heppyResult.components()
        self.datasetloop = DatasetLoop(datasets=self.components, reader=self.reader)

    def __repr__(self):
        name_value_pairs = (
            ('reader',      self.reader),
            ('heppyResult', self.heppyResult),
        )
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(['{}={!r}'.format(n, v) for n, v in name_value_pairs]),
        )

    def __call__(self):
        return self.datasetloop()

##__________________________________________________________________||
