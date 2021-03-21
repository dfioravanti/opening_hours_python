from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import time
from enum import Enum, auto
from json.decoder import JSONDecodeError
from typing import Dict, List, Optional, Union


class ValidationError(Exception):
    """
    Exception used to signal that it was not possible to process the JSON input
    """
    pass


class Day(Enum):
    """
    Enum used to represent a day of the week.
    """
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    def __str__(self) -> str:

        return self.name.capitalize()


# We use this to guarantee that we are going though a week in the correct order
WEEK = [Day.MONDAY, Day.TUESDAY, Day.WEDNESDAY,
        Day.THURSDAY, Day.FRIDAY, Day.SATURDAY, Day.SUNDAY]


class Status(Enum):
    """
    Enum used to represent the possible status of the restaurant.
    """
    OPEN = auto()
    CLOSE = auto()


@dataclass
class Timeslot:
    """
    Class used to represent a timeslot where the restourant is open.
    """
    opening: time
    closing: time

    @classmethod
    def from_timestamps(cls, opening_timestamp: int, closing_timestamp: int) -> Timeslot:
        """
        Create an object from a pair of timestamps that represent the number of seconds from midnight.

        Parameters
        ----------
        opening_timestamp : int
            timestamp of the opening time in seconds from midnight
        closing_timestamp : int
            timestamp of the closing time in seconds from midnight

        Returns
        -------
        Timeslot
            Object representing the timeslot associated with the timestamps
        """

        opening = _time_from_timestamp(opening_timestamp)
        closing = _time_from_timestamp(closing_timestamp)

        return cls(opening, closing)

    def __str__(self) -> str:
        """
        Returns the string representation of the object.

        The representation will be in the format HH[:MM[:SS]] AM|PM - HH[:MM[:SS]] AM|PM

        Returns
        -------
        str
            The string representation
        """

        return f"{_time_to_pretty_string(self.opening)} - {_time_to_pretty_string(self.closing)}"


RawInputs = Dict[str, List[Dict[str, Union[str, int]]]]
# These needs to be defined after the Day and Timeslot types otherwise the parser is not happy
Inputs = Dict[Day, List[Dict[str, Union[str, int]]]]
Timeslots = Dict[Day, List[Timeslot]]


