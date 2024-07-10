import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from agent.output import TalkLevel, set_talk_level
from agent.agent import Agent
from agent.superviser import Superviser
import config
from llm.qwen_llm import QwenLlmApi
import logger
from input_utils import get_multiline_input

logger.init_logger("DEBUG")
config.load_config()

set_talk_level(TalkLevel.FULL)

agent = Agent("Agent", QwenLlmApi(config.LLM_PROFILE), logger=logger.LOGGER)
supervisor = Superviser(
    None, QwenLlmApi(config.LLM_PROFILE), agent, logger=logger.LOGGER
)
supervisor.auto_configure()

agent.configure("You are a programmer, and you need to find the bug in the code.")
while True:
    prompt = get_multiline_input("You: ")
    if "exit" in prompt:
        logger.LOGGER.info("Exiting conversation")
        break
    response = agent.interact(prompt)
    if response is None:
        # print error in red color
        logger.LOGGER.error("Response is None")
