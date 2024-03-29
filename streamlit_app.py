import json
import yaml
import time
import requests
import graphviz as gv
import asyncio
import streamlit as st

from utils.db_store import store, dag_store
from tools.generate_dag import generate_dag
from tools.generate_persona import generate_persona

SYSTEM = "system"
USER = "user"
ASSISTANT = "assistant"

# Set layout to wide
st.set_page_config(layout="wide")

# Divide the page into 3 columns
col1, col2, col3 = st.columns(3)

hide_streamlit_style = """
                <style>
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def convert_json_to_flow_chart(data):
    # Create a new directed graph
    g = gv.Digraph(format='svg')

    # Add nodes to the graph
    for node in data['task_nodes']:
        g.node(node['task_id'], node['name'] + "\n" + node['task'])

    # Add edges to the graph
    for link in data['task_links']:
        g.edge(link['source'], link['target'])

    return g


with open('tools/tools.yaml', 'r') as yaml_file:
    tools = yaml.safe_load(yaml_file)  # Load YAML data


def get_script_data():
    with open('script.yaml', 'r') as yaml_file:
        script_data = yaml.safe_load(yaml_file)  # Load YAML data
    return script_data


def update_cols():
    # Get the current content of the first file
    try:
        with open('db_file.json') as f1:
            current_content1 = f1.read()
            if current_content1:  # Check if the file is not empty
                # Parse the JSON data
                st.session_state.current_content1 = json.loads(current_content1)

    except FileNotFoundError:
        st.error('Persona file not found.')
    except json.JSONDecodeError:
        st.error('Error decoding JSON in db_file.json')

    # Get the current content of the second file
    try:
        with open('dag.json') as f2:
            current_content2 = f2.read()
            if current_content2:  # Check if the file is not empty
                # Parse the JSON data
                st.session_state.current_content2 = convert_json_to_flow_chart(json.loads(current_content2))

    except FileNotFoundError:
        st.error('DAG file not found.')
    except json.JSONDecodeError:
        st.error('Error decoding JSON in dag.json')

    # Wait for 2 seconds before checking again
    time.sleep(5)
    st.rerun()


def on_user_input():
    global col2
    user_input = st.session_state.user_input
    script_stage = st.session_state.script_stage
    script_data = st.session_state.script_data

    st.session_state.messages.append({"role": USER, "content": user_input})
    messages = st.session_state.messages.copy()
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
    print(script_stage)
    print(bot_answer)
    print(script_data)
    st.session_state.messages.append({"role": ASSISTANT, "content": bot_resp})

    if script_stage == "collect_persona" and script_data[script_stage]['PROBING_KEYWORD'] == bot_answer:
        persona = asyncio.run(generate_persona(st.session_state.messages))
        print(f"PERSONA: {persona}")
        for key, value in persona.items():
            try:
                store.fetch(key)
                store.update(key, value)
            except Exception as e:
                store.add(key, value)
        st.session_state.messages = []
        st.session_state.script_stage = "assemble_user_tasks"
        col2 = st.empty()
        return
    elif script_stage == "assemble_user_tasks" and script_data[script_stage]['PROBING_KEYWORD'] != bot_answer  :
        messages = st.session_state.messages
        print(bot_answer)
        if "TASK_STEPS" in bot_answer:
            dag_json = asyncio.run(generate_dag([messages[-1]], tools))
            print("DAG " +  str(dag_json))
            for key, value in dag_json.items():
                try:
                    dag_store.fetch(key)
                    dag_store.update(key, value)
                except Exception:
                    dag_store.add(key, value)
    elif script_stage == "assemble_user_tasks" and script_data[script_stage]['PROBING_KEYWORD'] == bot_answer:
        st.session_state.script_stage = "run_persona"
        st.session_state.messages = []
        col2 = st.empty()
        return


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
        st.session_state.script_stage = "run_persona"

    # Display data in the left column
    col1.title("Persona details")
    if "current_content1" in st.session_state:
        col1.json(st.session_state.current_content1)

    if len(store.fetch_all()) == 0:
        st.session_state.script_stage = "collect_persona"
    elif len(dag_store.fetch_all()) == 0:
        st.session_state.script_stage = "assemble_user_tasks"

    if len([message for message in st.session_state.messages if message['role'] == ASSISTANT]) == 0:
        system_prompt = st.session_state.script_data[st.session_state.script_stage]['SYSTEM_PROMPT']
        if st.session_state.script_stage == "run_persona":
            system_prompt = system_prompt.format(persona=str(store.fetch_all()),
                                                 task_name=str(dag_store.fetch("task_name")),
                                                 input=dag_store.fetch("input"),
                                                 task_steps=dag_store.fetch("task_steps"))
        st.session_state.messages.append(
            {"role": SYSTEM, "content": system_prompt})
        st.session_state.messages.append(
            {"role": ASSISTANT, "content": st.session_state.script_data[st.session_state.script_stage]['INIT_PROMPT']})
    for i, message in enumerate(st.session_state.messages):  # display all the previous message
        if message['role'] != SYSTEM:
            col2.chat_message(message["role"]).write(message["content"])
    col2.chat_input("Enter a user message here.", key="user_input", on_submit=on_user_input)

    # Display data in the right column as a flow chart
    col3.title("Flow Chart")
    if "current_content2" in st.session_state:
        col3.graphviz_chart(st.session_state.current_content2)


if __name__ == "__main__":
    app()
    update_cols()
