import json
import os
import sys
from typing import Dict


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../headless-lsp/src"))
)

from tools.lsp_wrapper import LspWrapper, SymbolInfo
from lsp_client import LspClient
import config
import logger

logger.init_logger("DEBUG")
config.load_config()

# get first arg
CONFIG_PATH = os.path.join("data", sys.argv[1], "config")
with open(CONFIG_PATH, "r") as f:
    lines = f.readlines()

CWD = lines[0].strip()
FILE = lines[1].strip()
LINE = int(lines[2].strip())

client = LspClient("http://localhost:6256/jsonrpc")
try:
    client.initialize(CWD)
except Exception as e:
    logger.LOGGER.error(e)


def get_description(result: Dict[str, SymbolInfo], line):
    # check if result contains no item
    if not result:
        return None

    description = ""
    for k, v in result.items():
        description += f'{k} ("{v.file}", line {v.line + 1})\n'
        for prop, val in v.props.items():
            sym_descr = val.replace("\n", " ")
            description += f"{prop}: {sym_descr}\n"
        description += "---\n"
    return description


wrapper = LspWrapper(client)
with open(os.path.join("data", sys.argv[1], "extra"), "w") as f:
    for i in range(-3, 3):
        result = wrapper.fetch_line(os.path.join(CWD, FILE), LINE + i)
        descr = get_description(result, 992 + i)
        if descr is not None:
            f.write(descr)
