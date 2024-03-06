async def fetch_all_products_description(): 
    """
    Function to return few-line description of all products offered by Sprinklr.
    """
    import aiofiles
    import ast
    async with aiofiles.open('../kb/spr_products_short.txt', mode='r') as file:
        contents = file.read()

    return ast.literal_eval(str(contents))
