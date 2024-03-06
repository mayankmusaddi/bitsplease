async def fetch_specific_product_description(product: str):
    """
    Returns detailed description of a specific Sprinklr product.
    """
    import aiofiles
    import ast
    import os
    from utils.openai_utils import openai_call

    # current_dir = os.getcwd()
    # file_path = os.path.join(current_dir, '/kb/spr_products_long.txt')
    async with aiofiles.open("./tools/spr_products_long.txt", mode='r') as file:
        contents = await file.read()
    mapping = ast.literal_eval(str(contents))
    
    system_prompt = ("You are an expert in understanding large data and answering queries based on it.")
    messages = [{"role": "user", "content": f"This is a detailed mapping of Sprinklr products and their descriptions: {mapping}.\n Your response should only be the detailed description of the {product.title()} product."}]
    _response, _ = await openai_call(system_prompt, messages)
    return _response["results"]
