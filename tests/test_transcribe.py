import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from transcribe import Note, frames_to_notes, transcribe, write_midi, write_musicxml  # noqa: E402

SR = 22050


def tone(freq: float, seconds: float) -> np.ndarray:
    t = np.arange(int(SR * seconds)) / SR
    return 0.5 * np.sin(2 * np.pi * freq * t)


def test_frames_to_notes_merges_and_filters():
    nan = np.nan
    frames = np.array([60] * 10 + [nan] * 4 + [62] * 10 + [64] * 1 + [62] * 3, dtype=float)
    notes = frames_to_notes(frames, frame_period=0.02, min_note_s=0.05, smooth=3)
    assert [n.pitch for n in notes] == [60, 62]   # 1-frame glitch removed, silence is a gap
    assert notes[0].start == 0.0
    assert notes[1].start > notes[0].end


def test_silence_produces_no_notes():
    assert frames_to_notes(np.full(50, np.nan), 0.02) == []


def test_transcribe_two_tones(tmp_path):
    audio = np.concatenate([tone(440.0, 0.6), np.zeros(SR // 5), tone(523.25, 0.6)])
    wav = tmp_path / "a.wav"
    sf.write(wav, audio, SR)
    notes = transcribe(wav)
    assert [n.pitch for n in notes] == [69, 72]   # A4, C5


def test_writers(tmp_path):
    import pretty_midi

    notes = [Note(60, 0.0, 0.5), Note(64, 0.75, 1.25)]
    write_midi(notes, tmp_path / "x.mid")
    pm = pretty_midi.PrettyMIDI(str(tmp_path / "x.mid"))
    assert [n.pitch for n in pm.instruments[0].notes] == [60, 64]

    write_musicxml(notes, tmp_path / "x.musicxml")
    xml = (tmp_path / "x.musicxml").read_text(encoding="utf-8")
    assert xml.count("<note") == 3   # two notes + one rest
