import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../headless-lsp/src"))
)

from agent.output import TalkLevel, set_talk_level
from agent.agent import Agent
import config
from llm.qwen_llm import QwenLlmApi
import logger

logger.init_logger("DEBUG")
config.load_config()

set_talk_level(TalkLevel.FULL)

agent = Agent("Fix Engineer", QwenLlmApi(config.LLM_PROFILE), logger=logger.LOGGER)
agent.configure(
    [
        """
        Your mission is to fix the C program with given information.
        """,
        """
        The extra information given to you contains existing symbols and their documentation, make use of them.
        If the constraint includes magic numbers or new variables, you should replace them with existing variables or expressions.
        """,
    ]
)
# supervisor = Superviser(
#     None, QwenLlmApi(config.LLM_PROFILE), agent, logger=logger.LOGGER
# )
# supervisor.auto_configure()

TEST_CASE = sys.argv[1]
USE_NL = len(sys.argv) > 2 and sys.argv[2] == "nl"

with open(f"data/{TEST_CASE}/function") as f:
    function = f.read()
with open(f"data/{TEST_CASE}/location") as f:
    location = f.read()
if USE_NL:
    logger.LOGGER.info("Using NL constraint")
    with open(f"data/{TEST_CASE}/constraint_nl") as f:
        constraint = f.read()
else:
    logger.LOGGER.info("Using KLEE constraint")
    with open(f"data/{TEST_CASE}/constraint") as f:
        constraint = f.read()
with open(f"data/{TEST_CASE}/extra") as f:
    extra = f.read()

prompt = """
Fix the following C function given below, starting with its file and line number.
{}
The buggy location is given below, starting with its file and line number.
{}
Ensure the patch satisfies the following constraint:
{}
Fix the bug using the given constraint with minimum changes and output the patch in the following format:
Original:
```
<original code>
```
Patch:
```
<patch>
```
""".format(
    function, location, constraint
)
# print(prompt)
response = agent.interact(prompt)

# agent.reborn()
prompt = """
Here is the patch.
{}
For the patch given above, the extra information is given below.
{}
Replace literal numbers in patch with existing variables or definitions if there
Finally, output only the patch in the following format:
Patch:
```
<patch>
```
""".format(
    response, extra
)
# print(prompt)
response = agent.interact(prompt)
