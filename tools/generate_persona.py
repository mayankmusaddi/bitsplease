from utils.openai_utils import openai_call
import json


async def generate_persona(messages: list, tools: list=[]):
    tools = [json.dumps(tool) for tool in tools]
    tool_string = "# TASK LIST #:\n"
    tool_string += "\n".join(tools)

    system_prompt = ("You are an expert in understanding any persona and "
                     "creating a defined structured format")

    prompt = tool_string + """

    The above conversation describes how the user has shared with an assistant to create it's persona. 

    # GOAL #:
    Based on the above tools and the above conversation, I want you generate task steps, task nodes and task links to capture the complete flow that the user describes.
    The format must be a strict JSON, like: 
    {
    "Communication_Style" : "PLACEHOLDER1" ,
    "Tone_of_Voice": "PLACEHOLDER2",
    "WORK_TITLE":  "PLACEHOLDER3",
    "COMPANY": "PLACEHOLDER4",
    "NAME": "PLACEHOLDER5"}

    """

    prompt += """
    # REQUIREMENTS #: 
    1 Communication_Style :Analyze how the employee communicates with others. Do they use formal or informal language? Do they use jargon or technical terms? Do they use short, concise sentences or long, detailed explanations?
    2 Tone_of_Voice: Pay attention to the tone the employee uses. Are they generally positive and upbeat, or more serious and straightforward? Do they use humor or sarcasm?
    3 WORK_TITLE: What is user's title at your company 
    4 COMPANY: What is user's company 
    5 NAME : What is user's name     4. ensure all the steps are covered.
    6. Till you don't have this info, please continue talking to the user. Avoid repeating yourself and ask one thing at a time ensuring brevity.
    7. avoid using execute_python_code unless it is for mathematical reasoning. 
    8. only respond the json, say nothing else"""

    if messages[0]["role"] != "system":
        messages = [{"role": "system", "content": ""}] + messages
    messages[0]["content"] = system_prompt
    messages += [{"role": "user", "content": prompt}]

    _response, _ = await openai_call(system_prompt, messages)
    persona_string = _response["results"]
    if persona_string.startswith("```json"):
        persona_string = persona_string[len("```json"):-3]
    persona_json = json.loads(persona_string)
    return persona_json
