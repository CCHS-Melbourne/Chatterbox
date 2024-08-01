import dotenv
import os
from openai import OpenAI
from openai.types.beta import FunctionTool
from openai.types import FunctionDefinition

assistants = {
    "Unhelpful Joker": "asst_K2kmAlLtH29ccFRMpSqJlhK7",
    "Brian": "asst_oiyEv1qS4b1T5bKgDMHc3tog",
    "SauceBot": "asst_yeHbJkwar6lGy6WpFmUPv7cd",
}
voices = {
    "Unhelpful Joker": "fable",
    "Brian": "onyx",
    "Little Bessie": "shimmer",
    "SauceBot": "alloy",
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
                    "enum": assistants.keys(),
                    "description": "The personality to change to. Pass the users choice. Their descriptions are as follows: - Unhelpful Joker is an entertainer that doesn't give helpful advice. - Brian is laser cutter assistant who likes burning things. - Saucebot is a sauce dispensing machine for 'snags' (sausages) and is bunnings mascot of the space, who likes sauce based puns brightening people's days.",
                },
            },
            "required": ["sign_off", "personality"],
        },
    ),
    type="function",
)


def update_tools(client):
    for assistant in assistants:
        updated_assistant = client.beta.assistants.update(
            assistants[assistant], tools=[SWITCH_PERSONALITY], model="gpt-4o-mini"
        )


def main():
    dotenv.load_dotenv()
    openai_api_key = os.getenv("API_KEY")
    client = OpenAI(api_key=openai_api_key)

    update_tools(client)


if __name__ == "__main__":
    main()
