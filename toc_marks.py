import argparse
import re
import shutil
from pathlib import Path

import bitstring

"""
Adapted from https://github.com/Havrevoll/md
"""


def read_cuefile(cuefile) -> list[float]:
    track_marks: list[float] = []
    with open(cuefile) as f:
        for i, l in enumerate(f):
            minutes, seconds, frames = re.split(r"[:\.]", l)
            if i == 0:
                # if the first line is not 00:00.00, we're missing the first track, so insert it
                if minutes != "00" and seconds != "00" and frames != "00":
                    track_marks.append(float(0))
            track_marks.append(int(minutes) * 60 + int(seconds) + int(frames) / 75)
    return track_marks


def convert(gr):
    cluster = gr // (32 * 11)
    gr %= 32 * 11
    sector = gr // 11
    gr %= 11

    return (cluster, sector, gr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cuefile", nargs="?")
    parser.add_argument("binfile", nargs="?")
    # parser.add_argument("outfile", nargs='?')
    args = parser.parse_args()

    seconds = read_cuefile(Path(args.cuefile))
    groups = [round(a * 88200 / 512) for a in seconds]
    start = [convert(a + 17600) for a in groups]
    end = [convert(a + 17600 - 1) for a in groups[1:]]
    end.append((0, 0, 0))

    start_enc = [
        bitstring.BitArray("0b" + f"{a[0]:014b}" + f"{a[1]:06b}" + f"{a[2]:04b}").bytes
        for a in start
    ]
    end_enc = [
        bitstring.BitArray("0b" + f"{a[0]:014b}" + f"{a[1]:06b}" + f"{a[2]:04b}").bytes
        for a in end
    ]

    for i in range(10):
        backupfile = Path(args.binfile + ".bak" + str(i)).absolute()
        if not backupfile.exists():
            shutil.copy2(Path(args.binfile).absolute(), backupfile)
            break

    with open(Path(args.binfile), "r+b") as f:

        f.seek(0x30)  # Find location of freemap
        freemap = f.read(1)

        f.seek(0x13B)
        code = f.read(
            1
        )  # Read the type of track. Will be 0xA6 if it is SP stereo, 0xA2 if it is LP2.

        f.seek(0x13C)  # Find location of end of track
        end_enc[-1] = f.read(3)

        f.seek(0x1F)  # Write new number of tracks
        f.write(len(end_enc).to_bytes(1, byteorder="big"))

        f.seek(0x31)  # Write links to track fragment map, 1 to number of tracks
        f.write(bytes(range(1, len(start_enc) + 1)))
        # start_pos = 0x130
        l = b""
        track = b""
        for a, b in zip(start_enc, end_enc):
            l = l + a + code + b + bytes.fromhex("00")  # Create track fragment map
            track = (
                track
                + bytes.fromhex("00") * 6
                + bytes.fromhex("01")
                + bytes.fromhex("20")
            )  # Create timestamps map

        f.seek(0x2F)
        if not int.from_bytes(f.read(1), byteorder="big") == 255:
            f.seek(0x2F)  # Write next free track, which is number of tracks + 1
            f.write((len(end_enc) + 1).to_bytes(1, byteorder="big"))

        f.seek(0x138)  # Write the track fragment map
        f.write(l)

        f.seek(0x128F)  # Write next free timestamp slot, should be unnecessary.
        f.write((len(end_enc) + 1).to_bytes(1, byteorder="big"))

        f.seek(0x1290)  # Write track junction map, should be unnecessary.
        f.write(bytes(range(len(start_enc))))

        f.seek(0x1390)  # Write timestamps map, should be unnecessary.
        f.write(track)
