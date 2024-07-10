import json
import os
import re
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../headless-lsp/src"))
)

from lsp_client import LspClient
from agent.output import TalkLevel, print_talk, set_talk_level
from agent.agent import Agent
import config
from llm.qwen_llm import QwenLlmApi
import logger
from input_utils import get_multiline_input

logger.init_logger("DEBUG")
config.load_config()

set_talk_level(TalkLevel.FULL)

agent = Agent("Extractor", QwenLlmApi(config.LLM_PROFILE), logger=logger.LOGGER)
agent.configure(
    [
        """
        You are a C programmer reading the code.
        For a given line of code, extract all varaibles and macros with their character location.
        For each line, you should only output variable name and its location.
        The output should be in the format of <identifier> <location> with each identifier one line.
        For example, for the code:
        unsigned char *srcbuffs[MAX_SAMPLES];
        You should output:
        srcbuffs: 15
        MAX_SAMPLES: 24
        """
    ]
)
# supervisor = Superviser(
#     None, QwenLlmApi(config.LLM_PROFILE), agent, logger=logger.LOGGER
# )
# supervisor.auto_configure()

while True:
    prompt = get_multiline_input("You: ")
    if "exit" in prompt:
        logger.LOGGER.info("Exiting conversation")
        break
    response = agent.interact(prompt)
    if response is None:
        # print error in red color
        logger.LOGGER.error("Response is None")
