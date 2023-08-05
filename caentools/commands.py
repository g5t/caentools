def parse_extract():
    from argparse import ArgumentParser
    from pathlib import Path
    from os import R_OK, access

    def readable(arg):
        if not isinstance(arg, Path):
            arg = Path(arg)
        arg = arg.resolve()
        if not arg.exists():
            raise RuntimeError(f'{arg} does not exist')
        if not arg.is_file():
            raise RuntimeError(f'{arg} is not a file')
        if not access(arg, R_OK):
            raise RuntimeError(f'{arg} is not readable')
        return arg

    def numbers(arg):
        if '-' in arg and sum('-' == x for x in arg) == 1:
            min, max = [int(x) for x in arg.split('-')]
            return range(min, max+1)
        if ',' in arg:
            return [int(x) for x in arg.split(',')]
        return [int(arg)]

    parser = ArgumentParser(description='Extract one or more channels from a binary CAEN .dat file')
    parser.add_argument('filename', type=readable, help='The filename to extract from')
    parser.add_argument('-c', '--channels', type=numbers, default=range(15),
                        help='The zero-based channel indexes to extract, e.g., 0-5 or 4,3,8,9')
    parser.add_argument('-o', type=str, default=None, help='The output file prefix')

    args = parser.parse_args()
    return args


def extract():
    from numpy import round
    from .read import filter_events
    args = parse_extract()

    output = args.filename.stem if args.output is None else args.output

    for index in args.channels:
        channel = filter_events(args.filename, index)
        with open(f'{output}_channel_{index:02d}.txt', 'w') as file:
            a_array, b_array, x_array = [channel.coords[n].values for n in ('amplitude_a', 'amplitude_b', 'x')]
            for a, b, x in zip(a_array, b_array, x_array):
                ia, ib = [round(z).astype('int') for z in (a, b)]
                file.write(f'{ia:6d}\t{ib:6d}\t{x:16.13f}\n')

