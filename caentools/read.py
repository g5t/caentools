def read_dat(filename):
    """Read packed binary data of the form used for BIFROST detector tests
    
    Actually-found layout from LLB detector tests
    struct raw_data_t {
      uint32_t TimeHi;
      uint32_t TimeLo;
      uint16_t unused16;
      uint8_t TubeCh;
      uint8_t IDnFlags;
      uint16_t AmplA;
      uint16_t AmplB;
      uint32_t unused32;
    } __attribute__((__packed__));
    """
    from numpy import fromfile, uint32, uint16, uint8
    dtype = [('time_high', uint32), ('time_low', uint32),
             ('unused_16', uint16), ('tube_channel', uint8),
             ('id_flags', uint8),
             ('amplitude_a', uint16), ('amplitude_b', uint16),
             ('unused_32', uint32)]
    return fromfile(filename, dtype=dtype)


def read_scipp(filename, clock=None, sort=True, channel=None):
    from scipp import array, DataArray, ones_like
    if clock is None:
        clock = 1.25e8  # 125 MHz CPU clock, 25 MHz internal clock oscillator

    dat = read_dat(filename)
    # concatenate the two 32-bit time-words, divide by the clock frequency to get seconds
    th = dat['time_high'].astype('int') << 32
    tl = dat['time_low'].astype('int')
    time = (th + tl) / clock  
    time = array(values=time, dims=['event'], unit='sec')
    chan = array(values=dat['tube_channel'].astype('int'), dims=['event'])
    ampl_a = array(values=1.0 * dat['amplitude_a'].astype('int'), dims=['event'], unit='mV')
    ampl_b = array(values=1.0 * dat['amplitude_b'].astype('int'), dims=['event'], unit='mV')
    
    if channel:
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
