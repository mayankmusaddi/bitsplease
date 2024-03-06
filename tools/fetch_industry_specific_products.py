async def fetch_industry_specific_products(vertical: str):
    """
    Returns all of Sprinklr's products that can be pitched to a company under the specified vertical.
    """
    import aiofiles
    import ast
    async with aiofiles.open('../kb/spr_products_short.txt', mode='r') as file:
        contents = file.read()

    return ast.literal_eval(str(contents))
    system_prompt = ("You are an expert in understanding large data and how to answer queries based on it. You help in understanding which CRM/CXM products can be pitched to clients.")
    messages = [{"role": "user", "content": f"This is a mapping of Sprinklr products can be suggested to companies of specific vertical industries: {mapping}"}]
    _response, _ = await openai_call(system_prompt, messages)
    return _response["results"]
