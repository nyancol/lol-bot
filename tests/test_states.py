from pcsd_cog.states import StateMachine, StateLobby, StateGame
from redbot.core.bot import Red
import pytest
from unittest import mock

from time import sleep


@pytest.fixture
def ctx():
    fake_ctx = mock.Mock()
    fake_ctx.author = "author_name"
    fake_ctx.guild.id = 0
    return fake_ctx

def test_lobby_to_game(ctx):
    # machine = StateMachine(StateLobby(ctx))
    pass


def test_game_to_lobby(ctx):
    # machine = StateMachine(StateGame(ctx))
    pass

