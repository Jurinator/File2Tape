
# ************************************************** #
# *                   File2Tape                    * #
# *                                                * #
# *  @author Jure                                  * #
# *  @date 29/04/2025                              * #
# *  @version 1.0                                  * #
# *  @license UNLICENCE                            * #
# *                                                * #
# *  @description Simple libarary for encoding     * #
# *  and decoding files to cassette. Recomended    * #
# *  file size is only up to 100KB. Estimated wav  * #
# *  file size is 4s per KB of data.               * #
# *  @note Sadly there is no compression built     * #
# *  yet, so to reduce file size, I suggest using  * #
# *  the AVIF image format instead of PNG.         * #
# *                                                * #
# ************************************************** #

import numpy as np
import os
from scipy.io.wavfile import write as write_wav, read as read_wav


class File2Tape:
    def __init__(self, write_speed: int):
        self.WRITE_SPEED = write_speed

        self.FREQ_LOW = 1000 # 0
        self.FREQ_HIGH = 2000 # 1
        self.FREQ_END = 3000 # end seq frequency

        self.SAMPLE_RATE = 44100
        self.DURATION = 1/write_speed
        self.BIT_SAMPLES = int(self.SAMPLE_RATE * self.DURATION)


    #! ENCODE

    def generate_tone(self, frequency: int, duration: float) -> np.ndarray:
        t = np.linspace(0, duration, int(self.SAMPLE_RATE *duration), endpoint=False)
        return np.sin(2 * np.pi * frequency * t)

    def encode_byte(self, byte: int) -> np.ndarray:
        signal = np.zeros(8 * self.BIT_SAMPLES)

        for i in range(8):
            bit = (byte >> (7 - i)) & 1
            tone = self.generate_tone(self.FREQ_HIGH if bit else self.FREQ_LOW, self.DURATION)
            signal[i * self.BIT_SAMPLES:(i + 1) * self.BIT_SAMPLES] = tone

        return signal

    def encode_file_type(self, file_type: str) -> np.ndarray:
        signal = []

        for char in file_type:
            signal.append(self.encode_byte(ord(char)))
        signal.append(self.encode_byte(0))

        return np.concatenate(signal)

    def encode_end_sequence(self) -> np.ndarray:
        signal = []

        for i in range(10):
            signal.append(self.generate_tone(self.FREQ_END, self.DURATION))

        return np.concatenate(signal)

    def write(self, file_path: str, output_wav: str) -> None:
        if not os.path.exists(file_path):
            return

        file_size = os.path.getsize(file_path)
        file_type = os.path.splitext(file_path)[1][1:]

        total_bits = (file_size + len(file_type) + 1) * 8 + 10 * 8
        total_samples = total_bits * self.BIT_SAMPLES
        audio_signal = np.zeros(total_samples)

        file_type_signal = self.encode_file_type(file_type)
        audio_signal[:len(file_type_signal)] = file_type_signal
        offset = len(file_type_signal)

        with open(file_path, "rb") as f:
            for byte in f.read():
                byte_signal = self.encode_byte(byte)
                audio_signal[offset:offset + len(byte_signal)] = byte_signal
                offset += len(byte_signal)

        end_signal = self.encode_end_sequence()

        audio_signal[offset:offset + len(end_signal)] = end_signal
        audio_signal = audio_signal / np.max(np.abs(audio_signal))

        write_wav(output_wav, self.SAMPLE_RATE, (audio_signal * 32767).astype(np.int16))


    #! DECODE

    def decode_bit(self, bit_signal: np.ndarray) -> int:
        fft_result = np.fft.fft(bit_signal)
        freqs = np.fft.fftfreq(len(bit_signal), 1 / self.SAMPLE_RATE)
        dominant_freq = freqs[np.argmax(np.abs(fft_result))]

        if abs(dominant_freq - self.FREQ_LOW) < abs(dominant_freq - self.FREQ_HIGH): return 0
        elif abs(dominant_freq - self.FREQ_END) < abs(dominant_freq - self.FREQ_HIGH): return "END"
        else: return 1

    def decode_byte(self, byte_signal: np.ndarray) -> int:
        byte = 0

        for i in range(8):
            bit_signal = byte_signal[i * self.BIT_SAMPLES:(i + 1) * self.BIT_SAMPLES]
            bit = self.decode_bit(bit_signal)

            if bit == "END": return "END"
            byte = (byte << 1) | bit

        return byte

    def read(self, wav_file: str, output_file: str) -> None:
        if not os.path.exists(wav_file):
            return

        sample_rate, audio_signal = read_wav(wav_file)

        if sample_rate != self.SAMPLE_RATE:
            return

        audio_signal = audio_signal / 32767.0
        decoded_data = bytearray()
        file_type = ""
        num_bits = len(audio_signal) // self.BIT_SAMPLES
        reading_file_type = True

        for i in range(0, num_bits, 8):
            byte_signal = audio_signal[i * self.BIT_SAMPLES:(i + 8) * self.BIT_SAMPLES]
            if len(byte_signal) < 8 * self.BIT_SAMPLES:
                break

            decoded_byte = self.decode_byte(byte_signal)
            if decoded_byte == "END":
                break

            if reading_file_type:
                if decoded_byte == 0:
                    reading_file_type = False
                else:
                    file_type += chr(decoded_byte)

            else: decoded_data.append(decoded_byte)

        with open(f"{output_file}.{file_type}", "wb") as f:
            f.write(decoded_data)

if __name__ == "__main__":
    tape_handler = File2Tape(write_speed=2000)
    tape_handler.write("test/test.avif", "test/output.wav")
    tape_handler.read("test/output.wav", "test/decoded")