async def fetch_all_products_description(): 
    """
    Function to return few-line description of all products offered by Sprinklr.
    """
    import aiofiles
    import ast
    import os
    
    # current_dir = os.getcwd()
    # file_path = os.path.join(current_dir, '/kb/spr_products_short.txt')
    async with aiofiles.open("./tools/spr_products_short.txt", mode='r') as file:
        contents = await file.read()

    return ast.literal_eval(str(contents))
