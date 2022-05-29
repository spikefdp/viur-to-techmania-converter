from pathlib import Path

import click

from viurtotech.tvpfile import TVPFile


@click.command()
def main():
    # find tvp files in the directory
    p = Path()
    inputfiles = [TVPFile(file) for file in p.glob('*.tvp')]
    if len(inputfiles) == 0:
        print('No .tvp files found.')
        return

    message = f'{len(inputfiles)} file(s) found: '
    for i, file in enumerate(inputfiles):
        if i > 0:
            message += ', '
        message += file.path.name
    print(message)

    for file in inputfiles:
        file.read('metadata')

        # ask for the desired bps since in viur it can only be 4 or 8
        while file.targ_bps is None:
            inp = input(
                f'Enter the bps desired for "{file.path.name}". ' +
                f'Leave blank to keep the original value ({file.orig_bps}).\n'
                )
            if inp:
                try:
                    inp = int(inp)
                except ValueError:
                    click.secho('Error. Please enter an integer.', err=True, fg='red')
                    continue
                
                if inp < 1:
                    click.secho('Error. bps must be at least 1.', err=True, fg='red')
                else:
                    file.targ_bps = inp
            else:
                file.targ_bps = file.orig_bps

        print(file.targ_bps)



if __name__ == '__main__':
    main()
