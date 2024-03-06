from .web_search import web_search
from .execute_python_code import execute_python_code
from .fetch_specific_product_description import fetch_specific_product_description
from .fetch_all_products_description import fetch_all_products_description
from .fetch_vertical_specific_products import fetch_vertical_specific_products
available_functions = {
    "web_search": web_search,
    "execute_python_code": execute_python_code,
    "fetch_vertical_specific_products": fetch_vertical_specific_products,
    "fetch_all_products_description":fetch_all_products_description,
    "fetch_specific_products_description": fetch_specific_product_description
}