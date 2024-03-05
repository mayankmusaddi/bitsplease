import requests
import json
import logging
from jsonschema import validate, ValidationError
import time


async def openai_call(
    system_prompt, prompt, schema, previous_messages=[], max_attempts=3
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
                prompt,
                previous_messages=previous_messages,
                response_format={"type": "json_object"},
            )
            print("OUTPUT: ", output, time.time() - start)
            results = json.loads(output)
            if not isinstance(results, list):
                results = [results]
            results = [result for result in results if result]
            for result in results:
                validate(instance=result, schema=schema)
            success = True
        except ValidationError as e:
            error_message = str(e)
            logging.error(f"ValidationError on output: {results} : {error_message}")
            prompt = (
                f"{error_message}"
                "Error: The output you sent is not in the correct JSON format. "
                "Stick to the JSON schema specified. Do not apologize"
            )
        except Exception as e:
            error_message = str(e)
            logging.error(f"JSONDecodeError: {output} : {error_message}")
            prompt = (
                "Error: The output you sent is not a valid JSON. "
                "Do not return anything except a JSON. Do not apologize"
            )

    response = {
        "results": results,
        "s": success,
        "eM": error_message,
        "time": time.time() - start,
    }
    return response, previous_messages


def llm_router_call(messages):
    headers = {'Content-Type': 'application/json'}
    payload = {
        "model": "gpt-4-1106-preview",
        "messages": messages,
        "client_identifier": "aih_9"
    }
    url = "http://intuitionx-llm-router.prod0-k8singress-pz-intuition3.sprinklr.com/chat-completion"
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # If the request was successful (status code 200), then return the JSON response
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


async def get_openai_output(
    system_prompt, prompt, previous_messages=[], response_format={"type": "text"}
):
    try:
        system_message = {"role": "system", "content": system_prompt}
        current_message = {"role": "user", "content": prompt}

        if len(previous_messages) == 0:
            previous_messages.append(system_message)
        else:
            if previous_messages[0]["role"] == "system":
                previous_messages[0] = system_message
            else:
                previous_messages = [system_message] + previous_messages
        previous_messages.append(current_message)

        response = llm_router_call(previous_messages)
        content = response.choices[0].message.content
        messages = previous_messages + [{"role": "assistant", "content": content}]
        return content, messages
    except Exception as e:
        raise e
