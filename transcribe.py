"""Monophonic audio -> MIDI (and optional MusicXML) transcription.

Pipeline:
    1. load + normalise + trim silence
    2. frame-wise f0 with probabilistic YIN (pYIN), which also gives a voiced/unvoiced flag
    3. quantise f0 to MIDI pitches, median-filter to remove single-frame glitches
    4. merge consecutive frames of the same pitch into notes, drop notes shorter than
       ``min_note_s``
    5. write a MIDI file (and optionally a MusicXML score)

Usage:
    python transcribe.py song.wav                       # -> song.mid
    python transcribe.py song.mp3 -o out.mid --xml out.musicxml --program 73
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HOP_LENGTH = 512


@dataclass(frozen=True)
class Note:
    pitch: int      # MIDI note number
    start: float    # seconds
    end: float      # seconds

    @property
    def duration(self) -> float:
        return self.end - self.start


def track_pitch(
    y: np.ndarray, sr: int, fmin: str = "C2", fmax: str = "C7", hop_length: int = HOP_LENGTH
) -> tuple[np.ndarray, np.ndarray]:
    """Return per-frame MIDI pitch (NaN where unvoiced) and frame times in seconds."""
    import librosa

    f0, voiced, _ = librosa.pyin(
        y, fmin=librosa.note_to_hz(fmin), fmax=librosa.note_to_hz(fmax), sr=sr,
        hop_length=hop_length,
    )
    f0 = np.where(voiced & np.isfinite(f0) & (f0 > 0), f0, np.nan)
    midi = np.full_like(f0, np.nan)
    ok = ~np.isnan(f0)
    midi[ok] = np.round(librosa.hz_to_midi(f0[ok]))
    times = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=hop_length)
    return midi, times


def _median_filter(midi: np.ndarray, size: int) -> np.ndarray:
    """Median filter that treats unvoiced frames (NaN) as their own value (-1)."""
    if size <= 1:
        return midi
    filled = np.where(np.isnan(midi), -1.0, midi)
    pad = size // 2
    padded = np.pad(filled, pad, mode="edge")
    windows = np.lib.stride_tricks.sliding_window_view(padded, size)
    out = np.median(windows, axis=1)
    out = np.round(out)
    return np.where(out < 0, np.nan, out)


def frames_to_notes(
    midi: np.ndarray, frame_period: float, min_note_s: float = 0.08, smooth: int = 5
) -> list[Note]:
    """Group consecutive frames with the same pitch into notes."""
    midi = _median_filter(np.asarray(midi, dtype=float), smooth)
    notes: list[Note] = []
    start = None
    current = None
    for i, p in enumerate(np.append(midi, np.nan)):  # sentinel closes the last note
        same = current is not None and not np.isnan(p) and p == current
        if same:
            continue
        if current is not None:
            note = Note(int(current), start * frame_period, i * frame_period)
            if note.duration >= min_note_s:
                notes.append(note)
        current, start = (None, None) if np.isnan(p) else (p, i)
    return [n for n in notes if 0 <= n.pitch <= 127]


def transcribe(audio_path: str | Path, min_note_s: float = 0.08) -> list[Note]:
    """Transcribe a monophonic recording into a list of notes."""
    import librosa

    y, sr = librosa.load(str(audio_path), sr=22050, mono=True)
    y = librosa.util.normalize(y)
    y, _ = librosa.effects.trim(y, top_db=30)
    midi, _ = track_pitch(y, sr)
    return frames_to_notes(midi, HOP_LENGTH / sr, min_note_s=min_note_s)


def write_midi(notes: list[Note], path: str | Path, program: int = 0, velocity: int = 100) -> None:
    import pretty_midi

    pm = pretty_midi.PrettyMIDI()
    inst = pretty_midi.Instrument(program=program)
    inst.notes.extend(
        pretty_midi.Note(velocity=velocity, pitch=n.pitch, start=n.start, end=n.end) for n in notes
    )
    pm.instruments.append(inst)
    pm.write(str(path))


def write_musicxml(notes: list[Note], path: str | Path, bpm: float = 120.0) -> None:
    """Write a simple score: durations quantised to 16th notes, gaps become rests."""
    from music21 import meter, note, stream, tempo

    beat = 60.0 / bpm
    quant = 0.25  # quarter-length of a 16th note

    def ql(seconds: float) -> float:
        return max(quant, round(seconds / beat / quant) * quant)

    part = stream.Part()
    part.append(tempo.MetronomeMark(number=bpm))
    part.append(meter.TimeSignature("4/4"))
    cursor = 0.0
    for n in notes:
        if n.start - cursor >= beat * quant:
            part.append(note.Rest(quarterLength=ql(n.start - cursor)))
        m = note.Note(n.pitch)
        m.quarterLength = ql(n.duration)
        part.append(m)
        cursor = n.end
    part.write("musicxml", fp=str(path))


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("audio", help="Input audio file (wav, mp3, flac, ...)")
    p.add_argument("-o", "--output", help="Output MIDI path (default: <audio>.mid)")
    p.add_argument("--xml", help="Also write a MusicXML score to this path")
    p.add_argument("--program", type=int, default=0, help="General MIDI program (0 = piano)")
    p.add_argument("--min-note", type=float, default=0.08, help="Shortest note to keep, in seconds")
    p.add_argument("--bpm", type=float, default=120.0, help="Tempo used for the MusicXML score")
    args = p.parse_args(argv)

    notes = transcribe(args.audio, min_note_s=args.min_note)
    out = Path(args.output or Path(args.audio).with_suffix(".mid"))
    write_midi(notes, out, program=args.program)
    print(f"Transcribed {len(notes)} notes -> {out}")
    if args.xml:
        write_musicxml(notes, args.xml, bpm=args.bpm)
        print(f"Score -> {args.xml}")


if __name__ == "__main__":
    main()
