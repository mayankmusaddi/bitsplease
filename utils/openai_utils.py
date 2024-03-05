import requests
import json
import logging
from jsonschema import validate, ValidationError
import time


async def openai_call(
    system_prompt, messages=[], schema=None, response_format={"type": "text"}, tools=[], max_attempts=3
):
    start = time.time()

    results = []
    success = False
    error_message = ""

    attempts = 0
    while not success and attempts < max_attempts:
        try:
            attempts += 1
            output, previous_messages = await get_openai_output(
                system_prompt,
                messages,
                response_format=response_format,
                tools=tools,
            )
            print("OUTPUT: ", output, time.time() - start)
            if response_format["type"] == "json_object":
                results = json.loads(output)
                if not isinstance(results, list):
                    results = [results]
                results = [result for result in results if result]
                for result in results:
                    validate(instance=result, schema=schema)
                success = True
            else:
                success = True
                results = output
        except ValidationError as e:
            error_message = str(e)
            logging.error(f"ValidationError on output: {results} : {error_message}")
            prompt = (
                f"{error_message}"
                "Error: The output you sent is not in the correct JSON format. "
                "Stick to the JSON schema specified. Do not apologize"
            )
            messages.append({"role": "user", "content": prompt})
        except Exception as e:
            error_message = str(e)
            logging.error(f"JSONDecodeError: {output} : {error_message}")
            prompt = (
                "Error: The output you sent is not a valid JSON. "
                "Do not return anything except a JSON. Do not apologize"
            )
            messages.append({"role": "user", "content": prompt})

    response = {
        "results": results,
        "s": success,
        "eM": error_message,
        "time": time.time() - start,
    }
    return response, previous_messages


def llm_router_call(messages, response_format, tools=[]):
    headers = {'Content-Type': 'application/json'}
    payload = {
        "client_identifier": "aih_9",
        "model": "gpt-4-turbo-preview",
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
    }
    url = "https://prod0-intuitionx-llm-router.sprinklr.com/chat-completion"
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # If the request was successful (status code 200), then return the JSON response
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


async def get_openai_output(
    system_prompt, messages, response_format={"type": "text"}, tools=[]
):
    try:
        system_message = {"role": "system", "content": system_prompt}
        messages = [system_message] + messages
        response = llm_router_call(messages, response_format, tools)
        print("LLM RESPONSE: ", response)

        response_message = response["choices"][0]["message"]
        messages.append(response_message)
        if "tool_calls" in response_message and response_message["tool_calls"]:
            tool_calls = response_message["tool_calls"]
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])

                # function_to_call = available_functions[function_name]
                # function_response = function_to_call(
                #     location=function_args.get("location"),
                #     unit=function_args.get("unit"),
                # )

                print("Calling function:", function_name, function_args)
                function_response = {"response": "shahrukh khan is a popular bollywood actor"}
                messages.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )  # extend conversation with function response
            return await get_openai_output(system_prompt, messages, response_format=response_format, tools=tools)
        if "content" in response_message:
            content = response_message["content"]
            return content, messages
    except Exception as e:
        raise e
