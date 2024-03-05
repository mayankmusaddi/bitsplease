import requests
import json
import logging
from jsonschema import validate, ValidationError
import time


async def openai_call(
    system_prompt, messages=[], schema=None, response_format={"type": "text"}, max_attempts=3
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
                response_format,
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


def llm_router_call(messages, response_format):
    headers = {'Content-Type': 'application/json'}
    payload = {
        "model": "gpt-4-32k",
        "messages": messages,
        "client_identifier": "backend"
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
    system_prompt, messages, response_format
):
    try:
        system_message = {"role": "system", "content": system_prompt}
        messages = [system_message] + messages
        response = llm_router_call(messages, response_format)
        content = response["choices"][0]["message"]["content"]
        messages = messages + [{"role": "assistant", "content": content}]
        return content, messages
    except Exception as e:
        raise e
