import json
import streamlit as st
import requests
import yaml
from utils.db_store import store

USER = "user"
ASSISTANT = "assistant"
script_stage = "collect_persona"
SCRIPT_FILE_PATH = 'script.yaml'


def get_script_data():
    global SCRIPT_FILE_PATH
    with open(SCRIPT_FILE_PATH, 'r') as yaml_file:
        script_data = yaml.safe_load(yaml_file)  # Load YAML data
    return script_data


def app():
    global script_stage
    script_data = get_script_data()
    st.title("BitsPleaseBot")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.session_state.messages.append({"role": "system",
                                      "content": script_data[script_stage]['SYSTEM_PROMPT']})
    st.session_state.messages.append({"role": "assistant",
                                      "content": script_data[script_stage]['INIT_PROMPT']})
    for i, message in enumerate(
            st.session_state.messages
    ):  # display all the previous message
        st.chat_message(message["role"]).write(message["content"])

    user_input = st.chat_input("you")
    if user_input:
        st.chat_message(USER).write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

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
        print(bot_answer)
        if script_stage == "collect_persona" and script_data[script_stage]['PROBING_KEYWORD'] in bot_answer:
            for key, value in bot_answer[script_data[script_stage]['PROBING_KEYWORD']].items():
                try:
                    store.fetch(key)
                except Exception as e:
                    store.add(key, value)
            script_stage = "assemble_user_tasks"
        st.chat_message(ASSISTANT).write(bot_answer)
        st.session_state.messages.append({"role": "assistant", "content": bot_resp})


app()
