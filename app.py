"""
Event Task Manager Agent - Hugging Face Spaces
Google ADK + Groq + Gradio + MongoDB
"""
import os
import gradio as gr
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import root_agent
from mongo_service import save_message, get_chat_history

session_service = InMemorySessionService()
APP_NAME = "event_task_manager"
USER_ID = "user_1"
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


def get_or_create_session(session_id):
    try:
        return session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    except Exception:
        return session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)


def chat(message, history, session_id):
    get_or_create_session(session_id)
    save_message(session_id, "user", message)
    content = types.Content(role="user", parts=[types.Part(text=message)])
    response_text = ""
    for event in runner.run(user_id=USER_ID, session_id=session_id, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            response_text = event.content.parts[0].text
    save_message(session_id, "assistant", response_text)
    return response_text


def restore_session(session_id_input):
    if not session_id_input.strip():
        return [], "Please enter a valid session ID"
    messages = get_chat_history(session_id_input.strip())
    history = [{"role": m["role"], "content": m["content"]} for m in messages]
    return history, f"✅ Loaded {len(history)} messages!"


with gr.Blocks() as demo:
    session_id_state = gr.State(lambda: f"session_{os.urandom(4).hex()}")
    gr.Markdown("# 🗂️ Event Task Manager Agent")
    gr.Markdown("Built with **Google ADK + Groq** · MongoDB · GDG Cloud Chennai 🎉")

    with gr.Row():
        restore_input = gr.Textbox(placeholder="Enter previous session ID to restore...",
                                   label="🔁 Restore Previous Session", scale=4)
        restore_btn = gr.Button("Restore", variant="secondary", scale=1)
    restore_status = gr.Markdown("")

    chatbot_ui = gr.Chatbot(elem_id="chatbot",
                            placeholder="Ask me to create tasks, log connections, save notes...")
    with gr.Row():
        msg_input = gr.Textbox(placeholder="e.g. Create a task to follow up with ADK speaker",
                               scale=6, show_label=False)
        send_btn = gr.Button("Send 🚀", variant="primary", scale=1)

    gr.Examples(examples=[
        "Create a high priority task to build ADK agent at home",
        "Add speaker John who talked about MCP at GDG Chennai",
        "Save note: ADK supports multi-agent workflows using A2A protocol",
        "Show summary for GDG Cloud Chennai event",
        "List all pending tasks",
    ], inputs=msg_input)

    def submit(message, history, session_id):
        if not message.strip():
            return history, ""
        response = chat(message, history, session_id)
        history = history or []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        return history, ""

    send_btn.click(submit, inputs=[msg_input, chatbot_ui, session_id_state],
                   outputs=[chatbot_ui, msg_input])
    msg_input.submit(submit, inputs=[msg_input, chatbot_ui, session_id_state],
                     outputs=[chatbot_ui, msg_input])

    def restore(session_id_input, current_session):
        sid = session_id_input.strip() or current_session
        history, status = restore_session(sid)
        return history, status, sid

    restore_btn.click(restore, inputs=[restore_input, session_id_state],
                      outputs=[chatbot_ui, restore_status, session_id_state])

if __name__ == "__main__":
    demo.launch()
