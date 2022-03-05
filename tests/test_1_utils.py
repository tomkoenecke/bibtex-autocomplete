"""Tests for functions/classes in bibtexautcomplete/defs"""

from bibtexautocomplete.utils.only_exclude import OnlyExclude
from bibtexautocomplete.utils.safe_json import SafeJSON


def test_OnlyExclude_only():
    test = [1, 2, 3]
    a = OnlyExclude(test, None)
    b = OnlyExclude.from_nonempty(test, [])
    for i in range(10):
        if i in test:
            assert i in a
            assert i in b
        else:
            assert i not in a
            assert i not in b
    assert list(a.filter(range(10), lambda x: x)) == test


def test_OnlyExclude_exclude():
    test = [1, 2, 3]
    a = OnlyExclude(None, test)
    b = OnlyExclude.from_nonempty([], test)
    for i in range(10):
        if i in test:
            assert i not in a
            assert i not in b
        else:
            assert i in a
            assert i in b
    assert list(a.filter(range(10), lambda x: x)) == [0, 4, 5, 6, 7, 8, 9]


def test_SafeJSON():
    a = SafeJSON({"a": 5, "b": "bonjour", "c": [1, 2, {"3": 5, "4": [True, False]}]})
    assert a[0].value is None
    assert a["a"].to_int() == 5
    assert a["b"].to_str() == "bonjour"
    assert a["c"][0].to_int() == 1
    for key, val in a["c"][3].iter_dict():
        if key == "3":
            assert val.to_int() == 5
        elif key == "4":
            for i, x in enumerate(val.iter_list()):
                assert (i == 0) == x.to_bool()