from utils.openai_utils import openai_call
import asyncio


async def summarize(text: str, words: int = 100):
    system_prompt = ("You are an expert in understanding large context and summarizing them to keep only relevant and "
                     "important information")
    messages = [{"role": "user", "content": text + f"\n. Summarize the above text in less than {words} words."}]
    _response, _ = await openai_call(system_prompt, messages)
    return _response["results"]
