import json
import yaml
import time
import requests
import graphviz as gv
import streamlit as st

from utils.db_store import store

SYSTEM = "system"
USER = "user"
ASSISTANT = "assistant"

# Set layout to wide
st.set_page_config(layout="wide")

# Divide the page into 3 columns
col1, col2, col3 = st.columns(3)


def convert_json_to_flow_chart(data):
    # Create a new directed graph
    g = gv.Digraph(format='svg')

    # Add nodes to the graph
    for node in data['task_nodes']:
        g.node(node['task_id'], node['task'])

    # Add edges to the graph
    for link in data['task_links']:
        g.edge(link['source'], link['target'])

    return g


def get_script_data():
    with open('script.yaml', 'r') as yaml_file:
        script_data = yaml.safe_load(yaml_file)  # Load YAML data
    return script_data


def update_cols():
    # Get the current content of the files
    with open('db_file.json') as f1, open('dag.json') as f2:
        current_content1 = f1.read()
        current_content2 = f2.read()

    # Update and display JSON content in the left and right columns
    print(f"debug 2: {current_content1}, {current_content2}")
    st.session_state.current_content1 = json.loads(current_content1)
    st.session_state.current_content2 = convert_json_to_flow_chart(json.loads(current_content2))


def on_user_input():
    user_input = st.session_state.user_input
    script_stage = st.session_state.script_stage
    script_data = st.session_state.script_data

    # col2.chat_message(USER).write(user_input)
    st.session_state.messages.append({"role": USER, "content": user_input})
    messages = st.session_state.messages.copy()

    messages.append({"role": SYSTEM, "content": script_data[script_stage]['SYSTEM_PROMPT']})
    payload = {"messages": messages}

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
    if script_stage == "collect_persona" and script_data[script_stage]['PROBING_KEYWORD'] in bot_answer:
        for key, value in bot_answer[script_data[script_stage]['PROBING_KEYWORD']].items():
            try:
                store.fetch(key)
                store.update(key, value)
            except Exception as e:
                store.add(key, value)
        st.session_state.script_stage = "assemble_user_tasks"
    elif script_stage == "assemble_user_tasks" and script_data[script_stage]['PROBING_KEYWORD'] in bot_answer:
        for key, value in bot_answer[script_data[script_stage]['PROBING_KEYWORD']].items():
            try:
                store.fetch(key)
            except Exception as e:
                store.add(key, value)
        st.session_state.script_stage = "finished"
    # col2.chat_message(ASSISTANT).write(bot_answer)
    st.session_state.messages.append({"role": ASSISTANT, "content": bot_resp})


def app():
    if "last_content1" not in st.session_state:
        st.session_state.last_content1 = None

    if "last_content2" not in st.session_state:
        st.session_state.last_content2 = None

    if "script_data" not in st.session_state:
        st.session_state.script_data = get_script_data()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "script_stage" not in st.session_state:
        st.session_state.script_stage = "collect_persona"

    if "current_content1" not in st.session_state:
        with open('db_file.json') as f1:
            current_content1 = f1.read()
        st.session_state.current_content1 = json.loads(current_content1)

    if "current_content2" not in st.session_state:
        with open('dag.json') as f2:
            current_content2 = f2.read()
        st.session_state.current_content2 = convert_json_to_flow_chart(json.loads(current_content2))

    # Display data in the left column
    col1.title("Persona details")
    col1.json(st.session_state.current_content1)

    for i, message in enumerate(st.session_state.messages):  # display all the previous message
        col2.chat_message(message["role"]).write(message["content"])

    # Display data in the right column as a flow chart
    col3.title("Flow Chart")
    col3.graphviz_chart(st.session_state.current_content2)

    st.chat_input("Enter a user message here.", key="user_input", on_submit=on_user_input)


if __name__ == "__main__":
    app()
    while True:
        update_cols()
        print("debug 1")
        time.sleep(2)

