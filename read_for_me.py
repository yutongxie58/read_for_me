import PyPDF2
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
from tqdm import tqdm

import os
from google.cloud import texttospeech
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv("/Users/yutongxie/python-workspace/read_for_me/.env")

# Function to clean up the extracted text
def clean_text(text):
    text = re.sub(r'\s+', ' ', text) 
    return text.strip()

# Word-safe chunking function
def split_text_into_chunks(text, max_chunk_size=4500):
    chunks = []
    while len(text) > max_chunk_size:
        # Find the last space or punctuation mark before the limit
        split_at = text.rfind(' ', 0, max_chunk_size)
        if split_at == -1:
            # If no space is found, just cut at the limit (fallback)
            split_at = max_chunk_size
        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()
    if text:
        chunks.append(text)
    return chunks

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            num_pages = len(reader.pages)
            for page_num in tqdm(range(num_pages), desc="Processing PDF Pages"):
                page_text = reader.pages[page_num].extract_text()
                page_text = clean_text(page_text)
                page_text = re.sub(r'\b\d{1,3}\b', '', page_text)
                text += page_text
            return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None

# Function to extract text from EPUB and omit unwanted patterns like page numbers
def extract_text_from_epub(epub_path):
    try:
        book = epub.read_epub(epub_path)
        text = ''
        items = list(book.get_items())
        total_items = len(items)

        for item in tqdm(items, total=total_items, desc="Processing EPUB Chapters"):
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.content, 'html.parser')
                chapter_text = clean_text(soup.get_text())
                chapter_text = re.sub(r'\b\d{1,3}\b', '', chapter_text)
                text += chapter_text + ' '
        return text
    except Exception as e:
        print(f"Error reading EPUB file: {e}")
        return None
    
# Function to convert text to speech using Google Cloud TTS
def google_tts(text, output_audio_file='output.mp3', gender='male', speed=1.0, pitch=0.0):
    client = texttospeech.TextToSpeechClient()

    # Split the text into chunks below the 5000-byte limit
    chunks = split_text_into_chunks(text)

    print(f"Splitting text into {len(chunks)} chunks for TTS processing.")
    audio_content = b''

    for idx, chunk in enumerate(chunks):
        print(f"Processing chunk {idx+1}/{len(chunks)}")
        synthesis_input = texttospeech.SynthesisInput(text=chunk)

        voice_params = {
            'male': texttospeech.SsmlVoiceGender.MALE,
            'female': texttospeech.SsmlVoiceGender.FEMALE,
            'neutral': texttospeech.SsmlVoiceGender.NEUTRAL
        }

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            ssml_gender=voice_params.get(gender, 'male')
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speed,
            pitch=pitch
        )

        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        audio_content += response.audio_content  # Concatenate the audio chunks

    # Save the concatenated audio to an MP3 file
    with open(output_audio_file, "wb") as out:
        out.write(audio_content)
        print(f"Audio content written to file {output_audio_file}")

# Function to handle file naming conflicts
def get_unique_filename(directory, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}_{counter}{extension}"
        counter += 1
    return new_filename

# Main function to upload file, extract text, and generate audio
def process_file(file_path, gender='male', speed=1.0, pitch=0.0):
    if not os.path.exists(file_path):
        print(f"File '{file_path}' does not exist.")
        return
    
    # Determine file type and extract text
    if file_path.endswith('.pdf'):
        extracted_text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.epub'):
        extracted_text = extract_text_from_epub(file_path)
    else:
        print("Unsupported file format. Please upload a PDF or EPUB file.")
        return

    # Create 'audio_files' directory if it doesn't exist
    audio_dir = 'audio_files'
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
        print(f"Directory '{audio_dir}' created to store audio files.")

    # Get unique filename for audio
    file_name = os.path.basename(file_path).replace(' ', '_').split('.')[0]
    output_audio_file = get_unique_filename(audio_dir, f"{file_name}.mp3")

    # Convert extracted text to speech and save audio
    google_tts(extracted_text, os.path.join(audio_dir, output_audio_file), gender, speed, pitch)
    print(f"Audio saved as {output_audio_file} in {audio_dir}")

if __name__ == "__main__":
    # Replace with the path to your PDF or EPUB file
    file_path = './my_files/silent_reading.pdf'
    
    # You can adjust gender, speed, and pitch here
    process_file(file_path, gender='male', speed=1.1, pitch=0.0)