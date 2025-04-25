"""
Skyfield와 같은 상위 수준 라이브러리는 일반적으로 자신의 날짜와 시간을 처리. 
하지만 이 라이브러리를 사용하는 사람들에게는 그 자체로는 기본 Python 날짜/시간 처리가 편리할 수 있음음.

"""

import datetime as dt
from math import pi
from orbit_determination.functions import days2mdhms, jday

class _UTC(dt.tzinfo):
    'UTC'
    zero = dt.timedelta(0)
    def __repr__(self):
        return 'UTC'
    def dst(self, datetime):
        return self.zero
    def tzname(self, datetime):
        return 'UTC'
    def utcoffset(self, datetime):
        return self.zero

UTC = _UTC()

def jday_datetime(dt):
    
    year, month, day = dt.year, dt.month, dt.day
    hour, minute, second = dt.hour, dt.minute, dt.second + dt.microsecond / 1e6

    jd = (367.0 * year
        - int((7 * (year + int((month + 9) / 12.0))) * 0.25)
        + int(275 * month / 9.0)
        + day + 1721013.5)

    fr = (second + minute * 60.0 + hour * 3600.0) / 86400.0

    return jd, fr

def sat_epoch_datetime(sat):
    """주어진 위성의 epoch를 Python에에 날짜/시간으로 반환"""
    year = sat.epochyr
    year += 1900 + (year < 57) * 100
    days = sat.epochdays
    month, day, hour, minute, second = days2mdhms(year, days)
    if month == 12 and day > 31:  
        year += 1
        month = 1
        day -= 31
    second, fraction = divmod(second, 1.0)
    second = int(second)
    micro = int(fraction * 1e6)
    return dt.datetime(year, month, day, hour, minute, second, micro, UTC)

_ATTRIBUTES = []
_ATTR_MAXES = {}
_MAX_VALUES = {'2pi': 2*pi, 'pi': pi}

def _load_attributes():
    for line in sgp4.__doc__.splitlines():
        if line.endswith('*'):
            title = line.strip('*')
            _ATTRIBUTES.append(title)
        elif line.startswith('| ``'):
            pieces = line.split('``')
            name = pieces[1]
            _ATTRIBUTES.append(name)
            i = 2
            while pieces[i] == ', ':
                another_name = pieces[i+1]
                _ATTRIBUTES.append(another_name)
                i += 2
            if '<' in line:
                _ATTR_MAXES[name] = '2pi' if ('2pi' in line) else 'pi'

def check_satrec(sat):
    """Check whether satellite orbital elements are within range."""

    if not _ATTRIBUTES:
        _load_attributes()

    e = []

    for name, max_name in sorted(_ATTR_MAXES.items()):
        value = getattr(sat, name)
        if 0.0 <= value < _MAX_VALUES[max_name]:
            continue
        e.append('  {0} = {1:f} is outside the range 0 <= {0} < {2}\n'
                 .format(name, value, max_name))

    if e:
        raise ValueError('satellite parameters out of range:\n' + '\n'.join(e))


def dump_satrec(sat, sat2=None):
    """Yield lines that list the attributes of one or two satellites."""

    if not _ATTRIBUTES:
        _load_attributes()

    for item in _ATTRIBUTES:
        if item[0].isupper():
            title = item
            yield '\n'
            yield '# -------- {0} --------\n'.format(title)
        else:
            name = item
            value = getattr(sat, item, '(not set)')
            line = '{0} = {1!r}\n'.format(item, value)
            if sat2 is not None:
                value2 = getattr(sat2, name, '(not set)')
                verdict = '==' if (value == value2) else '!='
                line = '{0:39} {1} {2!r}\n'.format(line[:-1], verdict, value2)
            yield line
