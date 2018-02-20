##__________________________________________________________________||
import collections

##__________________________________________________________________||
# Named for each row in the component dataframe
Component = collections.namedtuple(
    'Component',
    'name eventtype dataset era nevents nfiles cross_section files'
)

##__________________________________________________________________||
