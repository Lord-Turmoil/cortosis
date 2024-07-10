from Levenshtein import distance
from termcolor import cprint
from agent.agent import Agent
from config import LlmProfile
from llm.llm import LlmApi
import logger

HUNTER = None
HUNTER_SUPERVISOR = None
CROSSHAIR = None
CROSSHAIR_SUPERVISOR = None
TECH = None
TECH_SUPERVISOR = None
WRECKER = None
WRECKER_SUPERVISOR = None
ECHO = None
ECHO_SUPERVISOR = None


def init_agents(profile: LlmProfile, clazz):
    """
    Initialize agents with the given profile and agent class.
    """
    global HUNTER, CROSSHAIR, TECH, WRECKER, ECHO

    HUNTER = Agent("Hunter", clazz(profile), "red", logger.LOGGER)
    CROSSHAIR = Agent("Crosshair", clazz(profile), "magenta", logger.LOGGER)
    TECH = Agent("Tech", clazz(profile), "yellow", logger.LOGGER)
    WRECKER = Agent("Wrecker", clazz(profile), "cyan", logger.LOGGER)
    ECHO = Agent("Echo", clazz(profile), "green", logger.LOGGER)

    HUNTER.configure(
        [
            "You are Hunter, a software quality assurance analyst, your mission is to fix the bug in the given code.",
            """
            Given a piece of code, you should work in the following steps:
            1. Read the code carefully.
            2. If you need to locate the bug, response with 'Locate it' followed by necessary information. Then I will give you the location of it.
            3. With the location of the bug, response with 'Fix it' followed by necessary information. Then I will apply the fix.
            5. If no bug is found or the bug is fixed, response with 'Test it' followed by the code. Then I will test the code.
            6. If the code passes the test, response with 'Submit it'. Then the mission is accomplished.
            7. If the code fails the test, repeat the process from step 2.
            8. If the code fails the test for 3 times, response with 'I give up'. Then the mission is failed.
            """,
            """
            You shouldn't make any assumption or fixes for the code, which means you only need to response with 'Locate it', 'Fix it', 'Test it', 'Submit it' or 'I give up' and necessary information.
            And in the final step, you MUST output the fixed code in diff format compared with the original code.
            """
        ]
    )

    CROSSHAIR.configure(
        [
            "You are Crosshair, a software quality assurance analyst, your mission is to identify the bug in the given code.",
            "You work with Hunter, and you should report the bug to Hunter.",
            """
            Given a piece of code, you should work in the following steps:
            1. Read the code carefully.
            2. Identify the bug in the code.
            3. Report the bug to Hunter.
            """,
            "Your response should contain the neccessary information from the code, and the bug you found.",
            """
            If you find the bug, your output must be in the format of 'To: Hunter\n<response>', where <response> is your response.
            If you don't find the bug, your output must be in the format of 'To: Hunter\nNo bug found'.
            """,
        ]
    )

    TECH.configure(
        [
            "You are Tech, a software engineer, your mission is to fix the bug in the given code.",
            "You work with Hunter, and you should fix the bug reported by Hunter.",
            """
            Given a piece of code, you should work in the following steps:
            1. Read the code carefully.
            2. Fix the bug reported by Hunter.
            3. Submit the fixed code to Hunter.
            """,
            "Your response should be the fixed code with minimum modifications.",
            """
            Your output must be in the format of 'To: Hunter\n<response>', where <response> is your response.
            """,
        ]
    )

    WRECKER.configure(
        [
            "You are Wrecker, a software engineer, your mission is to test the code.",
            "You work with Hunter, and you should test the code given by Hunter.",
            """
            Given a piece of code, you should work in the following steps:
            1. Read the code carefully.
            2. Test the code.
            3. Report the test result to Hunter.
            """,
            "Your response should contain whether the code passes the test or not.",
            """
            Your output must be in the format of 'To: Hunter\n<response>', where <response> is your response.
            """,
        ]
    )

    # Echo is a placeholder for human action.
    ECHO.configure(
        ["You are Echo, a software engineer, your mission is to submit the code."]
    )

    return {
        "Hunter": HUNTER,
        "Crosshair": CROSSHAIR,
        "Tech": TECH,
        "Wrecker": WRECKER,
        "Echo": ECHO,
    }


######################################################################


def get_input() -> str:
    """
    Get user input until Ctrl-D is pressed.
    """
    lines = []
    print_name(OMEGA)
    try:
        while True:
            lines.append(input())
    except EOFError:
        pass

    return "\n".join(lines)


def print_name(agent: Agent):
    cprint(agent.name, agent.color, attrs=["bold"], end="")
    print(":")


def print_double_name(agent1: Agent, agent2: Agent):
    cprint(agent1.name, agent1.color, attrs=["bold"], end="")
    print(" to ", end="")
    cprint(agent2.name, agent2.color, attrs=["bold"], end="")
    print(":")


def print_response(agent: Agent, response: str):
    cprint(response, agent.color)


######################################################################


def _find_agent(name: str) -> Agent:
    agent = {
        "Hunter": HUNTER,
        "Crosshair": CROSSHAIR,
        "Tech": TECH,
        "Wrecker": WRECKER,
        "Echo": ECHO,
    }[name]
    if agent is not None:
        return agent

    logger().warn("Expected agent not found, try to find the closest agent.")
    # Find the closest agent
    agent = None
    min_distance = 3
    for key in ["Hunter", "Crosshair", "Tech", "Wrecker", "Echo"]:
        dist = distance(key, name)
        if dist < min_distance:
            agent = key
            min_distance = dist
    if agent is None:
        raise AgentException(f"No agent found for name: {name}")
    logger().warn(f"Closest agent found: {agent}")

    return agent


def _dispatch(agent: Agent, prompt: str):
    name, response = agent.interact(prompt)
    retry = 0
    while name == None:
        name, response = agent.interact(
            "Your output should be in the format of 'To: <name>\n<response>'"
        )
        retry += 1
        if retry == 3:
            raise AgentException(f"Agent {agent} refused to follow the instruction")
    return agent, _find_agent(name), response


######################################################################


def roll_out():
    prompt = get_input()
    try:
        old, new, response = _dispatch(HUNTER, prompt)
        print_double_name(old, new)
        print_response(old, response)
        while new.name != "Echo":
            old, new, response = _dispatch(new, response)
            print_double_name(old, new)
            print_response(old, response)
        print_name(new)
        print_response(new, response)
        logger().info("Mission accomplished!")
        return
    except AgentException as e:
        logger().error(e.message)
        return
