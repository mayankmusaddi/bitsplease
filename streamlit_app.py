import json
import streamlit as st
import requests
import yaml

USER = "user"
ASSISTANT = "assistant"
SCRIPT_TASK = 0
SCRIPT_STARTED = {}
SCRIPT_FILE_PATH = 'script.yaml'


def get_script_data():
    global SCRIPT_FILE_PATH
    with open(SCRIPT_FILE_PATH, 'r') as yaml_file:
        script_data = yaml.safe_load(yaml_file)  # Load YAML data
    return script_data

def app():
    global SCRIPT_TASK, SCRIPT_STARTED
    script_data = get_script_data()
    st.title("BitsPleaseBot")

    if script_data[SCRIPT_TASK]['name'] in SCRIPT_STARTED:
        st.session_state.messages.append({"role": "system",
                                          "content": script_data[SCRIPT_TASK]['SYSTEM_PROMPT']})
        st.session_state.messages.append({"role": "assistant",
                                          "content": script_data[SCRIPT_TASK]['INIT_PROMPT']})
        SCRIPT_STARTED[script_data[SCRIPT_TASK]['name']] = 1
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for i, message in enumerate(
            st.session_state.messages
    ):  # display all the previous message
        st.chat_message(message["role"]).write(message["content"])

    user_input = st.chat_input("you")
    if user_input:
        st.chat_message(USER).write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input + " Use multiple web_search calls to plan if needed, always share reference, use execute_python_code whenever you can"})

        payload = {"messages": st.session_state.messages}

        with st.spinner("Running"):
            print("REQ: ", payload)
            response = requests.post(
                "http://localhost:10005/predict",
                json=payload,
            )
            response = response.json()
            print("RESP: ", response)

            bot_resp = response["results"]
        bot_answer = bot_resp
        try:
            bot_answer = json.loads(bot_resp)
        except Exception:
            pass
        if SCRIPT_TASK == 0 and bot_answer == script_data[SCRIPT_TASK]['PROBING_KEYWORD']:
            st.session_state.messages.append({"role": "user",
                                              "content": script_data[SCRIPT_TASK]['PROBING_PROMPT']})
            SCRIPT_TASK += 1
            #trigger assemble_user_tasks
        else:
            st.chat_message(ASSISTANT).write(bot_answer)
            st.session_state.messages.append({"role": "assistant", "content": bot_resp})


app()
