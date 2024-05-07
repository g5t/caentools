import typer
from pathlib import Path
from typing_extensions import Annotated
from dataclasses import dataclass, field


@dataclass
class Numbers:
    values: tuple = field(default_factory=tuple)

    def __iter__(self):
        return iter(self.values)


def parse_numbers(arg: str):
    if '-' in arg and sum('-' == x for x in arg) == 1:
        first, last = [int(x) for x in arg.split('-')]
        return Numbers(tuple(range(first, last + 1)))
    if ',' in arg:
        return Numbers(tuple(int(x) for x in arg.split(',')))
    return Numbers((int(arg), ))


def extract(filename: Path,
            channels: Annotated[Numbers, typer.Argument(parser=parse_numbers)] = '0-15',
            output: Annotated[Path, typer.Option(help='Output, calling directory if None')] = None):
    """
    Extract the comma separated list, dash separated range, or individual channel index(es)
    from the input CAEN '.dat' filename.
    """
    from numpy import round
    from .read import filter_events

    if output is None:
        output = Path()  # the calling working directory

    if output.is_dir():
        base = filename.stem
    else:
        base = output.parts[-1]  # everything following the last directory delimiter
        output = output.parent

    for index in channels:
        channel = filter_events(filename, index)
        file_path = output.joinpath(f'{base}_channel_{index:02d}.txt')
        with file_path.open('w') as file:
            a_array, b_array, x_array = [channel.coords[n].values for n in ('amplitude_a', 'amplitude_b', 'x')]
            for a, b, x in zip(a_array, b_array, x_array):
                ia, ib = [round(z).astype('int') for z in (a, b)]
                file.write(f'{ia:6d}\t{ib:6d}\t{x:16.13f}\n')


def cli_extract():
    typer.run(extract)


if __name__ == '__main__':
    typer.run(extract)
