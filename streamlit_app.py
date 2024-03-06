import streamlit as st
import time
import json
import requests
import yaml
import graphviz as gv

from utils.db_store import store

USER = "user"
ASSISTANT = "assistant"
script_stage = "collect_persona"
SCRIPT_FILE_PATH = 'script.yaml'

# Set layout to wide
st.set_page_config(layout="wide")

# Divide the page into 3 columns
col1, col2, col3 = st.beta_columns(3)

def convert_json_to_flow_chart(data):
    # Create a new directed graph
    g = gv.Digraph(format='svg')

    # Add nodes to the graph
    for i, line in enumerate(data):
        g.node(str(i), line)

    # Add edges to the graph
    for i in range(len(data) - 1):
        g.edge(str(i), str(i + 1))

    # Return the graph
    return g

def get_script_data():
    global SCRIPT_FILE_PATH
    with open(SCRIPT_FILE_PATH, 'r') as yaml_file:
        script_data = yaml.safe_load(yaml_file)  # Load YAML data
    return script_data


def app():
    global script_stage
    script_data = get_script_data()
    col2.title("BitsPleaseBot")
    if "messages" not in st.session_state:
        col2.session_state.messages = []

    col2.session_state.messages.append({"role": "system",
                                          "content": script_data[script_stage]['SYSTEM_PROMPT']})
    col2.session_state.messages.append({"role": "assistant",
                                          "content": script_data[script_stage]['INIT_PROMPT']})
    for i, message in enumerate(
            st.session_state.messages
    ):  # display all the previous message
        col2.chat_message(message["role"]).write(message["content"])

    user_input = col2.chat_input("you")
    if user_input:
        col2.chat_message(USER).write(user_input)
        col2.session_state.messages.append({"role": "user", "content": user_input})

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

    # Update and display JSON content in the left and right columns every k seconds
    while True:
        # Get JSON data from your local files
        with open('db_file.json') as f1, open('dag.json') as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)

        # Display data in the left column
        col1.title("Persona details")
        col1.json(data1)

        # Display data in the right column as a flow chart
        col3.title("Flow Chart")
        # Convert your JSON data to a flow chart
        flow_chart = convert_json_to_flow_chart(data2)
        col3.write(flow_chart)

        # Wait for 2 seconds before updating
        time.sleep(2)

app()
