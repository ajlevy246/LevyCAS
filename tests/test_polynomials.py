"""Tests for the polynomial operators monomial, polynomial, et cetera"""
import pytest

from levycas import *

def test_monomial():
    x, y = Variable('x'), Variable('y')