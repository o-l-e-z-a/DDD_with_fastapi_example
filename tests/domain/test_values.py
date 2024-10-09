import operator

from decimal import Decimal

import pytest

from src.domain.base.exceptions import IntegerError, PositiveNumberError
from src.domain.base.values import PositiveIntNumber


@pytest.mark.parametrize('valid_number', [1, 100*100, 1000*1000])
def test_positive_int_number_valid(valid_number):
    positive_int_number = PositiveIntNumber(valid_number)

    assert positive_int_number.value == valid_number


@pytest.mark.parametrize('invalid_number', [0, -1, -100*100, -7])
def test_positive_int_number_with_pos_int_error(invalid_number):
    with pytest.raises(PositiveNumberError):
        PositiveIntNumber(invalid_number)


@pytest.mark.parametrize('invalid_number', [2.4, 0.2, Decimal("2"), 100000000000.0])
def test_positive_int_number_with_int_error(invalid_number):
    with pytest.raises(IntegerError):
        PositiveIntNumber(invalid_number)


@pytest.mark.parametrize(
    'int_number, operation',
    ((2, operator.add), (100, operator.mul), (10000, operator.truediv), (514, operator.sub))
)
def test_operation_positive_int_number_with_int(int_number, operation):
    value = 666
    p = PositiveIntNumber(value)
    expected = operation(value, int_number)

    actual = operation(p, int_number)

    assert actual == expected


@pytest.mark.parametrize(
    'int_number, operation',
    ((2, operator.add), (100, operator.mul), (10000, operator.truediv), (514, operator.sub))
)
def test_r_operation_positive_int_number_with_int(int_number, operation):
    value = 666
    p = PositiveIntNumber(value)

    res = operation(int_number, p)

    assert res == operation(int_number, value)


@pytest.mark.parametrize(
    'int_number, operation',
    ((2, operator.add), (100, operator.mul), (10000, operator.truediv), (514, operator.sub))
)
def test_radd_positive_int_number_with_positive_int_number(int_number, operation):
    value = 666
    p = PositiveIntNumber(value)
    p2 = PositiveIntNumber(int_number)

    res = operation(p, p2)

    assert res == operation(value, int_number)
