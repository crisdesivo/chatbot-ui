import gradio as gr
import openai
from gradio.outputs import Label
import webbrowser
import json

# openai.api_key = open("key.txt", "r").read().strip("\n")

def check_openai_key():
    try:
        # use a cheap engine to check if the key is valid
        openai.Completion.create(engine="text-ada-001", prompt="H", max_tokens=1)
    except openai.error.AuthenticationError:
        return False
    return True



INITIAL_MESSAGES_AMOUNT = None

def predict(input, message_history, chatbot, message_history_var):
    # tokenize the new input sentence
    message_history.append({"role": "user", "content": f"{input}"})

    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo", #10x cheaper than davinci, and better. $0.002 per 1k tokens
      messages=message_history
    )
    print(completion)
    #Just the reply:
    reply_content = completion.choices[0].message.content#.replace('```python', '<pre>').replace('```', '</pre>')

    print(reply_content)
    message_history.append({"role": "assistant", "content": f"{reply_content}"}) 
    
    response = [(message_history[i]["content"], message_history[i+1]["content"]) for i in range(INITIAL_MESSAGES_AMOUNT, len(message_history)-1, 2)]  # convert to tuples of list

    rdic = {
        chatbot: response,
        message_history_var: message_history
    }
    return rdic

def set_openai_key(key):
    openai.api_key = key
    if check_openai_key():
        return True
    return False

def go_to_doc():
    url = "https://platform.openai.com/account/api-keys"
    webbrowser.open(url)

def gradio_app(initial_message_history):
    # creates a new Blocks app and assigns it to the variable demo.
    with gr.Blocks() as demo:
        # save the message history to local storage
        message_history_var = gr.State(initial_message_history)

        # System message label at the top
        system_message = gr.Markdown("Please enter your OpenAI API key to start the chatbot.")
        with gr.Column():
            docButton = gr.Button("Get OpenAI api key").style(container=False, scale=0.2)
            docButton.click(go_to_doc)

            key = gr.Textbox(show_label=False, placeholder="Enter your OpenAI API key").style(container=False)

        # key.submit(set_openai_key, key)
        chatbot = gr.Chatbot()
        chatbot.visible = False
        with gr.Row().style(container=True):
            txt = gr.Textbox(show_label=False, placeholder="Enter text and press enter").style(container=False)
            txt.visible = False
            # txt.add(docButton)


        def show_chatbot(key_):
            set_openai_key(key_)
            if check_openai_key():
                print("OpenAI key is valid")
                return {
                    chatbot: gr.update(visible=True),
                    txt: gr.update(visible=True),
                    system_message: gr.update(value="Chatbot is ready. Enter text and press enter to start chatting.")
                }
            else:
                print("OpenAI key is invalid")
                return {
                    chatbot: gr.update(visible=False),
                    txt: gr.update(visible=False),
                    system_message: gr.update(value="OpenAI key is invalid. Please enter a valid OpenAI key.")
                }
        key.submit(show_chatbot, key, [chatbot, txt, system_message])
        txt.submit(lambda x,y: predict(x, y, chatbot, message_history_var), [txt, message_history_var], [chatbot, message_history_var]) # submit(function, input, output)
        txt.submit(None, None, txt, _js="() => {''}") # No function, no input to that function, submit action to textbox is a js function that returns empty string, so it clears immediately.
    demo.launch()

# def gradio_app(message_history):
#     # creates a new Blocks app and assigns it to the variable demo.
#     with gr.Blocks() as demo: 
#         key = gr.Textbox(show_label=False, placeholder="Enter your OpenAI API key").style(container=False)
#         key.submit(set_openai_key, key)
        
#         chatbot = None # initialize chatbot as None
        
#         with gr.Row(): 
#             txt = gr.Textbox(show_label=False, placeholder="Enter text and press enter").style(container=False)
        
#         def submit_handler(textbox_value):
#             nonlocal chatbot # use nonlocal to modify the chatbot variable in the parent function
            
#             # check if the OpenAI key is valid
#             if check_openai_key():
#                 # if the key is valid, show the chatbot
#                 if chatbot is None:
#                     chatbot = gr.Chatbot()
#                     demo.add(chatbot) # add the new chatbot widget
#                 else:
#                     demo.remove(chatbot) # remove the old chatbot widget
#                     new_chatbot = gr.Chatbot()
#                     demo.add(new_chatbot) # add the new chatbot widget
#                     chatbot = new_chatbot
                
#                 predict(textbox_value, message_history, chatbot)
#                 demo.submit(txt) # clear textbox
#             else:
#                 # if the key is not valid, hide the chatbot and show an error message
#                 if chatbot is not None:
#                     demo.remove(chatbot)
#                 error_msg = Label("Invalid OpenAI API key. Please try again.")
#                 demo.add(error_msg)
#                 chatbot = None
        
#         txt.submit(submit_handler, txt) # use submit_handler instead of lambda function
        
#     demo.launch()


if __name__ == "__main__":
    from rephrase_bot import prompt
    INITIAL_MESSAGES_AMOUNT = len(prompt)
    gradio_app(prompt.copy())