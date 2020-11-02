"""
Convert time expressed in words to time expressed
in the usual way as numbers.
For example: "around five o'clock" --> "16:30-17:30"
Or, as this script currently works only for Hungarian:
"öt óra körül" --> "16:30-17:30"
"""


import argparse
import datetime
import sys


# If we are late not more than CAN_BE_LATE minutes,
# it is considered OK :)
CAN_BE_LATE = 3
# XXX negative numbers can be used for time to get there :)


NUMBER_WORDS = {
    'egy': '1',
    'két': '2',
    'kettő': '2',
    'három': '3',
    'négy': '4',
    'öt': '5',
    'hat': '6',
    'hét': '7',
    'nyolc': '8',
    'kilenc': '9',
    'tíz': '10',
    'tizenegy': '11',
    'tizenkét': '12',
    'tizenkettő': '12'
}

# XXX another variants is needed: 12 hours subtracted if needed
NUMBER = {
    '1': datetime.time(1),
    '2': datetime.time(2),
    '3': datetime.time(3),
    '4': datetime.time(4),
    '5': datetime.time(5),
    '6': datetime.time(6),
    '7': datetime.time(7),
    '8': datetime.time(8),
    '9': datetime.time(9),
    '10': datetime.time(10),
    '11': datetime.time(11),
    '12': datetime.time(12)
}


def add_to_time(start_time, minutes):
    """Add some minutes to a time object."""
    # arithmetic is not supported for datetime.time() objects
    # https://stackoverflow.com/questions/14043934
    start = datetime.datetime.combine(datetime.date.today(), start_time)
    stop = start + datetime.timedelta(minutes=minutes)
    stop_time = stop.time()
    return stop_time


def round_to_quarter(dt):
    """
    Calculate which quarter hour we are in: 0 / 15 / 30 / 45
    Return a modified datetime object.
    Quarter (15 minutes) is the basic time unit.
    CAN_BE_LATE is taken into account.
    """
    quarter = ((dt.minute + 14 - CAN_BE_LATE) // 15) * 15

    rhour = dt.hour
    rminute = quarter

    if quarter == 60:
        # XXX day change is not handled, but should be! :)
        # XXX cf. christmas midnight mass
        rhour += 1
        rminute = 0

    return datetime.datetime(
        dt.year, dt.month, dt.day, rhour, rminute)


def number_or_number_word(text):
    """Handle numbers and number_words as well."""
    # 1, 2 ...
    if text in NUMBER:
        return NUMBER[text]
    # egy, kettő ...
    if text in NUMBER_WORDS:
        return NUMBER[NUMBER_WORDS[text]]
    # otherwise
    return None


def when_interval(text):
    """Take time as text. Return a time interval."""
    onow = datetime.datetime.now()
    ohour = onow.hour
    ominute = onow.minute

    now = round_to_quarter(onow)
    hour = now.hour
    minute = now.minute

    # business logic -- how to make it simpler? :)

    # -- preprocessing
    text = text.lower()

    # -- specific cases
    # "X / X-es / X órakor / Xkor / X-kor"
    for pattern in ['', ' órakor', 'kor', '-kor']: # XXX tok?
        # XXX is there a better idea than replace('', '')?

        tmp = text.replace(pattern, '')
        res = number_or_number_word(tmp)
        if res is not None:
            return res, res

    # "X körül"
    tmp = text.replace(' körül', '') # XXX tok?
    res = number_or_number_word(tmp)
    if res is not None:
        return add_to_time(res, -30), add_to_time(res, 30)

    # "X előtt"
    tmp = text.replace(' előtt', '') # XXX tok?
    res = number_or_number_word(tmp)
    if res is not None:
        return datetime.time(0), add_to_time(res, -15)

    # "X után"
    tmp = text.replace(' után', '') # XXX tok?
    res = number_or_number_word(tmp)
    if res is not None:
        # XXX day change? how?
        return add_to_time(res, 15), datetime.time(23, 59)

    # "most"
    if text in ["most", "mostanában"]:
        return now.time(), now.time()

    # "reggel"
    if text == "reggel":
        return datetime.time(0), datetime.time(10)

    # "délben"
    if text == "délben":
        return datetime.time(11), datetime.time(13)

    # "este"
    if text == "este":
        return datetime.time(17), datetime.time(23, 59)

    # "X óra múlva" (körül!) # XXX körül dupl!!!
    tmp = text.replace(' óra múlva', '') # XXX tok?
    res = number_or_number_word(tmp)
    if res is not None:
        cen = add_to_time(now.time(), res.hour * 60)
        return add_to_time(cen, -15), add_to_time(cen, 15)

    # "X órán belül"
    tmp = text.replace(' órán belül', '') # XXX tok?
    res = number_or_number_word(tmp)
    if res is not None:
        return now.time(), add_to_time(now.time(), res.hour * 60)

    # -- finally if there is no better tip then: now
    return now.time(), now.time()
    # XXX a message linke "NOIDEA!" is needed somehow


def when(text):
    """Take time as text. Return time as numbers (in a string)."""
    beg, end = when_interval(text)

    if beg == end:
        beg_str = beg.strftime('%H:%M')
        return f'{beg_str}'
    else:
        beg_str = beg.strftime('%H:%M')
        end_str = end.strftime('%H:%M')
        return f'{beg_str}-{end_str}'


def main():
    """Test when() with some examples."""
    # get CLI arguments
    args = get_args()

    # XXX 1. hardcoded examples
    tests = ['5', '5-kor', '5 előtt', 'hat körül', 'két óra múlva']
    for text in tests:
        print(f'"{text}"')
        print(when(text))

    # XXX 2. examples from stdin
    for line in sys.stdin:
        text = line.strip()
        print(when(text))


def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    #parser.add_argument(
    #    '--smiley', '-s',
    #    help='add smiley',
    #    type=str,
    #    default=':)')
    
    return parser.parse_args()


if __name__ == '__main__':
    main()
