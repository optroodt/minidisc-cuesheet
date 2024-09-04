import argparse
import pathlib


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Create a cue sheet from a pipe (|) separated values file. The columns in the PSV file are track number, title, artist, track length (mm:ss)."
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Txt file you want to read from. (pipe separated values",
    )
    parser.add_argument(
        "--outfile", default="output.cue", help="File you want to write the result to"
    )
    parser.add_argument("--artist", default="Default artist")
    parser.add_argument("--title", default="Default title")
    parser.add_argument("--audio-file", default="default.wav")

    return parser.parse_args()


def timestring_to_frames(input_time):
    minutes, seconds = map(int, input_time.split(":"))

    framecount = 37  # start halfway, because I only have up to the second accuracy

    framecount += seconds * 75
    framecount += minutes * 75 * 60
    return framecount


def frames_to_time(input_frames):
    minutes = input_frames // (75 * 60)
    seconds = (input_frames - (minutes * 60 * 75)) // 75
    frames = input_frames % 75
    return minutes, seconds, frames


def frames_to_timestring(input_frames):
    minutes, seconds, frames = frames_to_time(input_frames)
    return f"{minutes:02}:{seconds:02}:{frames:02}"


def run():
    args = get_arguments()
    album_artist = args.artist  # "White Panda"
    album_title = args.title  # "Nightclub"
    album_file = (
        args.audio_file
    )  # "/Users/optroodt/Downloads/White Panda - Nightcub (Continuous Mix)/White Panda - Nightcub (Continuous Mix) - 01 Nightcub (Continuous Mix).wav"
    p = pathlib.Path(args.file)
    outfile = pathlib.Path(args.outfile)
    framecounter = 0

    with outfile.open("w") as output_fh:
        output_fh.write(f'PERFORMER "{album_artist}"\n')
        output_fh.write(f'TITLE "{album_title}"\n')
        output_fh.write(f'FILE "{album_file}" WAVE\n')
        with p.open("r") as fh:
            for i, line in enumerate(fh.readlines()):
                tracknumber, title, artist, time = line.strip().split("|")

                output_fh.write(f"  TRACK {int(tracknumber):02} AUDIO\n")
                output_fh.write(f'    PERFORMER "{artist}"\n')
                output_fh.write(f'    TITLE "{title}"\n')
                output_fh.write(f"    INDEX 01 {frames_to_timestring(framecounter)}\n")

                framecounter += timestring_to_frames(time)


if __name__ == "__main__":
    run()
