async def fetch_all_products_description(): 
    """
    Function to return few-line description of all products offered by Sprinklr.
    """
    import ast
    import json
    with open('../kb/spr_products_short.txt', 'r') as file:
        contents = file.read()

    return ast.literal_eval(str(contents))
