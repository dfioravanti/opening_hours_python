from datetime import datetime

import pytest
import pytz
from src.internals.timeslots import (Timeslot, ValidationError,
                                     prettify_timeslots)

from .utils import load_data_results

tz = pytz.timezone('GMT')


def test_string_representation():
    """
    Test if the __str__ method returns the correct representation
    """
    opening_string = "1 AM"
    opening_timestamp = int(datetime.strptime(
        f"1970-01-01 {opening_string}", "%Y-%m-%d %I %p").replace(tzinfo=tz).timestamp())
    closing_string = "5 AM"
    closing_timestamp = int(datetime.strptime(
        f"1970-01-01 {closing_string}", "%Y-%m-%d %I %p").replace(tzinfo=tz).timestamp())

    string = f"{opening_string} - {closing_string}"
    timeslot = Timeslot.from_timestamps(
        opening_timestamp=opening_timestamp, closing_timestamp=closing_timestamp)

    assert str(timeslot) == string

    opening_string = "1 AM"
    opening_timestamp = int(datetime.strptime(
        f"1970-01-01 {opening_string}", "%Y-%m-%d %I %p").replace(tzinfo=tz).timestamp())
    closing_string = "1 AM"
    closing_timestamp = int(datetime.strptime(
        f"1970-01-01 {closing_string}", "%Y-%m-%d %I %p").replace(tzinfo=tz).timestamp())

    string = f"{opening_string} - {closing_string}"
    timeslot = Timeslot.from_timestamps(
        opening_timestamp=opening_timestamp, closing_timestamp=closing_timestamp)

    assert str(timeslot) == string


def test_one_day():
    """
    Test if the code works as intended when we have only one open day
    """
    test_data, test_data_results = load_data_results(base_filename="one_day")
    for data, result in zip(test_data, test_data_results):
        assert prettify_timeslots(data) == result


def test_two_days():
    """
    Test if the code works as intended when we have only two open days
    """
    test_data, test_data_results = load_data_results(base_filename="two_days")
    for data, result in zip(test_data, test_data_results):
        assert prettify_timeslots(data) == result


def test_full_days():
    """
    Test if the code works as intended when we having all days
    """
    test_data, test_data_results = load_data_results(base_filename="seven_days")
    for data, result in zip(test_data, test_data_results):
        assert prettify_timeslots(data) == result


def test_errors():
    """
    Test if errors are detected correctly 
    """
    test_data = load_data_results(base_filename="errors", only_data=True)
    for data in test_data:
        with pytest.raises(ValidationError):
            prettify_timeslots(data)
