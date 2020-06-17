import pickle
from typing import Mapping, Tuple
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from collections import defaultdict
from pcsd_cog import events
from pcsd_cog.events import Event, Rule



def get_sheet(cell_range):
    SPREADSHEET_ID = "1we_1P6c7dxkJ-x5ORuDBtQusOkrjMLmfgQdTJweNNgc"
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=cell_range).execute()
    return result.get('values', [])


def parse_section(rows) -> Tuple[Event, Mapping[Rule, str]]:
    event = getattr(events, rows[0][0])
    rules = []
    links = []
    for row in rows:
        rule = {}
        for i, (cell1, cell2) in enumerate(zip(row[1:], row[2:])):
            rule[cell1.split('=')[0]] = cell1.split('=')[1]
            if i+3 == len(row):
                links.append(cell2)
        rules.append(rule)
    return event, {Rule(rule): link for rule, link in zip(rules, links)}

def parse(rows) -> Mapping[Event, Mapping[Rule, str]]:
    sections = []
    current_section = []
    mapping = {}
    for i, row in enumerate(rows):
        if any([v != '' for v in row]):
            current_section.append(row)
        if all([v == '' for v in row]) and current_section != [] or i+1 == len(rows):
            sections.append(current_section)
            current_section = []

    for section in sections:
        event, rules = parse_section(section)
        mapping[event] = rules
    return mapping
