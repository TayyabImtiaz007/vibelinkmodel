from django.shortcuts import render
from django.http import JsonResponse
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

# Load OpenAI API key
openai.api_key = 'sk-proj-rTdGmsmvdWwKGN5GYueAT3BlbkFJalNzsq63OlWWOxwJ73wG'

# Define Google Calendar scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

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

def get_response(conversation_history):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history
    )
    return response.choices[0].message['content']

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

def get_name(text):
    name_extract = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Extract name from the user input and your response will only contain the user name nothing else."},
            {"role": "system", "content": text},
        ]
    )
    return name_extract.choices[0].message['content']

def get_email(text):
    email_extract = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Extract email from the user input and your response will only contain the user email nothing else."},
            {"role": "system", "content": text},
        ]
    )
    return email_extract.choices[0].message['content']

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
