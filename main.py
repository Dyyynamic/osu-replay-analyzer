import argparse
from replay import Replay


if __name__ == "__main__":
    # Parse arguments
    formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=50)
    parser = argparse.ArgumentParser(formatter_class=formatter)
    parser.add_argument("file", help="osu! replay file to parse")
    parser.add_argument(
        "-d",
        "--decimals",
        metavar="int",
        type=int,
        default=2,
        help="the amount of decimals of the output",
    )
    args = parser.parse_args()

    replay = Replay(args.file)

    modList = replay.get_mod_list()
    mods = " +" + "".join(modList) if modList else ""

    format = lambda number: "{:.{d}f}".format(number, d=args.decimals)

    # Print replay information
    print(f"{replay.name} | {replay.beatmap['artist']} - {replay.beatmap['title']} [{replay.beatmap['version']}]{mods} ({format(replay.sr)}★)")
    print(f"Score: {'{:,}'.format(replay.score)}")
    print(f"Accuracy: {format(replay.calculate_accuracy())}%")
    print(f"MA Ratio: {format(replay.calculate_ma())}:1")
    print(f"PP: {format(replay.pp)}")
