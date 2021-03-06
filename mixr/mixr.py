import argparse
import datetime

from pydub import AudioSegment
from pydub.playback import play

# Generate a default filename, based on the current datetime.
def get_default_output_name():
    return '{0}.mp3'.format(datetime.datetime.today().strftime('%b-%d-%Y-%H:%M:%S'))

# Create a list of AudioSegments in the order listed in the `playlist` file.
def get_tracks(playlist_path):
    is_file_path = lambda str: bool(str) and str[0] is not '#'
    with open(playlist_path) as f:
        file_list = filter(is_file_path, f.read().split("\n"))
        return [
            AudioSegment.from_mp3(file_path) for file_path in file_list
        ]

# Adjust the volume to match the target gain level.
def normalize(sound, target_dBFS):
    change = target_dBFS - sound.dBFS
    return sound.apply_gain(change)


###############################################################################


parser = argparse.ArgumentParser(
    description='Generate a mix from an M3U playlist.')
parser.add_argument('playlist', metavar='<filename>',
                    help='Path to the playlist file.')
parser.add_argument('--bitrate', metavar='<bitrate=320k>', default='320k',
                    type=str, help='Bitrate of output file')
parser.add_argument('--crossfade', metavar='<seconds=2>', default=2,
                    type=int, help='Crossfade duration (in seconds).')
parser.add_argument('--fade-out', metavar='<seconds=20>', default=20,
                    type=int, help='Fade out duration (in seconds).')
parser.add_argument('--gain', metavar='<dBFS=-10.0>', type=float, default=-10.0,
                    help='Target gain level for mix.')
parser.add_argument('--intro', action='store_const', const=True,
                    help='Intro mode (i.e. don\'t crossfade first track).')
parser.add_argument('--output', metavar='<filename>',
                    default=get_default_output_name(),
                    help='Path to the output file.')


###############################################################################

# Parse arguments and run the program.
def main():
    args = parser.parse_args()

    tracks = get_tracks(args.playlist)
    mix = tracks.pop(0)

    # In intro mode, add the first track without crossfading.
    if args.intro:
        mix = mix.append(tracks.pop(0))

    # Concatenate remaining tracks with specified crossfade duration.
    crossfade_duration = args.crossfade * 1000
    for track in tracks:
        track = normalize(track, args.gain)
        mix = mix.append(track, crossfade=crossfade_duration)

    # Fade the mix out.
    fadeout_duration = args.fade_out * 1000
    mix = mix.fade_out(fadeout_duration)

    # Save the mix as an .mp3 file.
    output = open(args.output, 'wb')
    mix.export(output, format='mp3', bitrate=args.bitrate)
    print('Mix successfully exported as: {0}'.format(args.output))


###############################################################################


if __name__ == "__main__":
    main()
