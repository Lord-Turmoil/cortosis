from agent.agents import init_agents, roll_out
from config import get_llm_profile, load_config
from llm.qwen_llm import QwenLlmApi
from logger import init_logger

init_logger("DEBUG")
load_config()

init_agents(get_llm_profile(), QwenLlmApi)
roll_out()
