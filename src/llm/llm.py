from openai import OpenAI
from config import LlmProfile


class LlmApi:
    """
    Base interface for agent.
    """

    def __init__(self, profile: LlmProfile):
        self.client = OpenAI(
            api_key=profile.key,
            base_url=profile.base_url,
        )
        self.history = []

    def configure(self, prompt: str):
        """
        Configure the AI with system prompt.
        This should be called before any interaction.
        """
        self.history.append({"role": "system", "content": prompt})

    def restart(self, hard: bool = False):
        """
        Restart the conversation. If hard is True, clear all history.
        Otherwise, configured system prompts will be kept.
        """
        if hard:
            self.history = []
        else:
            i = 0
            for history in self.history:
                if history["role"] == "system":
                    i += 1
                else:
                    break
            self.history = self.history[:i]

    def interact(self, prompt: str) -> str:
        """
        Interact with the AI.
        """
        raise NotImplementedError
