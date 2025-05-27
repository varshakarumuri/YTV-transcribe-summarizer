import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt for Gemini
prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video, providing the important summary in points within 250 words.
Please provide the summary of the text given here: """


def extract_transcript_details(youtube_video_url):
    try:
        # Extract the video ID robustly
        if "v=" in youtube_video_url:
            video_id = youtube_video_url.split("v=")[-1].split("&")[0]
        elif "youtu.be/" in youtube_video_url:
            video_id = youtube_video_url.split("youtu.be/")[-1].split("?")[0]
        else:
            raise ValueError("Invalid YouTube URL format.")
        
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = " ".join([entry["text"] for entry in transcript_data])
        return transcript

    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        st.error("No transcript found for this video.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        raise e


def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content(prompt + transcript_text)
    return response.text


# UI
st.title("🎥 YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    try:
        # Extract video ID and show thumbnail
        if "v=" in youtube_link:
            video_id = youtube_link.split("v=")[-1].split("&")[0]
        elif "youtu.be/" in youtube_link:
            video_id = youtube_link.split("youtu.be/")[-1].split("?")[0]
        else:
            st.error("Invalid YouTube URL format.")
            video_id = None

        if video_id:
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

    except Exception as e:
        st.error(f"Could not extract video ID or display thumbnail: {e}")

if st.button("Get Detailed Notes"):
    if youtube_link:
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            st.markdown("## 📝 Detailed Notes:")
            st.write(summary)
        else:
            st.error("Transcript is empty or could not be retrieved.")
