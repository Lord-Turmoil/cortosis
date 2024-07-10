from config import LlmProfile
from llm.llm import LlmApi
import logger


class QwenLlmApi(LlmApi):
    def __init__(self, profile: LlmProfile):
        super().__init__(profile)

    def interact(self, prompt: str) -> str:
        """
        Interact with the AI. For now, we just don't need stream.
        """
        self.history.append({"role": "user", "content": prompt})
        try:
            response = self.client.chat.completions.create(
                model="qwen-turbo", messages=self.history, temperature=0.6
            )
            content = response.choices[0].message.content
            self.history.append(
                {"role": "assistant", "content": response.choices[0].message.content}
            )
        except Exception as e:
            logger.LOGGER.error(f"Error fetch response: {e}")
            logger.LOGGER.error(f"Failed prompt: {prompt}")
            self.history.pop()  # remove the failed prompt
            return None
        return content
