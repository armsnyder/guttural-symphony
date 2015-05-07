__author__ = 'Adam Snyder'

import wave
import struct
import random
import sys


def main():
    print "Reading wav file..."
    wav_array, sr = get_wav_array(sys.argv[1])
    if len(sys.argv) > 3:
        spacing = int(sys.argv[3])
    else:
        spacing = 400
    min_dist = 0.001*sr
    print "Finding audio peaks..."
    peaks = get_peaks(wav_array, spacing, min_dist)
    print "Generating output..."
    out = build_output(wav_array, peaks, sr)
    print "Writing output to wav..."
    write_wav(sys.argv[2], out, sr)


def get_wav_array(filename):
    p = wave.open(filename, 'r')
    nchannels, sampwidth, sr, nframes, comptype, compname = p.getparams()
    frames = p.readframes(nframes * nchannels)
    return struct.unpack_from("%dh" % nframes * nchannels, frames), sr


def get_peaks(wav_array, spacing, min_dist):
    peaks = []
    for i in range(len(wav_array)/spacing*2):
        peaks_seg = []
        for j in range(i*spacing/2, (i+2)*spacing/2):
            if j > len(wav_array)-1:
                continue
            try:
                if len(peaks_seg):
                    last_seg = peaks_seg[-1]
                else:
                    last_seg = -1000
                if wav_array[j] > 0 and j-last_seg > min_dist \
                        and wav_array[j-1] < wav_array[j] and wav_array[j+1] < wav_array[j]:
                    peaks_seg.append(j)
            except IndexError:
                pass
        try:
            peaks.append(sorted(peaks_seg, key=lambda x: wav_array[x], reverse=True)[0])
        except IndexError:
            pass
    peaks = sorted(set(peaks))
    peak_starts = []
    for peak in peaks:
        while wav_array[peak] > 0 and peak > 0:
            peak -= 1
        peak_starts.append(peak+1)
    return peak_starts


def build_output(wav_array, peak_starts, sr):
    out = []
    distance = 0.1*sr
    variance = 30
    direction = 0
    direction_limit = 200
    if len(sys.argv) > 4:
        min_dist = int(sys.argv[4])
    else:
        min_dist = variance
    if len(sys.argv) > 5:
        max_dist = int(sys.argv[5])
    else:
        max_dist = sr
    for i in range(len(peak_starts)):
        distance += random.random()*variance*2-variance + direction
        direction += random.random()*variance*2-variance
        if distance < min_dist:
            distance = min_dist
        if distance > max_dist:
            distance = max_dist
            direction = 0
        if abs(direction) > direction_limit:
            direction /= -2
        try:
            out.extend(make_sound_array(wav_array[peak_starts[i]:peak_starts[i+1]], random.randint(0, 2)))
            out.extend([0]*int(distance)*2)
        except IndexError:
            pass
        # print distance, direction
    return out


def make_sound_array(sound, channel):
    result = []
    if channel == 0:
        for thing in sound:
            result.append(0)
            result.append(thing)
    elif channel == 1:
        for thing in sound:
            result.append(thing)
            result.append(thing)
    else:
        for thing in sound:
            result.append(thing)
            result.append(0)
    return result


def write_wav(filename, out, sr):
    noise_output = wave.open(filename, 'w')
    noise_output.setparams((2, 2, sr, 0, 'NONE', 'not compressed'))

    values = []

    for i in range(len(out)):
        value = out[i]
        packed_value = struct.pack('h', value)
        values.append(packed_value)

    value_str = ''.join(values)
    noise_output.writeframes(value_str)
    noise_output.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: guttural_symphony.py <path-to-sound-file-input> <path-to-sound-file-output> ' \
              '[average-sample-distance] [min-silence-samples] [max-silence-samples]'
    else:
        main()