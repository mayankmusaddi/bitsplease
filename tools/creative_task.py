from utils.openai_utils import openai_call


async def creative_task(query: str):
    system_prompt = "You are an expert in creative writing skills and assist user for their query"
    messages = [{"role": "user", "content": query}]
    _response, _ = await openai_call(system_prompt, messages)
    return _response["results"]
