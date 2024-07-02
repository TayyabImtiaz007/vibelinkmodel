import os,boto3,shutil
import moviepy.editor as mp
# import speech_recognition as sr
import whisper
from pydub import AudioSegment
from docx import Document
import pdfplumber


def whisper_trans(file):
    model = whisper.load_model("base")
    result = model.transcribe(file)
    text = result["text"]
    return text

class Extraction:
    def __init__(self, file):
        self.file = file

    def transcribe_video(self):
        # Extract audio from video
        # video = mp.VideoFileClip(self.file)
        # audio = video.audio
        audio = AudioSegment.from_file(self.file)
    
        # Export audio as MP3 (you could also choose other formats like wav, etc.)
        # audio.export(output_audio_path, format='mp3')

        # Save extracted audio to a temporary WAV file
        temp_wav_file_path = "temp_audio.wav"
        audio.export(temp_wav_file_path, format='wav')
        # audio.write_audiofile("temp_audio.wav")

        # Transcribe the extracted audio
        transcribed_audio = whisper_trans(temp_wav_file_path)
        os.remove(temp_wav_file_path)  # Remove temporary audio file

        # Return the transcribed text
        return transcribed_audio

    def whisper_trans(self):
        model = whisper.load_model("base")
        result = model.transcribe(self.file)
        text = result["text"]
        return text

    def transcribe_recording(self):
        # Load the audio file
        audio = AudioSegment.from_file(self.file)

        # Check if the audio is already in WAV format
        if audio.frame_rate != 44100 or audio.sample_width != 2 or audio.channels != 2:
            # Convert to WAV format (44.1 kHz, 16-bit stereo)
            audio = audio.set_frame_rate(44100).set_sample_width(2).set_channels(2)

        temp_wav_file_path = "temp_audio.wav"

        # Export the audio to WAV format
        audio.export(temp_wav_file_path, format="wav")
        transcribed_audio = whisper_trans(temp_wav_file_path)
        os.remove(temp_wav_file_path)
        return transcribed_audio





    def whisper_trans2(self):
        model = whisper.load_model("base")

        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio(self.file)
        audio = whisper.pad_or_trim(audio)

        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # detect the spoken language
        _, probs = model.detect_language(mel)
        print(f"Detected language: {max(probs, key=probs.get)}")

        # decode the audio
        options = whisper.DecodingOptions()
        text = whisper.decode(model, mel, options)

        return text


    def extract_text_from_pdf(self):
        """
        Extract all text from a PDF file.

        Parameters:
        - pdf_file_path (str): Path to the PDF file.

        Returns:
        - extracted_text (str): Extracted text from the PDF.
        """
        extracted_text = ""
        with pdfplumber.open(self.file) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text()
        return extracted_text


    def extract_text_from_document(self):
        doc = Document(self.file)
        text = ''
        for para in doc.paragraphs:
            text += para.text
        return text


    def extract_text_from_txtfile(self):
        # TEMP_DIR = '/tmp/' + user_id + '_' + username + '/'
        # os.makedirs(TEMP_DIR, exist_ok=True)
        # file_name = f"{user_id}+{username}_data.txt"
        text = ''
        with open(self.file, "r") as file:
            text = file.read()
        return text