from utils.openai_utils import openai_call


async def decision_node(query: str, options: list):
    system_prompt = "You are expert at making decisions."
    prompt = f"User Query: {query}\n Options: {options}\n Based on the user query, respond with one of the options. Do not write anything else except from the chosen option string"
    messages = [{"role": "user", "content": prompt}]
    _response, _ = await openai_call(system_prompt, messages)
    return _response["results"]
