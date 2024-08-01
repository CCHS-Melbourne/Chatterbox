import dotenv
import os
from openai import OpenAI
from openai.types.beta import FunctionTool
from openai.types import FunctionDefinition
from collections import namedtuple

Assistant = namedtuple("Assistant", ["id", "voice", "desc"])

assistants = {
    "Unhelpful Joker": Assistant(
        id="asst_K2kmAlLtH29ccFRMpSqJlhK7",
        voice="fable",
        desc="Unhelpful Joker is an entertainer that doesn't give helpful advice.",
    ),
    "Brian": Assistant(
        id="asst_oiyEv1qS4b1T5bKgDMHc3tog",
        voice="onyx",
        desc="Brian is laser cutter assistant who likes burning things.",
    ),
    "SauceBot": Assistant(
        id="asst_yeHbJkwar6lGy6WpFmUPv7cd",
        voice="alloy",
        desc="Saucebot is a sauce dispensing machine for 'snags' (sausages) and is bunnings mascot of the space, who likes sauce based puns brightening people's days.",
    ),
}

SWITCH_PERSONALITY = FunctionTool(
    function=FunctionDefinition(
        name="switch_personality",
        description="Switch to a different chatterbot personality",
        parameters={
            "type": "object",
            "properties": {
                "sign_off": {"type": "string", "description": "Your sign-off message."},
                "personality": {
                    "type": "string",
                    "enum": list(assistants.keys()),
                    "description": "The personality to change to."
                    + "Pass the users choice."
                    + "Their descriptions are as follows: "
                    + " ".join("- " + x.desc for x in assistants.values()),
                },
            },
            "required": ["sign_off", "personality"],
        },
    ),
    type="function",
)


def update_tools(client):
    for assistant in assistants.values():
        updated_assistant = client.beta.assistants.update(
            assistant.id, tools=[SWITCH_PERSONALITY], model="gpt-4o-mini"
        )


def main():
    dotenv.load_dotenv()
    openai_api_key = os.getenv("API_KEY")
    client = OpenAI(api_key=openai_api_key)

    update_tools(client)


if __name__ == "__main__":
    main()
