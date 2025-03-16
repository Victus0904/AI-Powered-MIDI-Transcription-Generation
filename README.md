# AI-Powered-MIDI-Transcription-Generation

Transform raw audio into MIDI with the power of AI! This project leverages **machine learning and signal processing** to convert music into MIDI files, enabling easy editing, playback, and composition.

---

## 📌 Features
✅ **Transcribes audio to MIDI** using AI-powered pitch tracking  
✅ **Generates MIDI files** that can be edited in DAWs like FL Studio, GarageBand, or Ableton  
✅ **Handles monophonic melodies** with high accuracy  
✅ **Optimized note duration detection** to prevent choppy playback  
✅ **Exports MIDI files** for use in music production  

---

## 🛠 Installation
Make sure you have Python installed, then install the required dependencies:
```bash
pip install -r requirements.txt
```

Alternatively, install them manually:
```bash
pip install librosa pretty_midi numpy jupyter
```

---

## 🎼 How It Works
1. **Load an audio file** (MP3, WAV, etc.).
2. **Analyze pitch & detect melody** using AI-powered signal processing.
3. **Convert detected frequencies to MIDI notes**.
4. **Optimize note durations** to improve transcription accuracy.
5. **Save the final MIDI file** for further use or editing.

---

## 🚀 Usage
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/victus0904/ai-midi-transcription.git
cd ai-midi-transcription
```

### 2️⃣ Open the Jupyter Notebook
```bash
jupyter notebook AI_Powered_MIDI_Transcription_&_Generation.ipynb
```

### 3️⃣ Run the Notebook
Execute the cells step by step to:
- Load your audio file
- Extract melody
- Convert it into MIDI format
- Save the output MIDI file

### 4️⃣ Get Your MIDI File!
Your transcribed MIDI file will be saved as `output.mid`. Open it in any MIDI editor for playback and editing.

---

## 📝 Code Overview
- **Pitch Detection** → Uses AI-based signal processing to track pitch.
- **MIDI Conversion** → Maps detected frequencies to musical notes.
- **Note Optimization** → Merges and adjusts note lengths for accuracy.
- **Export as MIDI** → Saves the final transcription as `output.mid`.

---

## 🎹 Example
Input: `audio.mp3` (a simple melody or vocal recording)  
Output: `output.mid` (a playable MIDI version of the melody)

---

## 💡 Notes & Limitations
⚠️ Works best with **monophonic melodies** (single instrument or voice).  
⚠️ Accuracy depends on the **quality of the input audio**.  
⚠️ Not yet optimized for **polyphonic (chord-based) music**.  

---

## 🔥 Future Improvements
🔹 Support for **polyphonic transcription** (chords & multiple instruments)  
🔹 Integration with **deep learning models** for enhanced accuracy  
🔹 Real-time MIDI transcription support  

---

## 🤝 Contributing
Contributions are welcome! If you have ideas for improvements, feel free to fork the repository, create a new branch, and submit a pull request.

---

## 🎵 Have Fun Creating Music!
Let me know if you have any questions or feature suggestions. Happy coding! 🎹🚀

