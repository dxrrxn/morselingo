import streamlit as st
from PIL import Image
import pygame
import time
from gtts import gTTS
import os
from streamlit_option_menu import option_menu
from streamlit_folium import st_folium
import folium
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import boto3
import io
import openai
from streamlit_chat import message
import matplotlib.pyplot as plt
import numpy as np
import cv2
import random
import tempfile
import requests


@st.cache_resource()
def init_connection():
    return MongoClient(
        "mongodb+srv://dzrrzn:ppR8MaJGpemi81tn@cluster0.zdiqoso.mongodb.net/?retryWrites=true&w=majority"
    )


client = init_connection()


morse_code_dict = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    " ": " ",
}
morse_code_dict_reverse = {v: k for k, v in morse_code_dict.items()}


def text_to_morse(text):
    morse_code = []
    for char in text.upper():
        if char in morse_code_dict:
            morse_code.append(morse_code_dict[char])
        else:
            morse_code.append("?")  # Use '?' for unknown characters
    return " ".join(morse_code)


def morse_to_text(morse_code):
    morse_words = morse_code.split(" / ")
    text = []
    for morse_word in morse_words:
        morse_chars = morse_word.split(" ")
        word = ""
        for morse_char in morse_chars:
            if morse_char in morse_code_dict_reverse:
                word += morse_code_dict_reverse[morse_char]
            else:
                word += " "
        text.append(word)
    return " ".join(text)


def play_morse_sound(morse_code):
    pygame.init()

    sound_dot = pygame.mixer.Sound("dot.wav")
    sound_dash = pygame.mixer.Sound("dash.wav")

    for char in morse_code:
        if char == ".":
            sound_dot.play()
            time.sleep(0.2)
        elif char == "-":
            sound_dash.play()
            time.sleep(0.5)
        elif char == " ":
            time.sleep(0.5)


