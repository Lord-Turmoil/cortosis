import json
import os
import re
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../headless-lsp/src"))
)

from lsp_client import LspClient
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

agent = Agent("LSP", QwenLlmApi(config.LLM_PROFILE), logger=logger.LOGGER)
agent.configure(
    [
        "You are a programmer to read the code base.",
        """
        You have access to a LSP Server with the following functions, their name and parameters are listed below:
        1. GotoDefinition <full path> <line> <character> - go to definition of a symbol at line and character
        2. FindReferences <full path> <line> <character> - find references of a symbol at line and character
        3. DocumentLink <full path> - get all links in a file
        4. DocumentSymbol <full path> - get symbols in a file
        5. GetFileContent <full path> - get the content of a file
        """,
        "You can browse the codebase freely using the functions above.",
        """
        When you want to use a function, type the function name and its parameters, separated by space. For example:
        Function: `DocumentSymbol /home/tonix/buaa/repair/demo/project/demo/main.c`
        """,
        "You must reply only with the functions you want to use, and the parameters for each function and use actual parameters."
    ]
)
# supervisor = Superviser(
#     None, QwenLlmApi(config.LLM_PROFILE), agent, logger=logger.LOGGER
# )
# supervisor.auto_configure()

client = LspClient("http://localhost:6256/jsonrpc")
try:
    client.initialize("/home/tonix/buaa/repair/demo/project/demo/")
except Exception as e:
    logger.LOGGER.error(e)
opened = set()
def execute_command(response):
    global opened
    # use re to extract text in ``
    "Function: `DocumentSymbol /home/tonix/buaa/repair/demo/project/demo/main.c`"
    alll = re.findall(r'Function: `([^`]+)`', response)
    if alll:
        for i in alll:
            logger.LOGGER
            command = i.split(" ")
            command_name = command[0]
            if command_name == "GotoDefinition":
                path = command[1]
                line = int(command[2])
                character = int(command[3])
                if path not in opened:
                    print(client.did_open(path))
                    opened.add(path)
                return client.goto_definition(path, line, character)
            elif command_name == "FindReferences":
                path = command[1]
                line = int(command[2])
                character = int(command[3])
                if path not in opened:
                    client.did_open(path)
                    opened.add(path)
                return client.find_references(path, line, character)
            elif command_name == "DocumentLink":
                path = command[1]
                if path not in opened:
                    client.did_open(path)
                    opened.add(path)
                return client.document_link(path)
            elif command_name == "DocumentSymbol":
                path = command[1]
                if path not in opened:
                    client.did_open(path)
                    opened.add(path)
                return client.document_symbol(path)
            elif command_name == "GetFileContent":
                path = command[1]
                with open(path, "r") as f:
                    return f.read()
            else:
                logger.LOGGER.error("Invalid command")


while True:
    prompt = get_multiline_input("You: ")
    if "exit" in prompt:
        logger.LOGGER.info("Exiting conversation")
        break
    response = agent.interact(prompt)
    if response is None:
        # print error in red color
        logger.LOGGER.error("Response is None")
    response = execute_command(response)
    if isinstance(response, dict):
        print(json.dumps(response))
    elif isinstance(response, list):
        print(json.dumps([v if isinstance(v, dict) else v.to_dict() for v in response]))
