import argparse
import csv
import pathlib
from dataclasses import dataclass


@dataclass
class Track:
    tracknumber: int = None
    artist: str = None
    title: str = None


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Update a Web MiniDisc Pro toc-csv with titles from a cue-sheet."
    )
    parser.add_argument("--csv", default=None, help="The TOC csv you want to update.")
    parser.add_argument(
        "--cue", default=None, help="The cue you want to read titles from."
    )
    parser.add_argument(
        "--outfile", default="output.csv", help="File to write the result to."
    )

    return parser.parse_args()


def run():
    args = get_arguments()

    tracks = []
    artists = set()
    with pathlib.Path(args.cue).open("r") as cue_fh:
        album_title = ((next(cue_fh)).split(' "')[1]).strip().strip('"')
        while True:
            try:
                line = next(cue_fh)
            except StopIteration:
                break
            t = Track()
            while True:
                if "INDEX " in line:
                    tracks.append(t)
                    t = Track()
                    break

                if "TRACK " in line:
                    track = int(line.split(" ")[3])
                    t.tracknumber = track
                if "TITLE " in line:
                    title = (line.split(' "')[1]).strip().strip('"')
                    t.title = title
                if "SONGWRITER " in line or "PERFORMER " in line:
                    songwriter = (line.split(' "'))[1].strip().strip('"')
                    t.artist = songwriter
                    artists.add(songwriter)

                line = next(cue_fh)

    with open(args.outfile, "w", encoding="utf-8") as csv_output:
        with open(args.csv) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            writer = csv.writer(csv_output, delimiter=",", quoting=csv.QUOTE_MINIMAL)
            header = next(reader)
            writer.writerow(header)
            writer.writerow(next(reader))

            for t, row in zip(tracks, reader):
                row[-4] = t.artist
                row[-5] = album_title
                row[-7] = t.title
                writer.writerow(row)
    print(
        f"Album: {album_title}\nArtist: {artists.pop() if len(artists) == 1 else 'Various'}\nTracks: {len(tracks)}"
    )
    print("Done!")


if __name__ == "__main__":
    run()
