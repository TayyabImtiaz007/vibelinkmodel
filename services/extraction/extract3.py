import logging,json,sys,os,csv,glob,sqlite3,csv,re,time,boto3,shutil
import certifi
import moviepy.editor as mp
# import speech_recognition as sr
import whisper
from pydub import AudioSegment
from docx import Document
import pdfplumber


# os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
# os.environ["SSL_CERT_FILE"] = certifi.where()
# pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
#AWS Services
# s3 = boto3.resource('s3')
# s3_client = boto3.client('s3', region_name='us-west-2')
# # sns = boto3.client('sns')
#
# userID = 'otbjg-hjjjj-hjjjj'
# first_name = 'Akinyiga'
# last_name = 'Obadamilare'
# Statement_bucket = 'jacob-ryan-customer-files'
# # items = 'vocabula'
# os.makedirs('/tmp/'+userID +'_' + first_name+last_name+'/txt/', exist_ok=True)
def transcribe_video(video_file_path):
    # Extract audio from video
    video = mp.VideoFileClip(video_file_path)
    audio = video.audio

    # Save extracted audio to a temporary WAV file
    temp_wav_file_path = "temp_audio.wav"
    audio.write_audiofile(temp_wav_file_path)

    # Transcribe the extracted audio
    transcribed_audio = whisper_trans(temp_wav_file_path)
    os.remove(temp_wav_file_path)  # Remove temporary audio file

    # Return the transcribed text
    return transcribed_audio


# def transcribe_audio(audio_file_path):
#     # Initialize recognizer
#     recognizer = sr.Recognizer()
#
#     # Load audio file
#     with sr.AudioFile(audio_file_path) as source:
#         # Adjust for ambient noise
#         recognizer.adjust_for_ambient_noise(source)
#
#         # Record the audio
#         audio_data = recognizer.record(source, duration=100)
#
#     # Transcribe audio using Google Speech Recognition
#     try:
#         transcribed_text = recognizer.recognize_google(audio_data)
#         return transcribed_text
#     except sr.UnknownValueError:
#         print("Google Speech Recognition could not understand the audio")
#     except sr.RequestError as e:
#         print(f"Could not request results from Google Speech Recognition service; {e}")


# Example usage

def transcribe_recording(recording_file):
    # Load the audio file
    audio = AudioSegment.from_file(recording_file)

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


def whisper_trans(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    text = result["text"]
    return text


def whisper_trans2(audio_path):
    model = whisper.load_model("base")

    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(audio_path)
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


# def extract_text_from_pdf(pdf_path):
#     with open(pdf_path, 'rb') as file:
#         reader = PyPDF2.PdfReader(file)
#         text = ''
#         for page_number in range(len(reader.pages)):
#             text += reader.pages(page_number).extractText()

def extract_text_from_pdf(pdf_file_path):
    """
    Extract all text from a PDF file.

    Parameters:
    - pdf_file_path (str): Path to the PDF file.

    Returns:
    - extracted_text (str): Extracted text from the PDF.
    """
    extracted_text = ""
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text()
    return extracted_text


def extract_text_from_document(doc_path):
    doc = Document(doc_path)
    text = ''
    for para in doc.paragraphs:
        text += para.text
    return text


def extract_text_from_txtfile(user_id, username, text):
    TEMP_DIR = '/tmp/' + user_id + '_' + username + '/'
    os.makedirs(TEMP_DIR, exist_ok=True)
    file_name = f"{user_id}+{username}_data.txt"
    with open(file_name, "w") as file:
        file.write(text)