import requests
import requests.exceptions
import dataclasses
import json
from pcsd_cog import events
from pcsd_cog.players import Player



class Fetcher():
    def __init__(self):
        self._id = None
        self._host = "192.168.1.11"
        self._port = "2999"

    def eventdata(self):
        params = {"eventID": self._id} if self._id else None
        try:
            response = requests.get("https://" + self._host + ":" + self._port + "/liveclientdata/eventdata", params=params, verify=False).json()
        except:
            return []

        # with open("./sample_eventdata.json") as f:
        #     response = json.load(f)
        if response["Events"]:
            self._id = max([e["EventID"] for e in response["Events"]]) + 1

        event_list = []
        for e in response["Events"]:
            event_class_str = "Event" + e["EventName"]
            event_class = getattr(events, event_class_str)
            event_list.append(event_class(**e))
        if event_list:
            print(f"Got events: {event_list}")
        return event_list


    def activeplayer(self):
        response = requests.get("https://" + self._host + ":" + self._port + "/liveclientdata/activeplayer", verify=False).json()


    def playerlist(self):
        try:
            response = requests.get("https://" + self._host + ":" + self._port + "/liveclientdata/playerlist", verify=False).json()
            # with open("sample_players.json") as f:
            #     response = json.load(f)
        except requests.exceptions.ConnectionError:
            return None
        print(response)
        return [Player(**p) for p in response]



    def gamestats(self):
        response = requests.get("https://" + self._host + ":" + self._port + "/liveclientdata/gamestats", verify=False).json()
