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

    
        

if __name__ == '__main__':
    main()