from termcolor import cprint
from enum import Enum

class TalkLevel(Enum):
    """
    The level of talk, used to filter unnecessary talks.
    """

    FULL = 0
    TRIVIAL = 1
    NORMAL = 2
    ESSENTIAL = 3


MIN_LEVEL = TalkLevel.NORMAL


def set_talk_level(level):
    global MIN_LEVEL
    MIN_LEVEL = level


def _print_name(agent):
    cprint(agent.name, agent.color, end="")


def _print_text(agent, text: str):
    cprint(text, agent.color)


def print_talk(agent, talk: str, level=TalkLevel.NORMAL):
    if level.value >= MIN_LEVEL.value:
        _print_name(agent)
        print(":")
        _print_text(agent, talk)


def print_communicate(agent, to, talk: str, level=TalkLevel.NORMAL):
    if level.value >= MIN_LEVEL.value:
        _print_name(agent)
        print(" to ", end="")
        _print_name(to)
        print(":\n")
        _print_text(agent, talk)
