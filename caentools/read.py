from datetime import datetime


def datatype(pivot: datetime | None = None):
    from numpy import uint32, uint16, uint8
    if pivot is None:
        pivot = datetime.now()
    if not isinstance(pivot, datetime):
        raise ValueError("Input should be a valid datetime")
    # only two (known) formats for CAEN firmware, with minor differences
    dtype = [('time_high', uint32), ('time_low', uint32)]

    if pivot.year < 2024 or (pivot.year == 2024 and pivot.month <= 9):
        dtype.extend([('unused_16', uint16), ('group', uint8), ('id_flags', uint8)])
    else:
        dtype.extend([('flags_om', uint8), ('group', uint8), ('unused_16', uint16)])
    
    for x in ('a', 'b', 'c', 'd'):
        dtype.append((f'amplitude_{x}', 'uint16'))

    return dtype


def file_creation_datetime(filename):
    import os
    try:
        return datetime.fromtimestamp(os.path.getctime(filename))
    except Exception as ex:
        return None


def read_dat(filename, pivot: datetime | None = None):
    """Read packed binary data from CAEN instrumetns"""
    from numpy import fromfile
    dtype = datatype(file_creation_datetime(filename) if pivot is None else pivot)
    return fromfile(filename, dtype=dtype)


def read_scipp(filename, clock=None, sort=True, channel=None, pivot: datetime | None = None):
    from scipp import array, DataArray, ones_like
    if clock is None:
        clock = 1.25e8  # 125 MHz CPU clock, 25 MHz internal clock oscillator

    dat = read_dat(filename, pivot=pivot)
    # concatenate the two 32-bit time-words, divide by the clock frequency to get seconds
    time = array(values=(dat['time_high'].astype('int') * 2**32 + dat['time_low'].astype('int')) / clock,
                 dims=['event'], unit='sec')
    chan = array(values=dat['group'].astype('int'), dims=['event'])
    ampl_a = array(values=1.0 * dat['amplitude_a'].astype('int'), dims=['event'], unit='mV')
    ampl_b = array(values=1.0 * dat['amplitude_b'].astype('int'), dims=['event'], unit='mV')
    
    if channel is not None:
        keep = chan == channel
        chan, ampl_a, ampl_b, time = [da[keep] for da in (chan, ampl_a, ampl_b, time)]
    
    ab = ampl_a + ampl_b
    rx = ampl_a - ampl_b

    events = ones_like(1. * chan)
    events.unit = 'counts'

    coordinates = {
        'x': rx / ab,
        'time': time,
        'channel': chan,
        'amplitude_a': ampl_a,
        'amplitude_b': ampl_b,
        'ab': ab,
        'rx': rx
    }
    data = DataArray(data=events, coords=coordinates)
    if sort:
        from scipp import sort as ss
        data = ss(data, 'time')
        
    return data


def filter_events(filename, channel, **kwargs):
    return read_scipp(filename, channel=channel, **kwargs)
