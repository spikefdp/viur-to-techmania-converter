from pathlib import Path

from config import Config
from tvpfile import TVPFile


def main():
    Config.load()

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
        file.read()

        # ask for the desired bps since in viur it can only be 4 or 8
        looping = True
        while looping:
            inp = input(f'Enter the bps desired for "{file.path.name}". ' +
                f'Leave blank to keep the original value ({file.bps}).\n')
            if inp:
                try:
                    int(inp)
                except ValueError:
                    print('Error. Please enter an integer.')
                else:
                    looping = False
            else:
                looping = False
        file.bps = inp



if __name__ == '__main__':
    main()