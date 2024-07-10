from typing import List
from agent.output import TalkLevel, print_communicate, print_talk
from agent.exceptions import AgentException
from llm.llm import LlmApi
import logger


class BaseAgent:
    """
    Base class for all agents.
    """

    def __init__(self, name: str, api: LlmApi, color: str, logger=None):
        self.name = name
        self.color = color
        self.api = api
        self.instructions = []
        self.supervisor = None
        self.logger = logger

    def __str__(self):
        return self.name

    def set_supervisor(self, supervisor):
        self.supervisor = supervisor

    def configure(self, instructions: List[str]):
        """
        Give the agent instructions of what to do.
        This should be implemented by specific agents.
        """
        for instruction in instructions:
            self.api.configure(instruction)
        self.instructions = instructions

    def get_configuration(self):
        return "\n".join(self.instructions)

    def reborn(self):
        self.api.restart()

    def interact(self, prompt):
        raise NotImplementedError("This should be implemented by specific agents.")


class Agent(BaseAgent):
    def __init__(self, name: str, api: LlmApi, color: str = "green", logger=None):
        super().__init__(name, api, color, logger)

    def interact(self, prompt):
        """
        Interact with the agent, return the name, and response.
        Note that None will be returned if some thing wrong happens.
        """
        logger.LOGGER.debug(f"Agent {self.name} is thinking...")

        if self.supervisor is not None:
            self.supervisor.before_interact(prompt)

        response = self.api.interact(prompt)
        if response == None:
            raise AgentException(self, "Response with None")
        print_talk(self, response, TalkLevel.NORMAL)

        if self.supervisor is not None:
            status, feedback = self.supervisor.post_interact(response)
            retry = 0
            while not status:
                if retry == 5:
                    # raise AgentException(self, "Failed to refine the response")
                    response = "I am sorry, I am not able to understand your request, please rephrase it."
                    if self.logger:
                        self.logger.warning(
                            f"Agent {self.name} failed to refine the response"
                        )
                    break
                response = self.api.interact(feedback)
                print_communicate(self, self.supervisor, feedback)
                status, feedback = self.supervisor.post_interact(response)
                retry = retry + 1
        return response


# This is a placeholder for global conversation.
global MASTERMIND
MASTERMIND = Agent("Mastermind", None, "black")
