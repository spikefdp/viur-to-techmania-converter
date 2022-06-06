import logging
from pathlib import Path

import click
# import click_log

from viurtotech.tvpfile import TVPFile


logger = logging.getLogger(__name__)
logging.basicConfig(filename='test.log', filemode='wt', level=logging.DEBUG)
# click_log.basic_config(logger)


@click.command()
@click.option('-p', '--path', 'inppath', default='.',
    help='Specify the path to look for the .tvp files')
# @click_log.simple_verbosity_option(logger)
def main(inppath: str):
    # find tvp files in the directory
    p = Path(inppath)
    inpfiles = [TVPFile(file) for file in p.glob('*.tvp')]
    if len(inpfiles) == 0:
        click.secho('No .tvp files found.', err=True, fg='red')
        return

    message = f'{len(inpfiles)} file(s) found: '
    for i, file in enumerate(inpfiles):
        if i > 0:
            message += ', '
        message += file.path.name
    click.echo(message)

    for file in inpfiles:
        file.read('metadata')

        # ask for the desired bps since in viur it can only be 4 or 8
        # more details in README file
        while file.bps is None:
            inp = click.prompt(
                f'Enter the bps desired for "{file.path.name}". ' +
                f'Leave blank to keep the original value ({file.orig_bps}).\n',
                type=int, default=file.orig_bps, show_default=False)
            if inp < 1:
                click.secho('Error: bps must be at least 1.', err=True, fg='red')
            else:
                file.bps = inp

        file.read('bpm', 'note')

        logger.info(file.notes)

        file.convert_notes()

        logger.info(file.tech_holds)



if __name__ == '__main__':
    main()
