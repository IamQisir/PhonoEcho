import streamlit as st
from ai_chat import AIChat

"""
This file has been deprecated,
because ai_chat.py has been changed,
the file can not run any more
"""

def show_history():
    """Render prior chat messages from session state."""
    for message in st.session_state.messages:
        if message is not None:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def main():
    """Run the deprecated chatbox UI."""
    st.title("エコー発音先生🤖🧠🇦🇮😎")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Initialize AIChat instance
    ai_chat = AIChat()

    # show history chat first
    show_history()

    # Check if error_table exists and is not empty
    if ("ai_initial_input" in st.session_state and 
        st.session_state['ai_initial_input'] is not None and 
        not st.session_state['ai_initial_input'].empty):
        
        # Set the prompt and generate new feedback
        ai_chat.set_prompt(st.session_state['ai_initial_input'])
        
        # Generate initial output
        ai_chat.initial_output()
        # Add initial response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": st.session_state.initial_response
        })
        

    def chat_bot():    
        """Handle user input and stream assistant responses."""
        # React to user input
        if prompt := st.chat_input("聞きたい内容を入れてください"):
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Generate and display assistant response
            response = ai_chat.model.generate_content(prompt, stream=True)
            full_response = ""
            with st.chat_message("assistant"):
                for content in ai_chat.stream_generator(response):
                    st.markdown(content)
                    full_response += content
            st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Run the chat bot
    chat_bot()
    st.session_state['ai_initial_input'] = None

def ai_chat_tab():
    """Render the chat tab UI for the learning page."""
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Initialize AIChat instance
    ai_chat = AIChat()

    # show history chat first
    show_history()

    # Check if error_table exists and is not empty
    if ("ai_initial_input" in st.session_state and 
        st.session_state['ai_initial_input'] is not None and 
        not st.session_state['ai_initial_input'].empty):
        
        # Set the prompt and generate new feedback
        ai_chat.set_prompt(st.session_state['ai_initial_input'])
        
        # Generate initial output
        ai_chat.initial_output()
        # Add initial response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": st.session_state.initial_response
        })
        

    def chat_bot():    
        """Handle user input and stream assistant responses."""
        # React to user input
        if prompt := st.chat_input("聞きたい内容を入れてください"):
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Generate and display assistant response
            response = ai_chat.model.generate_content(prompt, stream=True)
            full_response = ""
            with st.chat_message("assistant"):
                for content in ai_chat.stream_generator(response):
                    st.markdown(content)
                    full_response += content
            st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Run the chat bot
    chat_bot()
    st.session_state['ai_initial_input'] = None

with st.spinner("ロード中"):
    main()
