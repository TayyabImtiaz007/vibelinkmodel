from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import openai
import json
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import logging
import re
import sys
import io
import boto3
from dotenv import load_dotenv

# Load OpenAI API key and other environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_KEY')

# Define Google Calendar scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# AWS S3 setup
s3_client = boto3.client('s3')
customer_bucket = 'chat-customers'

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.StreamHandler()
file_handler = logging.FileHandler('logs/excerpt_api.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Google Calendar authentication
def authenticate_google():
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds

# Google Calendar events retrieval
def get_events():
    creds = authenticate_google()
    try:
        service = build("calendar", "v3", credentials=creds)
        now = datetime.now(timezone.utc).isoformat()
        end_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            timeMax=end_time,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        return [(event["start"].get("dateTime", event["start"].get("date")),
                 event["end"].get("dateTime", event["end"].get("date")))
                for event in events]
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

# Time slot creation for appointments
def create_time_slots():
    slots = []
    tz = timezone(timedelta(hours=5))  # Adjust time zone as needed
    now = datetime.now(tz)
    for day_offset in range(3):  # Generate slots for the next 3 days
        start_time = now.replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=day_offset)
        end_time = start_time.replace(hour=15)
        
        while start_time < end_time:
            if start_time > now:  # Only add future time slots
                slots.append(start_time)
            start_time += timedelta(hours=1)
    
    return slots

# Find available slots from booked times
def find_available_slots(booked_times):
    time_slots = create_time_slots()
    available_slots = []

    for slot in time_slots:
        slot_end = slot + timedelta(hours=1)
        is_available = True
        for start, end in booked_times:
            booked_start = datetime.fromisoformat(start).astimezone(slot.tzinfo)
            booked_end = datetime.fromisoformat(end).astimezone(slot.tzinfo)
            if (booked_start < slot_end and booked_end > slot):
                is_available = False
                break
        if is_available:
            available_slots.append(slot.strftime("%Y-%m-%dT%H:%M:%S"))

    return available_slots

# Create a new calendar event
def create_event(name, email, slot):
    creds = authenticate_google()
    try:
        service = build("calendar", "v3", credentials=creds)
        start_time = {
            "dateTime": slot,
            "timeZone": "Asia/Karachi"  
        }
        end_time = {
            "dateTime": (datetime.strptime(slot, "%Y-%m-%dT%H:%M:%S") + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "Asia/Karachi"  
        }
        event = {
            "summary": name,
            "start": start_time,
            "end": end_time,
            "attendees": [{"email": email}],
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},
                    {"method": "popup", "minutes": 10},
                ],
            },
        }
        event = service.events().insert(calendarId="primary", sendNotifications=True, body=event).execute()
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])
    except HttpError as error:
        print(f"An error occurred: {error}")

# Get chatbot response
def get_response(conversation_history):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history
    )
    return response.choices[0].message['content']

# Get conversation history
def get_conversation_history(conversation_history):
    output_capture = io.StringIO()
    sys.stdout = output_capture
    for i, message in enumerate(conversation_history):
        role = "User" if message["role"] == "user" else "ChatGPT"
        print(f"{role}: {message['content']}")
    sys.stdout = sys.__stdout__
    captured_output = output_capture.getvalue()
    output_capture.close()
    return captured_output

# Extract name from text
def get_name(text):
    name_extract = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Extract name from the user input and your response will only contain the user name nothing else."},
            {"role": "system", "content": text},
        ]
    )
    return name_extract.choices[0].message['content']

# Extract email from text
def get_email(text):
    email_extract = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Extract email from the user input and your response will only contain the user email nothing else."},
            {"role": "system", "content": text},
        ]
    )
    return email_extract.choices[0].message['content']

# Process user input for chatbot
conversation_history = []

system_prompt = {"role": "system", "content": "You are an appointment booking chatbot. Follow these instructions strictly and don't answer beyond the scope of these instructions. 1. If the user requests to book an appointment, respond with: Sure, I'd be happy to help you book an appointment. Can you please provide your name? 2. Once the user provides their name, respond with: [User's Name]. Could you also provide your email address so we can send you the appointment details? 3. After receiving the user's email, confirm the information by saying: appointment [User's Name]. We have your email as [User's Email]. 4. Please select from the following free slots. 5. Event is booked kindly check email for confirmation. "}
conversation_history.append(system_prompt)

