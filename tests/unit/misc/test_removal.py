# Tai Sakuma <tai.sakuma@gmail.com>
from __future__ import print_function
import logging

import pytest

try:
   import cPickle as pickle
except:
   import pickle

from alphatwirl.misc.removal import _removed

##__________________________________________________________________||
@_removed(msg='extra message')
def func():
    pass

def test_func_logging(caplog):
    with pytest.raises(RuntimeError):
       with caplog.at_level(logging.ERROR):
          func()

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'ERROR'
    assert 'test_removal' in caplog.records[0].name
    assert 'func() is removed. extra message' in caplog.records[0].msg

def test_func_name():
    assert  'func' == func.__name__

def test_func_pickle():
    pickle.dumps(func)

@_removed()
def func_without_msg():
    pass

def test_func_logging_without_msg(caplog):
    with pytest.raises(RuntimeError):
       with caplog.at_level(logging.ERROR):
          func_without_msg()

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'ERROR'
    assert 'test_removal' in caplog.records[0].name
    assert 'func_without_msg() is removed.' in caplog.records[0].msg

##__________________________________________________________________||
@_removed(msg='extra message')
class ClassWithInit(object):
    def __init__(self):
        pass

@_removed(msg='extra message')
class ClassWithoutInit(object):
    pass

@_removed()
class ClassWithInitNoMsg(object):
    def __init__(self):
        pass

@_removed()
class ClassWithoutInitNoMsg(object):
    pass

@pytest.mark.parametrize('Class', (ClassWithInit, ClassWithoutInit))
def test_class_logging(Class, caplog):
    with pytest.raises(RuntimeError):
       with caplog.at_level(logging.ERROR):
          c = Class()
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'ERROR'
    assert 'test_removal' in caplog.records[0].name
    expected = '{} is removed. extra message'.format(Class.__name__)
    assert expected in caplog.records[0].msg

@pytest.mark.parametrize('Class', (ClassWithInitNoMsg, ClassWithoutInitNoMsg))
def test_class_logging_no_msg(Class, caplog):
    with pytest.raises(RuntimeError):
       with caplog.at_level(logging.ERROR):
          c = Class()
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'ERROR'
    assert 'test_removal' in caplog.records[0].name
    expected = '{} is removed.'.format(Class.__name__)
    assert expected in caplog.records[0].msg

##__________________________________________________________________||
