class AgentException(Exception):
    def __init__(self, agent, message, *args: object) -> None:
        super().__init__(*args)
        self.agent = agent
        self.message = message

    def __str__(self) -> str:
        return f"Agent {self.agent} failed to interact: {self.message}"