def prettify_timeslots(json_input: str) -> Dict[str, str]:
    """
    Prettify a string that contains a valid json representing opening hours in the "ugly format".

    The ugly format is defined as a dictionary with the following format
        weekday: [
            {
                "status": "open"/"close"
                "value": int
            }
            ...
        ]
    where value is the number of seconds from the midnight of the day. 
    Days which are missing or where there are no entries are considered days where the restaurant is closed.

    The prettified output is in a dictionary with the following format
        weekday: "time_opening_1 - time_closing_1, ..., time_opening_n - time_closing_n"
    where both time_opening and time_closing are in the 12h clock format. 
    Minutes and seconds are displayed only if needed.

    Parameters
    ----------
    json_input : str
        A string contain a JSON encoded "ugly" list of timeslots.

    Returns
    -------
    Dict[str, str]
        A prettified version of the input

    Raises
    ------
    ValidationError
        Raised if
            * The JSON cannot be parsed
            * If the first status, not on Monday, is a close
            * There are same type entries back to back
            * There is no matching close entry on Monday for an opening on Sunday
            * There is no matching opening on Sunday for a closing on Monday
    """

    try:
        raw_inputs: RawInputs = json.loads(json_input)
    except JSONDecodeError:
        raise ValidationError("The input is not a valid JSON")

    # Sort the raw inputs by timestamp for each day.
    # This allows us to establish some invariants on the data:
    # Each opening should be followed by a closing
    # There are no repeated opening/closing
    # If a day has only one closing then the restourant is closed for that day
    inputs: Inputs = {}
    for raw_day, raw_values in raw_inputs.items():
        day = Day[raw_day.upper()]
        inputs[day] = sorted(raw_values, key=lambda k: k['value']) if raw_values else []

    timeslots: Timeslots = {}
    # we use the following two variables to keep track of what was the status in the previous iteration
    previous_status: Optional[Status] = None
    opening_timestamp: Optional[int] = None
    # As a week is circular we might have that the first entry on Monday is a Sunday closure time.
    # If this is the case we flag this and we account for it after the main cycle
    starts_monday_closure = False

    # we cannot guarantee that we receive the day of the week in the correct order in the JSON
    # so we need walk tough the week in the correct order.
    # We could sort the dictionary but that would be more expensive.
    for day in WEEK:
        # days where there are no entries are considered as days where the restaurant is closed.
        entries = inputs.get(day, [])
        timeslots[day] = []

        for i, entry in enumerate(entries):
            # Validate the current input and check if we have back to back opening and closing
            try:
                current_status = Status[entry['type'].upper()]
            except ValueError:
                raise ValidationError(f"We expected a weekday, instead we got {entry['type']}")
            if current_status == previous_status:
                raise ValidationError(
                    f"On {(day)} the opening hours have a repeated {previous_status} status")

            if current_status == Status.OPEN:
                opening_timestamp = entry['value']
                day_opening = day
            else:
                # we cannot process this right now as we need the matching opening in Sunday
                if day == Day.MONDAY and i == 0:
                    starts_monday_closure = True
                    continue
                # we do not support closing before opening
                if previous_status is None:
                    raise ValidationError(
                        f"The first status found is a close on {day} without a previous open")

                timeslots[day_opening].append(Timeslot.from_timestamps(opening_timestamp,
                                                                       entry['value']))
                opening_timestamp = None

            previous_status = current_status

    # Deal with the fact that the week is circular so a restaurant might open on Sunday and close on Monday
    if previous_status == Status.OPEN:
        if starts_monday_closure:
            closing_entry = inputs[Day.MONDAY][0]
            timeslots[Day.SUNDAY].append(Timeslot.from_timestamps(opening_timestamp,
                                                                  closing_entry['value']))
        else:
            raise ValidationError("On Sunday the restaurant opened but it never closed")
    elif starts_monday_closure:
        raise ValidationError(
            "The first action on Monday is close but there is no matching opening on Sunday.")

    # As we can have opening and closing that span multiple days with the current implementation
    # we cannot do the string conversions inside the previous loop.
    # As there are only seven days in a week this is not too computationally expensive but we might need to refactor
    # this behavior if the service needs to scale up to massive scale.
    output = {}
    for day in WEEK:
        daily_timeslots = timeslots[day]
        if len(daily_timeslots) == 0:
            output[str(day)] = "Closed"
        else:
            output[str(day)] = ", ".join([str(timeslot) for timeslot in timeslots[day]])
    return output


def _time_to_pretty_string(time_object: time) -> str:
    """
    Cast a time object to string in a pretty format.

    Parameters
    ----------
    time_object : time
        The time object to cast to string

    Returns
    -------
    str
        The pretty string
    """
    if time_object.second != 0:
        pretty_format = "%I:%M:%S %p"
    elif time_object.minute != 0:
        pretty_format = "%I:%M %p"
    elif time_object.minute is not None:
        pretty_format = "%I %p"
    pretty_string = time.strftime(time_object, pretty_format)

    # We do not want leading zero so 09 AM -> 9 AM
    if pretty_string[0] == '0':
        return pretty_string[1:]
    else:
        return pretty_string


def _time_from_timestamp(timestamp: int) -> time:
    """
    Casts a timestamp representing the number of seconds from the midnigh to a time object

    Parameters
    ----------
    timestamp : int
        The number of seconds since midnight

    Returns
    -------
    time
        The associated time object
    """
    SECONDS_IN_MINUTE = 60
    SECONDS_IN_HOUR = 60 * SECONDS_IN_MINUTE

    remaining_time = timestamp
    hour, remaining_time = divmod(remaining_time, SECONDS_IN_HOUR)
    minute, second = divmod(remaining_time, SECONDS_IN_MINUTE)

    return time(hour, minute, second)
