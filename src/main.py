from pathlib import Path

from config import Config
from tvpfile import TVPFile


def main():
    Config.load()

    p = Path()
    for file in p.glob('*.tvp'):
        tvp = TVPFile(file)
        tvp.read()
        print(tvp.bpm_events)


if __name__ == '__main__':
    main()