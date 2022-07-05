import json
import logging
from pathlib import Path

import click

from viurtotech.techfile import TechFile
from viurtotech.tvpfile import TVPFile


logger = logging.getLogger(__name__)
logging.basicConfig(filename='test.log', filemode='wt', level=logging.DEBUG)


@click.command()
@click.option('-p', '--path', 'filepath', default='.',
    help='Specify the path to look for the .tvp files')
def main(filepath: str):
    # find tvp files in the directory
    p = Path(filepath)
    tvpfiles = [TVPFile(file) for file in p.glob('*.tvp')]
    if len(tvpfiles) == 0:
        click.secho('No .tvp files found.', err=True, fg='red')
        return

    message = f'{len(tvpfiles)} file(s) found: {", ".join(f.path.name for f in tvpfiles)}'
    click.echo(message)

    for file in tvpfiles:
        read_and_convert(file)

    # use the first file for the track's metadata
    tech = TechFile(tvpfiles[0])
    for file in tvpfiles:
        tech.add_pattern(file)
    
    with open('track.tech', 'wt') as f:
        json.dump(vars(tech), f, indent='\t')

    print('Done!')


def read_and_convert(file: TVPFile):
    file.read('metadata')

    # ask for the desired bps since in viur it can only be 4 or 8
    # more details in README file
    while not hasattr(file, 'bps'):
        msg = ''.join((
            f'Enter the bps desired for "{file.path.name}". ',
            f'Leave blank to keep the original value ({file.orig_bps}).\n'
            ))
        inp: int = click.prompt(msg, type=int, default=file.orig_bps, show_default=False)
        if inp < 1:
            click.secho('Error: bps must be at least 1.', err=True, fg='red')
        else:
            file.bps = inp

    file.read('bpm', 'note')
    file.convert_notes()


if __name__ == '__main__':
    main()