def play_text_sound(text):
    tts = gTTS(text)
    tts.save("temp.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.quit()
    os.remove("temp.mp3")


def generate_response(prompt):
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = completions.choices[0].text
    return message


# We will get the user's input by calling the get_text function
def get_text():
    input_text = st.text_input("You: ", "Hello, how are you?", key="input")
    return input_text


def translate_states(states):
    morse_code = ""
    on_state_durations = []  # List to store the duration of ON states
    off_state_durations = []  # List to store the duration of OFF states

    consecutive_ones = 0
    consecutive_zeros = 0

    for state in states:
        if state == 1:
            consecutive_ones += 1
            if consecutive_zeros > 0:
                off_state_durations.append(
                    consecutive_zeros
                )  # Store the duration of OFF state
                consecutive_zeros = 0  # Reset consecutive zeros counter
        else:
            consecutive_zeros += 1
            if consecutive_ones > 0:
                on_state_durations.append(
                    consecutive_ones
                )  # Store the duration of ON state
                consecutive_ones = 0  # Reset consecutive ones counter

    print("on_state_durations", on_state_durations)
    print("off_state_durations", off_state_durations)

    # Calculate a threshold based on the average duration of OFF states
    if off_state_durations:
        average_off_duration = sum(off_state_durations) / len(off_state_durations)
        print("average_off_duration", 1.5 * average_off_duration)
    else:
        average_off_duration = 0

    insert_space = False
    for i, duration in enumerate(on_state_durations):
        if i >= 0 and off_state_durations[i] > (1.5 * average_off_duration):
            insert_space = True

        if insert_space:
            morse_code += " "
            insert_space = False

        if duration > (1.5 * average_off_duration):
            morse_code += "-"
        else:
            morse_code += "."

    return morse_code


background = "Our project is to create a Morse code translator app for the Singapore Navy. It purpose is to enhance communication without internet by using machine learning and signal processing. This app quickly translates Morse code from flashing lights, reducing manual interpretation, saving time and costs, and ensuring precise communication during naval operations."
tusers = "The targeted users for this project are specifically the Singapore Navy. Nevertheless, individuals outside of this demographic who are interested in translating Morse code from flashing light videos can also benefit from and utilize this solution."
features = "The feature set encompasses a pivotal real-time translation mechanism that seamlessly converts flashing light signals into text, tailored to meet the Singapore Navy's distinct requirements. This solution stands out due to its user-friendly design, optimized specifically for efficient usage by naval personnel on board. Notably, its speed and precision are good, guaranteeing accurate translations. Furthermore, its outstanding accessibility ensures effortless adoption and utilization, cementing its role as a cutting-edge asset for maritime communication needs."
introduction = "Morse code is a system of encoding text characters as sequences of two different signal durations, called dots and dashes, or short and long signals. These signals can be transmitted using various methods, such as sound (auditory signals), light (visual signals), or even touch (tactile signals)."
invented = "Samuel F. B. Morse is known to have invented Morse code."
image = Image.open("conversiontable.png")
# logo = Image.open("logo morse.JPG")
# new_size = (150, 150)  # Adjust the width and height as needed
# logo = logo.resize(new_size)
# st.image(logo)
# Use CSS styling to make the header text red and large
st.markdown(
    """
    <style>
    /* Make the text red and large */
    .red-header {
        color: #CC3333;
        font-size: 4.5rem; /* Adjust the font size as needed */
    }

    /* Make the header text cover the entire container */
    .full-width-header {
        width: 100%;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Apply the CSS classes to the header
st.markdown(
    '<h1 class="red-header full-width-header">MorseLingo</h1>', unsafe_allow_html=True
)

selected = option_menu(
    menu_title=None,
    options=[
        "Home",
        "FAQs",
        "Contact Us",
        "Feedback",
        "Morse Bot",
        "Quiz",
    ],
    icons=[
        "Home",
        "Frequently Asked Questions",
        "Contact Us",
        "Feedback",
        "Chatbot",
        "Quiz",
        "Quiz",
    ],
    orientation="horizontal",
)

if selected == "Home":
    st.title("Morse Code Translation")

    st.subheader("Flashing Light to Text Converter")
    uploaded_file = st.file_uploader(
        "Upload your flashing light video here", type=["mp4"]
    )

    if st.button("Translate"):
        if uploaded_file is not None:
            # Convert the uploaded file to bytes
            video_bytes = uploaded_file.read()

            # Create a temporary directory
            temp_dir = tempfile.TemporaryDirectory()
            temp_file_path = os.path.join(temp_dir.name, "temp.mp4")

            # Write the video bytes to the temporary file
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(video_bytes)

            # Create a VideoCapture object from the temporary file
            video_capture = cv2.VideoCapture(temp_file_path)

            frame_counter = 0
            states = []  # To store ON/OFF states over time

            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break
                frame_counter += 1

                # Convert the frame to grayscale
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, thresholded_frame = cv2.threshold(
                    gray_frame, 200, 255, cv2.THRESH_BINARY
                )

                # Find contours in the thresholded frame
                contours, _ = cv2.findContours(
                    thresholded_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )

                # Determine if a contour is present
                is_signal = len(contours) > 0

                # If present, append to states
                states.append(1 if is_signal else 0)

            video_capture.release()

            # Now you can work with the 'states' list, which contains the ON/OFF states over time

            # Clean up: Close the temporary directory and remove the temporary file
            temp_dir.cleanup()

            video_capture.release()
            result = translate_states(states)
            st.write("Morse: ", result)
            translated = morse_to_text(result)
            st.write("Text: ", translated)

        if uploaded_file:
            file = uploaded_file

            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.mp4"

            file_content_io = io.BytesIO(file.read())

        s3 = boto3.client(
            service_name="s3",
            aws_access_key_id=st.secrets["access_key"],
            aws_secret_access_key=st.secrets["secret_access_key"],
        )
        try:
            s3.upload_fileobj(file_content_io, "videofilesmp", filename)
            file_data = {
                "filename": filename,
                "upload_date": datetime.now(),
            }
            db = client.morsecode
            videocollection = db.videofiles
            videocollection.insert_one(file_data)
            st.success(f"File uploaded and stored.")
        except Exception as err:
            st.error(f"Error uploading file: {err}")
    st.write("Files may be kept for research purposes")
    st.subheader("Text to Morse Translation")

    col1, col2 = st.columns(2)
    with col1:
        text2morse = st.text_input("Text")
        morse_result1 = text_to_morse(text2morse)
        st.write("Morse code detected is: ", morse_result1)
        soundbuttonmorse = st.button("Morse Sound")
        if soundbuttonmorse == True:
            play_morse_sound(morse_result1)
    with col2:
        morse2text = st.text_input("Morse")
        morse_result2 = morse_to_text(morse2text)
        st.write("Text detected is: ", morse_result2)
        soundbuttontext = st.button("Text Sound")
        if soundbuttontext == True:
            play_text_sound(morse_result2)

    st.subheader("Number of file inputs each day")
    db = client.morsecode
    collection = db.videofiles
    data = list(collection.find({}, {"upload_date": 1}))
    upload_dates = [entry["upload_date"] for entry in data]
    upload_dates = [entry.date() for entry in upload_dates]
    upload_counts = pd.Series(upload_dates).value_counts().sort_index()

    st.bar_chart(upload_counts, use_container_width=True)

if selected == "FAQs":
    st.title("Frequently Asked Questions")
    st.subheader("What is Morse Code?")
    st.markdown(introduction)
    st.image(image, caption="International Morse Code Conversion Table")
    st.subheader(
        "Here is a video of the US Navy optimising the flashing light to text converter"
    )
    st.video(
        "https://www.youtube.com/watch?v=8dpdBPyIoLA&t=39s&ab_channel=USNavyResearch"
    )
    st.subheader("Who invented Morse Code?")
    st.markdown(invented)

    st.subheader("Uses of Morse Code")
    (
        tab1,
        tab2,
        tab3,
        tab4,
    ) = st.tabs(
        [
            "Emergency Signaling",
            "Amateur Radio Communication",
            "Military and Tactical Communication",
            "Brain Training",
        ]
    )

    with tab1:
        st.markdown(
            "Morse code's concise and recognizable patterns make it useful for emergency situations. Flashing lights, signal mirrors, or audible signals can be used to transmit SOS (··· - - - ···) for help."
        )

    with tab2:
        st.markdown(
            "Morse code remains a popular mode of communication among amateur radio operators (Hams). It allows for long-distance communication even under challenging conditions."
        )

    with tab3:
        st.markdown(
            "In military contexts, Morse code can still be used for covert communication when silence is essential."
        )

    with tab4:
        st.markdown(
            "Learning Morse code involves memorization and pattern recognition, which can help keep the mind sharp and improve cognitive abilities."
        )

    st.subheader("Background of our Project")
    st.markdown(background)

    st.subheader("Targeted Users")
    st.markdown(tusers)

    st.subheader("Features")
    st.markdown(features)

if selected == "Contact Us":
    st.title("Contact Us")
    st.markdown(
        "Thank you for visiting our website! We're excited to connect with you. Whether you have questions, feedback, or just want to say hello, we're here to assist you. Below, you'll find our contact information as well as information about Temasek Polytechnic, the institution where we're currently studying."
    )
    st.subheader("Our Team")
    st.markdown("Feel free to connect with us on LinkedIn:")

    st.markdown("Ng Renjie")
    st.write("https://www.linkedin.com/in/ren-jie-ng/")
    st.markdown("Fong Wei Hung")
    st.write("https://www.linkedin.com/in/fong-wei-hung-864516218/")

    st.subheader("Contact Infomation")

    st.markdown(
        "If you have any inquiries or would like to get in touch, you can reach us via email:"
    )
    st.write(
        "General Inquiries: 2102630G@student.tp.edu.sg or 2100911c@student.tp.edu.sg"
    )
    st.header("Temasek Polytechnic")
    st.markdown(
        "We're students of Temasek Polytechnic in Diploma of Applied Artificial Intelligience.Temasek Polytechnic is known for its innovative approach to education and strong emphasis on hands-on learning,Temasek Polytechnic equips students with practical skills and knowledge that prepare them for the real world."
    )
    st.subheader("Address")
    st.write("21 Tampines Avenue 1 Singapore 529757")
    m = folium.Map(location=[1.3453, 103.9318], zoom_start=16)
    folium.Marker(
        [1.3453, 103.9318], popup="Temasek Polytechnic", tooltip="Temasek Polytechnic"
    ).add_to(m)

    st_data = st_folium(m, width=725)

    st.subheader("Website")
    st.write("www.tp.edu.sg")
    st.markdown(
        "Thank you once again for visiting our website. We look forward to connecting with you and providing the information you need. Whether it's about our projects, or just a friendly chat, we're here and eager to engage."
    )


if selected == "Feedback":
    st.title("Feedback Form")
    with st.form("myform1", clear_on_submit=True):
        name = st.text_input("Enter your Full Name")
        email = st.text_input("Enter your E-Mail")
        feedback = st.text_area("Enter your Feedback")
        rating = st.slider("Rate Our App", 1, 5, 3)
        needsreply = st.checkbox("Check if you want a reply from us :)")

        if st.form_submit_button("Submit"):
            # Create a dictionary to store the data
            feedback_data = {
                "date": datetime.now(),
                "name": name,
                "email": email,
                "feedback": feedback,
                "rating": rating,
                "needsreply": needsreply,
            }

            db = client.morsecode
            collection = db.feedback
            collection.insert_one(feedback_data)

            st.success("Feedback submitted successfully!")


if selected == "Morse Bot":
    st.title("Chat with Morse Bot")
    openai.api_key = st.secrets["openai_key"]
    # Storing the chat
    if "generated" not in st.session_state:
        st.session_state["generated"] = []

    if "past" not in st.session_state:
        st.session_state["past"] = []

    user_input = get_text()

    if user_input:
        output = generate_response(user_input)
        # store the output
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)

    if st.session_state["generated"]:
        for i in range(len(st.session_state["generated"]) - 1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")


if selected == "Quiz":
    # Define a list of dictionaries for your quiz questions
    trivia = [
        {
            "question": "Who invented Morse Code?",
            "options": [
                "Samuel Morse",
                "Karl Morse",
                "Patrick Morse",
                "Mandrin Morse",
            ],
            "correct_option": "Samuel Morse",
        },
        {
            "question": "Which of the following option is NOT a use of Morse Code?",
            "options": [
                "Emergency Signalling",
                "Military and Tactical Communication",
                "Radio Communication",
                "Programming in Cars",
            ],
            "correct_option": "Programming in Cars",
        },
        {
            "question": "The letters of a word are separated by a space of how many units?",
            "options": ["1", "2", "3", "4"],
            "correct_option": "3",
        },
        {
            "question": "When was Morse Code invented?",
            "options": [
                "May 24, 1884",
                "May 24, 1844",
                "May 24, 1944",
                "May 24, 1994",
            ],
            "correct_option": "May 24, 1844",
        },
        {
            "question": "These are some ways that Morse Code can be transmitted. Which of the following is False?",
            "options": ["Flashing Lights", "Blinking", "Tapping", "Dancing"],
            "correct_option": "Dancing",
        },
        {
            "question": "What does the morse '... --- ...' translate into?",
            "options": ["EEETTTEEE", "SOS", "MOM", "SAS"],
            "correct_option": "SOS",
        },
        {
            "question": "What letter is represented by four dots?",
            "options": ["K", "H", "J", "G"],
            "correct_option": "H",
        },
        {
            "question": "What letter is represented by two dashes?",
            "options": ["O", "N", "M", "A"],
            "correct_option": "N",
        },
        {
            "question": "The letters of a word are separated by a space of how many units?",
            "options": ["1", "2", "3", "4"],
            "correct_option": "3",
        },
        {
            "question": "What does the morse '.--.' translate into?",
            "options": ["P", "Q", "R", "S"],
            "correct_option": "P",
        },
        {
            "question": "What letter is made out of 1 dash?",
            "options": ["T", "C", "A", "O"],
            "correct_option": "T",
        },
    ]

    # Initialize session state to maintain quiz state
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
        st.session_state.score = 0

    # Shuffle the quiz questions randomly only once when starting the quiz
    if st.session_state.current_question == 0:
        random.shuffle(trivia)

    # Streamlit app
    st.title("Morse Quiz")

    # Display the current question and options
    if st.session_state.current_question < len(trivia):
        st.subheader(
            f"Question {st.session_state.current_question + 1}: {trivia[st.session_state.current_question]['question']}"
        )
        selected_option = st.radio(
            "Select an option:", trivia[st.session_state.current_question]["options"]
        )

        # Check if the answer is correct
        if st.button("Submit"):
            if (
                selected_option
                == trivia[st.session_state.current_question]["correct_option"]
            ):
                st.session_state.score += 1

            st.session_state.current_question += 1

    # Display the score or quiz completion message
    if st.session_state.current_question == len(trivia):
        st.success(
            f"Quiz Completed! Your Score: {st.session_state.score}/{len(trivia)}"
        )
    else:
        st.write(
            f"Current Score: {st.session_state.score}/{st.session_state.current_question + 1}"
        )

        # Display the next question button
        if st.session_state.current_question < len(trivia):
            st.button("Next Question")
