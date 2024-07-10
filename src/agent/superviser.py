from typing import List
from agent.agent import MASTERMIND, BaseAgent
from agent.output import TalkLevel, print_communicate
from llm.llm import LlmApi


def _default_configure_callback(configure) -> List[str]:
    """
    Generate the configuration for the supervisor.
    """
    instructions = []
    instructions.append("You are a supervisor to an agent.")
    instructions.append(
        "Given am objective, your mission is to evaluate the agent's response to check if it meets the objective."
    )
    instructions.append("The overall responsibility for the agent is " + configure)
    instructions.append(
        "If the text starts with 'Objective', it means the objective of the agent. For this, you just need to remember it. "
        + "After that, it will be the responses from the agent, for which you need to evaluate."
    )
    instructions.append(
        "If the response meets the objective, just response with 'super good' and nothing else. "
        + "Otherwise, please provide feedback to the agent."
    )
    return instructions


def _default_evaluate_callback(objective, answer) -> str:
    """
    Generate the evaluation prompt.
    """
    return (
        "The response of agent is as follows:\n"
        + answer
        + "\n"
        + "Please evaluate if the response meets the objective."
    )


class Superviser(BaseAgent):
    def __init__(
        self,
        name: str,
        api: LlmApi,
        agent: BaseAgent,
        configure_callback=None,
        evaluate_callback=None,
        terminate_keyword=None,
        logger=None,
    ):
        super().__init__(
            f"{agent}'s Supervisor" if name is None else name,
            api,
            "white",
            logger,
        )
        agent.set_supervisor(self)
        
        self.agent = agent
        self.objective = ""
        self.configure_callback = (
            _default_configure_callback
            if configure_callback is None
            else configure_callback
        )
        self.evaluate_callback = (
            _default_evaluate_callback
            if evaluate_callback is None
            else evaluate_callback
        )
        self.terminate_keyword = (
            "super good" if terminate_keyword is None else terminate_keyword
        )

    def auto_configure(self):
        self.configure(self.configure_callback(self.agent.get_configuration()))

    def before_interact(self, objective):
        """
        This should be invoked before the agent start to reply.
        """
        self.reborn()
        self.objective = objective
        response = self.api.interact(self.objective)
        print_communicate(MASTERMIND, self, f"Objective: {self.objective}", TalkLevel.TRIVIAL)
        print_communicate(self, MASTERMIND, response, TalkLevel.TRIVIAL)

    def post_interact(self, answer) -> bool:
        """
        This should be invoked after every response of the agent.
        It will return whether the objective is satisfied in a tuple.
        The first element is a boolean indicating if the objective is satisfied.
        The second element is the response of the supervisor.
        """
        prompt = self.evaluate_callback(self.objective, answer)
        print_communicate(MASTERMIND, self, prompt, TalkLevel.TRIVIAL)
        response = self.api.interact(prompt)
        print_communicate(self, self.agent, response, TalkLevel.TRIVIAL)
        if self.terminate_keyword in response:
            self.logger.info("Objective completed")
            return True, None
        self.logger.info("Objective not satisfied")
        return False, response
