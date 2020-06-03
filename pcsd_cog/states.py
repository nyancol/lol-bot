from promise import Promise
import asyncio

class Message:
    type: str
    data: bin


class State:
    pass



class StateDisconnected(State):
    events: Event = EventConnected

class StateConnected(State):
    events: Event = EventFriendConnected

class StateLobby(State):
    events: Event = EventChampionSelect

    def inbox(self, event):
        pass

class StateGame(State):
    events: Event = EventData

class StateGameEnd(State):
    events: Event = EventGameStats


class StateMachine:
    def __init__(self, initial_state: State):
        self.current_state = initial_state
        self.current_state.run()

    def inbox(self, event):
        
