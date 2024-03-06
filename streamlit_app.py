import json
import streamlit as st
import requests

USER = "user"
ASSISTANT = "assistant"


def app():
    st.title("BitsPleaseBot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for i, message in enumerate(
        st.session_state.messages
    ):  # display all the previous message
        st.chat_message(message["role"]).write(message["content"])

    user_input = st.chat_input("you")
    if user_input:
        st.chat_message(USER).write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input + " Use multiple web_search calls to plan if needed, always share reference, use execute_python_code whenever you can, ensure units are respected or write another function to change units "})

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
        st.chat_message(ASSISTANT).write(bot_answer)
        st.session_state.messages.append({"role": "assistant", "content": bot_resp})


app()