def process_user_input(user_input):
    try:
        conversation_history.append({"role": "user", "content": user_input})

        response = get_response(conversation_history)

        if "free slots" in response.lower():
            booked_times = get_events()
            available_slots = find_available_slots(booked_times)
            if available_slots:
                slots_message = "\n".join([f"Slot {i+1}: {slot}" for i, slot in enumerate(available_slots)])
            else:
                slots_message = "No available slots found."
            print(f"ChatGPT: Select a free slot:\n{slots_message}")
            conversation_history.append({"role": "assistant", "content": slots_message})
            return slots_message

        conversation_history.append({"role": "assistant", "content": response})

        print(f"ChatGPT: {response}")

        if "slot" in user_input.lower():
            text = get_conversation_history(conversation_history)
            name = get_name(text)
            email = get_email(text)
            slot_input = re.search(r"User: slot (\d+)", text)
            if slot_input:
                slot_number = int(slot_input.group(1))
                time_slots = re.findall(r"Slot \d+: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", text)
                if 1 <= slot_number <= len(time_slots):
                    slot = time_slots[slot_number - 1]
                    print(slot)
                    create_event(name, email, slot)
                    conversation_history.clear()
                    conversation_history.append(system_prompt)
        return response
    except Exception as e:
        logging.error(f"Error processing user input: {e}")
        return "Sorry, I couldn't process your request. Please try again."

# Django views for chatbot
def chatbot_view(request):
    if request.method == "POST":
        user_input = request.POST.get('user_input')
        response = process_user_input(user_input)
        return JsonResponse({'response': response})
    return render(request, 'chatbot/index.html')

def predict_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            response = process_user_input(message)
            return JsonResponse({'response': response})
        except Exception as e:
            logging.error(f"Error in predict_view: {e}")
            return JsonResponse({'response': "An error occurred. Please try again later."}, status=500)

# API views for text transcript and chat system
class TextTranscript(APIView):
    def post(self, request):
        output_transcript = {}
        if request.method == 'POST':
            try:
                file_id = request.data['user_id']
                file_name = request.data['user_file']
                user_name = request.data['username']
                customer_data = file_id + '_' + user_name + '/dataset/data.txt'
                temp_data_path = 'tmp/' + file_id + '_' + user_name + '/dataset/'
                os.makedirs(temp_data_path, exist_ok=True)
                filename = 'tmp/' + customer_data

                stt = Extraction(file_name)
                if file_name.name.endswith(".pdf"):
                    text = stt.extract_text_from_pdf()
                elif file_name.name.endswith(".wav"):
                    text = stt.whisper_trans()
                elif file_name.name.endswith((".mp4", ".avi", ".mkv")):
                    text = stt.transcribe_video()
                elif file_name.name.endswith(".docx"):
                    text = stt.extract_text_from_document()
                elif file_name.name.endswith(".txt"):
                    text = file_name.read()
                elif file_name.name.endswith((".m4a", ".mp3")):
                    text = stt.transcribe_recording()
                output_transcript = {
                    "text": text,
                    "file_id": file_id,
                    'user_name': user_name,
                    "file_name": file_name.name.split(".")[0]
                }
                response = s3_client.list_objects_v2(Bucket=customer_bucket, Prefix=customer_data)
                if 'Contents' in response:
                    update_file_s3_bucket(customer_bucket, customer_data, filename, text)
                else:
                    with open(filename, 'w') as file:
                        file.write(text + '\n')
                s3_client.upload_file(filename, customer_bucket, customer_data)
                print("File updated and uploaded successfully.")
                return Response(output_transcript, status=status.HTTP_200_OK)
            except Exception as error:
                logger.error([error])
                return Response(output_transcript, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(output_transcript, status=status.HTTP_404_NOT_FOUND)

class ChatSystem(APIView):
    def post(self, request):
        output_transcript = {}
        if request.method == 'POST':
            try:
                file_id = request.data['user_id']
                user_name = request.data['username']
                customer_data = file_id + '_' + user_name + '/dataset/data.txt'
                file_path = 'tmp/' + file_id + '_' + user_name
                file_name = 'tmp/' + customer_data
                temp_data_path = 'tmp/' + file_id + '_' + user_name + '/dataset/'
                os.makedirs(file_path, exist_ok=True)
                os.makedirs(temp_data_path, exist_ok=True)
                s3_client.download_file(customer_bucket, customer_data, file_name)
                chat = ChatService(file_name.split('/')[-1], file_id, file_path)
                chat.chatsys()
                output_transcript = {
                    "file_id": file_id,
                    "file_name": file_name.split(".")[0]
                }
                upload_folder_to_s3(file_path, customer_bucket, file_id + '_' + user_name)
                return Response(output_transcript, status=status.HTTP_200_OK)
            except Exception as error:
                logger.error([error])
                return Response(output_transcript, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(output_transcript, status=status.HTTP_404_NOT_FOUND)

class ChatBot(APIView):
    def post(self, request):
        output_transcript = {}
        if request.method == 'POST':
            try:
                file_id = request.data['user_id']
                user_name = request.data['username']
                text = request.data['text']
                file_path = 'tmp/' + file_id + '_' + user_name
                os.makedirs(file_path, exist_ok=True)
                download_folder_from_s3(customer_bucket, file_id + '_' + user_name, file_path)
                chat = ChatQueryService(file_id, text, file_path)
                text = chat.query_text_service()
                output_transcript = {
                    "text": text,
                    "file_id": file_id
                }
                return Response(output_transcript, status=status.HTTP_200_OK)
            except Exception as error:
                logger.error([error])
                return Response(output_transcript, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(output_transcript, status=status.HTTP_404_NOT_FOUND)
