from pcsd_cog import model
from pcsd_cog.events import EventData


## EQ
def test_1_eq_1():
    rule = model.Rule() + "1 == 1"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))


def test_aa_eq_aa():
    rule = model.Rule() + "aa == aa"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))


def test_1_eq_2():
    rule = model.Rule() + "1 == 2"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", "")) == False


## NE
def test_1_ne_2():
    rule = model.Rule() + "1 != 2"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))

def test_2_ne_2():
    rule = model.Rule() + "2 != 2"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", "")) == False

## LT
def test_1_lt_2():
    rule = model.Rule() + "1 < 2"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))


## LE
def test_2_le_2():
    rule = model.Rule() + "2 <= 2"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))


## GT
def test_2_gt_1():
    rule = model.Rule() + "2 > 1"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))


# GE
def test_2_ge_2():
    rule = model.Rule() + "2 >= 2"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))


# LIKE
def test_aaa_like_aa():
    rule = model.Rule() + "aa LIKE aa.*"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))


def test_baa_notlike_aa():
    rule = model.Rule() + "ba LIKE aa.*"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", "")) == False
