<h1 align="center">File2Tape</h1>
<h3 align="center">A Python Library for Storing Files on Cassette Tapes</h3>
<hr>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.0%2B-green?style=for-the-badge&logo=python" alt="Python 3.0+">
</p>

---

## 📖 About
**File2Tape** is a Python library that allows you to encode files into audio signals for storage on cassette tapes and decode them back into their original form. It supports any file type and size, but files under **100KB** are recommended for optimal performance. Currently, there is no built-in compression.

---

## ⚙️ Requirements
- `Python 3.0` or higher
- `numpy`
- `scipy`

Install the required dependencies using:
```bash
pip install numpy scipy
```

---

## 📼 Usage

### 1. Create an instance of the class
```python
from file2tape import File2Tape

th = File2Tape(write_speed=2000)
```

### 2. Encode a file to audio
Encode the file `test/test.avif` into an audio `.wav` file:
```python
th.write("test/test.avif", "test/output.wav")
```

<p align="center">
  <img src="test/test.avif" alt="Original Image" width="300">
</p>

<p align="center">
  <b>WARNING:</b> The generated audio is loud!<br>
  <audio style="margin-top: 5px;" controls  src="test/output.wav">Your browser does not support the audio element</audio>
</p>

### 3. Decode the audio back to the original file
Decode the audio file `test/output.wav` back into the original file:
```python
th.read("test/output.wav", "test/decoded")
```

<p align="center">
  <img src="test/test.avif" alt="Original Image" width="300">
</p>

<p align="center">
  <b>WARNING:</b> The generated audio is loud! Ensure your volume is low before playing the audio.<br>
  <audio controls src="test/output.wav"></audio>
</p>

---

## 📝 Notes
- **File size:** Files larger than 100KB can result in very large `.wav` files and longer processing times.
- **Recommended formats:** Use efficient file formats like `AVIF` for images to reduce file size.
- **Audio warning:** The generated audio is loud and may damage speakers or hearing if played at high volume.