import yaml

from logger import LOGGER


class LlmProfile:
    def __init__(self, name, base_url, key):
        self.name = name
        self.base_url = base_url
        self.key = key


global LLM_PROFILE
LLM_PROFILE = None


def load_config(filename="config.yaml"):
    global LLM_PROFILE

    with open(filename, "r") as f:
        CONFIG = yaml.load(f, Loader=yaml.FullLoader)
    try:
        select = CONFIG["llm"]["select"]
        for profile in CONFIG["llm"]["profiles"]:
            if profile["name"] == select:
                LLM_PROFILE = LlmProfile(
                    profile["name"], profile["base_url"], profile["key"]
                )
                break
    except KeyError:
        LOGGER.error("Config file is not valid")
        exit(1)
