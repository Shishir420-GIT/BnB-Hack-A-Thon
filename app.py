import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import google.generativeai as genai
from google.cloud import firestore
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables

# Initialize Firestore client
firestore_client = firestore.Client.from_service_account_json("reviewz_firebase_key.json")

def get_youtube_transcript(video_url):
    """Fetches the transcript of a YouTube video given its URL."""
    try:
        video_id = video_url.split("v=")[-1].split("&")[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        formatted_transcript = formatter.format_transcript(transcript)
        return formatted_transcript
    except Exception as e:
        return str(e)

def generate_comparison(transcript1, transcript2, model):
    """Generates a comparison table using Gemini AI."""
    model = genai.GenerativeModel(model)

    prompt = f"""
    You are a Technical Blogger for the smartphone industry, tasked with comparing specifications from transcripts. 
    
    Analyze the following transcripts and generate a table comparing the two phones' specifications and features:

    Transcript 1:
    {transcript1}

    Transcript 2:
    {transcript2}

    Please include:
    - Numeric specifications (e.g., screen size, resolution, camera megapixels, battery capacity, chipset performance).
    - Qualitative attributes (e.g., build quality, user experience, and durability).
    Format the output in a clear tabular structure.
    """
    response = model.generate_content(prompt)
    return response.text


def generate_summary(transcript, model):
    """Generates a summary table using Gemini AI."""
    model = genai.GenerativeModel(model)

    prompt = f"""
    You are a Technical Blogger for the smartphone industry, tasked with summarizating specifications from transcripts. 
    
    Analyze the following transcript and generate a summary.

    Return the below key points only:
    - Key Highlights
    - Paramteres considered for the Ranking
    - Best Feature wise, Budget and overall

    Below is the Transcript
    {transcript}

    Please make it concise and in layman terms, do not add additional data into it.
    """
    response = model.generate_content(prompt)
    return response.text


def generate_csv(transcript1, transcript2, model):
    """Generates a CSV-formatted string comparing two transcripts using Gemini AI."""
    model = genai.GenerativeModel(model)

    prompt = f"""
    You are a Technical Blogger specializing in smartphone specifications. Analyze the following transcripts and return the comparison strictly in CSV format.

    Transcript 1:
    {transcript1}

    Transcript 2:
    {transcript2}

    Ensure:
    - Include numeric specifications (e.g., screen size, resolution, camera megapixels, battery capacity).
    - Include qualitative attributes (e.g., build quality, user experience, durability).
    - No additional text or commentary—return only valid CSV data.

    Output Example:
    "Feature","Phone 1","Phone 2"
    "Screen Size","6.1 inches","6.5 inches"
    "Battery","4000 mAh","4500 mAh"
    """
    response = model.generate_content(prompt)
    return response.text


def generate_csv_to_markdown(data, model):
    """Generates a CSV-formatted string comparing two transcripts using Gemini AI."""
    model = genai.GenerativeModel(model)

    prompt = f"""
    You are a Technical Blogger specializing in smartphone specifications. Analyze the following and prepare a comparison table.

    Data:
    {data}

    Ensure:
    - Include numeric specifications (e.g., screen size, resolution, camera megapixels, battery capacity).
    - Include qualitative attributes (e.g., build quality, user experience, durability).
    - No additional text or commentary—return only valid CSV data.

    Output Example:
    "Feature","Phone 1","Phone 2"
    "Screen Size","6.1 inches","6.5 inches"
    "Battery","4000 mAh","4500 mAh"
    """
    prompt2 = f"""
    You are a Technical Blogger specializing in smartphone specifications. Your task is to analyze the given data and prepare a **comparison table** in CSV format.

    Data:
    {data}

    **Requirements**:
    1. Include **numeric specifications** (e.g., screen size, resolution, camera megapixels, battery capacity).
    2. Include **qualitative attributes** (e.g., build quality, user experience, durability).
    3. Do **not** add any text, commentary, or explanation outside the table.
    4. Ensure the data is accurate and well-structured as valid CSV.

    **Output Format**:
    Here is the data formatted as a well-spaced table for better readability:

    Feature	       |    Phone 1	          |   Phone 2
    Screen Size    |  6.1 inches	      |  6.5 inches
    Battery	       |    4000 mAh	      |   4500 mAh
    Build Quality  |	   Aluminum	      |   Plastic
    User Experience|	  Smooth and fast |	Feature-rich but laggy

    """

    response = model.generate_content(prompt2)
    return response.text

def store_csv_in_firestore(csv_data):
    """Stores the generated CSV data in Firestore."""
    doc_ref = firestore_client.collection("comparisons").document("last_comparison")
    doc_ref.set({"csv_data": csv_data})


def get_last_csv_from_firestore(model):
    """Fetches the last stored CSV data from Firestore."""
    doc_ref = firestore_client.collection("comparisons").document("last_comparison")
    doc = doc_ref.get()
    if doc.exists:
        data_in_md = doc.to_dict().get("csv_data")
        return generate_csv_to_markdown(data_in_md, model)
    return "No data found."


if __name__ == "__main__":
    genai.configure(api_key=os.getenv("API_KEY"))

    # Streamlit UI
    st.set_page_config(page_title="YouTube Video Comparison", page_icon="📊", layout="wide")
    selected_model = st.radio("Select Gemini Model:",
        ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-2.0-flash-exp'],
        key="selected_model_image",
        horizontal=True,
    )
    st.header("YouTube Video Comparator", divider="rainbow")
    st.image("media/Banner.gif", use_container_width=True)
    print(st.session_state, type(st.session_state.get('show_video')))

    # st.video("/Users/shishir/Desktop/ScreenRecording/Screen Recording 1946-09-21 at 17.18.24.mov", start_time=0)
    st.sidebar.image("media/LogoImage.webp", use_container_width=True)
    st.sidebar.header("Input Video URLs")
    video_url1 = st.sidebar.text_input("YouTube Video URL 1", "https://www.youtube.com/watch?v=vXIAB_1FEC0")
    video_url2 = st.sidebar.text_input("YouTube Video URL 2", "https://www.youtube.com/watch?v=MRtg6A1f2Ko")

    if st.sidebar.button("Compare Videos"):
        st.session_state["show_video"] = False

        with st.spinner("### Fetching Transcripts..."):
            transcript1 = get_youtube_transcript(video_url1)
            transcript2 = get_youtube_transcript(video_url2)
        col1, col2 = st.columns(2)
        with col1:
            with st.spinner("### Summarizing video 1"):
                st.write("### Summary of Video 1")
                st.markdown(generate_summary(transcript1, selected_model), unsafe_allow_html=True)
        with col2:
            with st.spinner("### Summarizing video 2"):
                st.write("### Summary of Video 2")
                st.markdown(generate_summary(transcript2, selected_model), unsafe_allow_html=True)
        
        st.header("Comparison Section", divider="rainbow")
        with st.spinner("Generating Comparison..."):
            comparison_result = generate_comparison(transcript1, transcript2, selected_model)
            st.write("### Comparison Table")
            st.markdown(comparison_result, unsafe_allow_html=True)

        if not comparison_result:
            st.error("No comparison data found!")
        else:
            if "csv_data" not in st.session_state:
                csv_data = generate_csv(transcript1, transcript2, selected_model)
                st.session_state.csv_data = "\n".join(csv_data.split("\n")[1:])
            store_csv_in_firestore(csv_data)

            st.download_button(
                label="Download as CSV",
                data=st.session_state.csv_data,
                file_name="comparison_table.csv",
                mime="text/csv"
            )

    # Button to display last comparison
    if st.sidebar.button("Show Last Comparison"):
        last_csv = get_last_csv_from_firestore(selected_model)
        st.write("### Previous Comparison")
        st.markdown(last_csv, unsafe_allow_html=True)

    #st.session_state["show_video"] = True
    st.header("@BnB Hack-a-thon", divider="rainbow")
    st.sidebar.markdown("Developed using Streamlit and Gemini AI.")
