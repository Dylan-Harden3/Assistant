from abc import ABC, abstractmethod
from email.mime.text import MIMEText
import base64
from duckduckgo_search import DDGS
from googleapiclient.discovery import build
from setup_credentials import setup_credentials
import googleapiclient
from datetime import timedelta
from typing import Optional, List
from utils import check_iso_format
from datetime import datetime


def get_gmail_service(creds=None):
    if creds is None:
        creds = setup_credentials()
    return build("gmail", "v1", credentials=creds)


def get_calendar_service(creds=None):
    if creds is None:
        creds = setup_credentials()
    return build("calendar", "v3", credentials=creds)


class Tool(ABC):
    @abstractmethod
    def __init__(self, name: str, description: str, usage: str):
        self.name = name
        self.description = description
        self.usage = usage

    @abstractmethod
    def run(self, *args, **kwargs):
        pass


class Email(Tool):
    def __init__(self):
        super().__init__(
            name="send_email",
            description="Uses the gmail API to send an email and returns success message or failure error. Useful when you want to send an email on behalf of the Human.",
            usage="send_email(recipient_email: str, subject: str, body: str, closing: str)",
        )
        self.gmail_service = get_gmail_service()

    def run(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        closing: str,
    ) -> str:
        message = MIMEText(body + "\n" + closing)
        message["to"] = recipient_email
        message["subject"] = subject
        message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        try:
            message = (
                self.gmail_service.users()
                .messages()
                .send(userId="me", body={"raw": message})
                .execute()
            )
            return "Email was sent successfully!"
        except Exception as e:
            return f"Error in send_email: {e}"


class Search(Tool):
    def __init__(self):
        super().__init__(
            name="search",
            description="Searches the internet with a query and returns some responses. Useful to retrieve any information that you dont have knowledge of.",
            usage="search(query: str)",
        )

    def run(self, query: str) -> str:
        search_results = DDGS().text(query, max_results=5)
        res = []
        for search in search_results:
            res.append("title: " + search["title"])
            res.append("href: " + search["href"])
            res.append("body: " + search["body"])
            res.append("\n")
        return "\n".join(res)


class CreateEvent(Tool):
    def __init__(self):
        super().__init__(
            name="create_event",
            description="Inserts an event into the Humans calendar with a summary, start_time, end_time and optional location, attendees list and time_zone. start_time and end_time must be in ISO format (YYYY-MM-DDTHH:MM:SS).",
            usage="create_event(summary: str, start_time: str, end_time: str, location: Optional[str]=None, attendees: Optional[List[str]]=None, time_zone: str='America/Chicago')",
        )
        self.calendar_service = get_calendar_service()

    def run(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        time_zone: str = "America/Chicago",
    ) -> str:
        if not summary or not start_time or not end_time:
            return "Error in create_event:  summary, start_time and end_time must be provided."

        if not check_iso_format(start_time):
            return "Error in create_event: start_time must be in valid ISO format (YYYY-MM-DDTHH:MM:SS)."

        if not check_iso_format(end_time):
            return "Error in create_event: end_time must be in valid ISO format (YYYY-MM-DDTHH:MM:SS)."

        if datetime.fromisoformat(start_time) >= datetime.fromisoformat(end_time):
            return f"Error in create_event: start_time {start_time} must be before end_time {end_time}."

        event = {
            "summary": summary,
            "start": {
                "dateTime": start_time,
                "timeZone": time_zone,
            },
            "end": {
                "dateTime": end_time,
                "timeZone": time_zone,
            },
            "location": location if location else "No Location Provided",
            "attendees": [{"email": email} for email in attendees] if attendees else [],
        }

        try:
            event = (
                self.calendar_service.events()
                .insert(calendarId="primary", body=event)
                .execute()
            )
            return f"Event created successfully: {event['htmlLink']}"
        except googleapiclient.errors.HttpError as e:
            if "conflict" in str(e).lower():
                return f"Error in create_event: the human already has an event in the time range {start_time} - {end_time}."
            return f"Error in create_event: {e}."


class ReadCalendar(Tool):
    def __init__(self):
        super().__init__(
            name="read_calendar",
            description="Checks the Humans calendar for a given date and returns any events they have on that day. Date must be in the format YYYY-MM-DD. You will likely need to use the get_date tool combined with what the Human says to use this tool.",
            usage="read_calendar(date: str)",
        )
        self.calendar_service = get_calendar_service()

    def run(self, date: str) -> str:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return f"Error: {date} is not in the correct format (YYYY-MM-DD)."
        time_min = target_date.isoformat() + "Z"
        time_max = (target_date + timedelta(days=1)).isoformat() + "Z"
        try:
            events_result = (
                self.calendar_service.events()
                .list(
                    calendarId="primary",
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
            if not events:
                return f"There are no scheduled events on {date}."
            else:
                res = []
                for event in events:
                    cur = []
                    for k, v in event.items():
                        cur.append(f"{k}: {v}")
                    res.append("\n".join(cur))
                return "\n".join(res)

        except googleapiclient.errors.HttpError as e:
            return f"Error in read_calendar: {e}."

class DeleteEvent(Tool):
    def __init__(self):
        super().__init__(
            name="delete_event",
            description="Deletes an event on the Humans calendar with a given event_id.",
            usage="delete_event(event_id: str)",
        )
        self.calendar_service = get_calendar_service()

    def run(self, event_id: str) -> str:
        try:
            self.calendar_service.events().delete(
                calendarId="primary", eventId=event_id
            ).execute()
            return "Event deleted successfully."

        except googleapiclient.errors.HttpError as e:
            if e.resp.status == 404:
                return f"Error in delete_event: event with ID {event_id} not found."
            return f"Error in delete_event: {e}."


class GetDate(Tool):
    def __init__(self):
        super().__init__(
            name="get_date",
            description="Returns the current date in the format Day of week, Month Day, Year.",
            usage="get_date()",
        )

    def run(self):
        from datetime import datetime

        cur = datetime.now()
        return cur.strftime("%A, %B, %d, %Y")
