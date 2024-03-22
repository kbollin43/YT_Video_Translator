import streamlit as st
from st_pages import Page, show_pages
import spacy
from youtube_transcript_api import YouTubeTranscriptApi
from langchain import OpenAI, PromptTemplate
from langchain.chains import LLMChain, LLMMathChain, TransformChain, SequentialChain, SimpleSequentialChain
from langchain.chat_models import ChatOpenAI
import pytube
from moviepy.editor import VideoFileClip, AudioFileClip
from gtts import gTTS
import os
from io import StringIO
import PyPDF2
import base64
from transformers import pipeline


nlp = spacy.load("en_core_web_sm")

global transcript

transcript = ''

st.set_page_config(
    page_title="Kalpana Project Phase",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

language_codes = {'Hindi': 'hi', 'Malayalam': 'ml', 'Tamil': 'ta', 'Telugu': 'te', 'Kannada': 'kn', 'Bengali': 'bn', 'Gujarati': 'gu', 'Marathi': 'mr'}

def convert_func():
    if ytlink:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(ytlink, languages=['en', 'ar', 'en-IN', 'en-GB', 'en-US', 'en-AU', 'en-CA', 'en-IE', 'en-ZA', 'en-JM', 'en-NZ', 'en-PH', 'en-TT', 'en-ZW'])
        except Exception as e: 
            st.error('Error in fetching transcript')
            st.error(e)
        
        original_transcript = ''

        for i in transcript:
            original_transcript+=i['text'] + ' '

        st.markdown(f"<h3 style='text-align: center; color:pink'>ORIGINAL TRANSCRIPT</h3>", unsafe_allow_html=True)
        st.write(original_transcript)

        st.write('')

        ans = convert_lang(original_transcript, target_language)
        st.markdown(f"<h3 style='text-align: center; color:pink'>CONVERTED TRANSCRIPT</h3>", unsafe_allow_html=True)
        st.write(ans)

        url = f"https://www.youtube.com/watch?v={ytlink}"

        yt = pytube.YouTube(url)
        video = yt.streams.filter(progressive=True, file_extension="mp4").first()

        custom_filename = f"{ytlink}.mp4"
        video.download(filename=custom_filename)

        video_clip = VideoFileClip(custom_filename)
        mute_and_play_text_over_video(custom_filename, ans)
            
    elif transcript1:
        binary_data = transcript1.getvalue()
        pdfReader = PyPDF2.PdfReader(transcript1)

        text=''
        for i in range(0, len(pdfReader.pages)):
            pageObj = pdfReader.pages[i]
            text+=pageObj.extract_text() + ' '

       
        ans2 = convert_lang(text, language_codes[target_language])
        tts = gTTS(text=ans2, lang=language_codes[target_language])
        tts.save("speech_target.mp3")
        audio_file = open('speech_target.mp3', 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')
        
        base64_pdf = base64.b64encode(binary_data).decode('utf-8')

        pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="800" type="application/pdf"></iframe>'

        st.markdown(pdf_display, unsafe_allow_html=True)


    

def mute_and_play_text_over_video(ytlink, text):
    url = f"https://www.youtube.com/watch?v={ytlink}"

    yt = pytube.YouTube(url)
    video = yt.streams.filter(progressive=True, file_extension="mp4").first()

    custom_filename = f"{ytlink}.mp4"
    video.download(filename=custom_filename)

    video_clip = VideoFileClip(custom_filename)
    muted_clip = video_clip.without_audio()

    tts = gTTS(text=text, lang='en')  
    tts.save("tts.mp3")

    final_clip = muted_clip.set_audio(AudioFileClip("tts.mp3"))

    final_clip.write_videofile(f"muted_with_tts_{custom_filename}")

    video_file = open(f'muted_with_tts_{ytlink}.mp4', 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)
    # st.stop()



def convert_lang(old_text, target_language):
    llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=.9, openai_api_key="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")
    prompt1 = PromptTemplate(
    template = """
                You are given text : {texty}.\n
                You are given the target language : {target_lang}.\n
                You have to convert text to target language
        """, input_variables=["texty", "target_lang"]
    )

    prompt_chain1 = LLMChain(llm=llm, prompt=prompt1)
    LLM_chain = SequentialChain(chains=[prompt_chain1], input_variables = ["texty", "target_lang"], verbose=True)

    tar_lang = LLM_chain({"texty":old_text, "target_lang":target_language})

    output_lang = tar_lang['text']

    return output_lang


st.title("Welcome to our App")

choice = st.sidebar.selectbox('choose one', ['YouTube Langauge converter', 'Q n a sys'])
# st.write('')
if choice == "YouTube Langauge converter":
    ytlink = st.text_input('Enter the youtube Vide ID')
    st.text('OR')
    transcript1 = st.file_uploader('Upload a file...', type="pdf")
    target_language = st.selectbox('Select Language', ['Hindi', 'Malayalam', 'Tamil', 'Telugu', 'Kannada', 'Bengali', 'Gujarati', 'Marathi'])
    convert = st.button('Convert')

    if convert:
        convert_func()

else:
    # st.write('Q n a sys')
    st.header("YouTube Q&A Chatbot")
    # qna = st.text_input('Enter the youtube Video ID')
    
    # # Init the chat history
    # if "messages" not in st.session_state:
    #     st.session_state.messages = []

    # # display chat messages from history on the app:
    # for message in st.session_state.messages:
    #     with st.chat_message(message["role"]):
    #         st.markdown(message["content"])
    
    # # react to the user:
    # prompt = st.chat_input("What's up?")
    # if prompt:
    #     # display user message in chat message container
    #     with st.chat_message("user"):
    #         st.markdown(prompt)
    #     # Add user message to the history:
    #         st.session_state.messages.append({"role": "user" , "content":prompt})

    #     response = f"Echo: {prompt}"

    #     # Display assistat response:
    #     with st.chat_message("assistant"):
    #         st.markdown(response)
    #     # Add this to messages:
    #     st.session_state.messages.append({"role":"assistant", "content": response})
    # Function to extract captions from YouTube video
    # Function to extract captions from YouTube video
    # Function to extract captions from YouTube video
    
    # Function to interact with ChatGPT API
    # Function to interact with ChatGPT API
    def chat_with_gpt(prompt):
        api_key = "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"
        endpoint = "https://api.openai.com/v1/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        data = {
            "model": "text-davinci-003",  # Model name or ID
            "prompt": prompt,
            "max_tokens": 100,  # Adjust as needed
            "temperature": 0.7  # Adjust as needed
        }

        response = requests.post(endpoint, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()["choices"][0]["text"]
        else:
            return "Error: Failed to get response from ChatGPT API"

    # Main Streamlit app
    def main():
        # User input
        user_input = st.text_input("Ask your question:")

        # ChatGPT interaction
        if user_input:
            response = chat_with_gpt(user_input)
            st.text_area("ChatGPT's Response:", value=response, height=150)

    # Run the app
    if __name__ == "__main__":
        main()