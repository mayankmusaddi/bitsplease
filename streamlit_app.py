import streamlit as st
import json
import requests
import time
import yaml
import graphviz as gv

from utils.db_store import store

USER = "user"
ASSISTANT = "assistant"
SCRIPT_FILE_PATH = 'script.yaml'

# Set layout to wide
st.set_page_config(layout="wide")

# Divide the page into 3 columns
col1, col2, col3 = st.columns(3)

# Store the last read content of the files
last_content1 = None
last_content2 = None


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
    global SCRIPT_FILE_PATH
    with open(SCRIPT_FILE_PATH, 'r') as yaml_file:
        script_data = yaml.safe_load(yaml_file)  # Load YAML data
    return script_data

def app():
    global script_stage, last_content1, last_content2
    script_data = get_script_data()
    col2.title("BitsPleaseBot")
    print(st.session_state)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "script_stage" not in st.session_state:
        st.session_state.script_stage = "collect_persona"
    script_stage = st.session_state.script_stage
    # st.session_state.messages.append({"role": "assistant",
    #                                   "content": script_data[script_stage]['INIT_PROMPT']})
    for i, message in enumerate(
            st.session_state.messages
    ):  # display all the previous message
        col2.chat_message(message["role"]).write(message["content"])

    user_input = col2.chat_input("you")
    if user_input:
        col2.chat_message(USER).write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        messages = st.session_state.messages.copy()

        messages.append({"role": "system",
                                          "content": script_data[script_stage]['SYSTEM_PROMPT']})
        payload = {"messages": messages}

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
        col2.chat_message(ASSISTANT).write(bot_answer)
        st.session_state.messages.append({"role": "assistant", "content": bot_resp})

        # Update and display JSON content in the left and right columns every k seconds
        while True:
            # Get the current content of the files
            with open('db_file.json') as f1, open('dag.json') as f2:
                current_content1 = f1.read()
                current_content2 = f2.read()

            # If the content of the first file has changed since the last time it was read, update the data
            if last_content1 != current_content1:
                # Parse the JSON data
                data1 = json.loads(current_content1)

                # Display data in the left column
                col1.title("Persona details")
                col1.json(data1)

                # Update the last read content
                last_content1 = current_content1

            # If the content of the second file has changed since the last time it was read, update the data
            if last_content2 != current_content2:
                # Parse the JSON data
                data2 = json.loads(current_content2)

                # Display data in the right column as a flow chart
                col3.title("Flow Chart")
                # Convert your JSON data to a flow chart
                flow_chart = convert_json_to_flow_chart(data2)
                col3.graphviz_chart(flow_chart)

                # Update the last read content
                last_content2 = current_content2

            # Wait for 2 seconds before checking again
            time.sleep(2)


if __name__ == "__main__":
    app()
