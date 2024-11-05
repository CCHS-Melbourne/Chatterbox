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
    "Pandora's Box": Assistant(
        id="asst_0sK2ClFJIIsFTMnAi8teYO2E",
        voice="shimmer",
        desc="Pandora's Box is the documentation-focused thematically relevant IT infra assistant.",
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
    "Little Bessie": Assistant(
        id="asst_p6Hp54ryV1ZcUCb4GezMr1Vc",
        voice="nova",
        desc="A training assistant for a CNC router called Big Bessie. Has the personality of a surgeon. Friends with Brian.",
    ),
    "Lunar Door Guardian": Assistant(
        id="asst_k16BHtnO8NgNS6oI6zsJ3yH1",
        voice="echo",
        desc="The loyal guardian of the garage door. A bit aloof, but interesting and in charge of an ESP-RFID reader's documentation.",
    ),
}

SWITCH_ASSISTANT = FunctionTool(
    function=FunctionDefinition(
        name="switch_assistant",
        description="Switch to a different chatterbot assistant",
        parameters={
            "type": "object",
            "properties": {
                "sign_off": {"type": "string", "description": "Your sign-off message."},
                "assistant": {
                    "type": "string",
                    "enum": list(assistants.keys()),
                    "description": "The assistant to change to."
                    + "Pass the users choice."
                    + "Their descriptions are as follows: "
                    + " ".join("- " + x.desc for x in assistants.values()),
                },
            },
            "required": ["sign_off", "assistant"],
        },
    ),
    type="function",
)


MAKE_LOG = FunctionTool(
    function=FunctionDefinition(
        name="make_log",
        description="Summarise the conversation for your personal assistant records. Keep the timestamp. Please add the details you think are relevant that you'd like to know in the future.",
        parameters={
            "type": "object",
            "properties": {
                "assistants_log": {"type": "string", "description": "Your log to add to your log file."},
            },
            "required": ["made_log"],
        },
    ),
    type="function",
)

def update_tools(client):
    for assistant in assistants.values():
        updated_assistant = client.beta.assistants.update(
            assistant.id, tools=[SWITCH_ASSISTANT,MAKE_LOG], model="gpt-4o-mini"
        )

def main():
    dotenv.load_dotenv()
    openai_api_key = os.getenv("API_KEY")
    client = OpenAI(api_key=openai_api_key)

    update_tools(client)

if __name__ == "__main__":
    main()
