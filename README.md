# Read for Me

This project was created because I love listening to audiobooks at night, but some of my favorite novels are only available in PDF or EPUB format without audio versions. So, I built a simple Python program that converts these files into natural-sounding audio using Google Cloud Text-to-Speech. You can adjust the voice, speed, and pitch to your liking.

## How It Works

1. Upload a PDF or EPUB file.
2. The program extracts the text and splits it into chunks.
3. Google Cloud Text-to-Speech converts the text into an audio file.
4. Download the audio and listen!

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/read-for-me.git
cd read-for-me
```

### 2. Create a Virtual Environment

**On macOS/Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Google Cloud TTS

- Get your Google Cloud credentials and save the tts-project.json file in the root directory.
- Create a .env file:

```bash
GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/tts-project.json"
```

### 5. Run the Program

```bash
python read_for_me.py
```

This runs the program, and you can upload your files and convert them to audio.

### Future Plans

I’m planning to turn this into a web app later, but for now, it’s just the program code. Enjoy converting your books to audio! 😄
