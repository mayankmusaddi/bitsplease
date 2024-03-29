async def fetch_vertical_specific_products(vertical: str):
    """
    Returns all of Sprinklr's products that can be pitched to a company under the specified vertical.
    """
    import aiofiles
    import os
    from utils.openai_utils import openai_call

    current_dir = os.getcwd()
    print(current_dir)
    # file_path = os.path.join(current_dir, '/kb/vertical_product_map.txt')
    async with aiofiles.open("./tools/vertical_product_map.txt", mode='r') as file:
        mapping = await file.read()
    
    system_prompt = ("You are an expert in understanding large data and how to answer queries based on it. You help in understanding which CRM/CXM products can be pitched to clients.")
    messages = [{"role": "user", "content": f"This is a mapping of Sprinklr products can be suggested to companies of specific vertical industries: {mapping}.\n Your response should only be the list of products that can be pitched to a company belonging to the {vertical} industry."}]
    _response, _ = await openai_call(system_prompt, messages)
    return _response["results"]
