# Import necessary libraries
from flask import Flask, render_template, request, redirect, jsonify, session, make_response
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
from urllib.parse import urlparse 
import os
import time
import ssl
import secrets


#include SSL cert and OpenAI key in a .env file
load_dotenv()
CERT_FILE = os.environ['CERT_FILE']
KEY_FILE = os.environ['KEY_FILE']
client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

# Create a Flask web application
app = Flask(__name__)
CORS(app)  # Initialize CORS for the entire app



# Initialize variables for chat history
explicit_input = ""
chatgpt_output = 'Chat log: /n'
cwd = os.getcwd()
chat_history = ''

# Function to complete chat input using OpenAI's GPT-3.5 Turbo
def chatcompletion(user_input, user_name, user_prompt, user_token, custom_variable_1, explicit_input, chat_history):
    output = client.chat.completions.create(model="gpt-3.5-turbo-0301",
    temperature=1,
    presence_penalty=0,
    frequency_penalty=0,
    max_tokens=2000,
    messages=[
        {"role": "system", "content": f"{user_prompt}. Conversation history: {chat_history}"},
        {"role": "user", "content": f"{user_input}. {explicit_input}"},
    ])

    chatgpt_output = output.choices[0].message.content

    return chatgpt_output

# Function to handle user chat input
def chat(user_input, user_name, user_prompt, user_token, custom_variable_1):
    global chat_history, name, chatgpt_output
    
    # Each time only set chat_history equal to users log of chat_history find with token.
    history_file = os.path.join(cwd, f'chat_history{user_token}.txt') 
    f = open(history_file, 'r')
    chat_history = f.read()
    print("Chat history is " + chat_history)
    current_day = time.strftime("%d/%m", time.localtime())
    current_time = time.strftime("%H:%M:%S", time.localtime())
    chat_history += f'\nUser: {user_input}\n'
    chatgpt_raw_output = chatcompletion(user_input, user_name, user_prompt, user_token, custom_variable_1, explicit_input, chat_history).replace(f'{user_name}:', '')
    chatgpt_output = f'{user_name}: {chatgpt_raw_output}'
    chat_history += chatgpt_output + '\n'
#    user_token = varUserToken
    history_file = os.path.join(cwd, f'chat_history{user_token}.txt')
    with open(history_file, 'a') as f:
        f.write('\n'+ current_day+ ' '+ current_time+ ' User: ' +user_input +' \n' + current_day+ ' ' + current_time+  ' ' +  chatgpt_output + '\n')
        f.close()
    return chatgpt_raw_output

# Function to get a response from the chatbot
def get_response(userText, user_name, user_prompt, user_token, custom_variable_1):
    return chat(userText, user_name, user_prompt, user_token, custom_variable_1)

# Define app routes

# This is triggered when the page is loaded, set a cookie so each user has one logfile created
# to maintain history sent to LLM and keep as a log.
@app.route("/", methods=['GET'])
def on_page_load():
    print("in root route")
    user_token = request.args.get('user_token')

    # Find an available chat history file
    if os.path.exists(os.path.join(cwd, f'chat_history{user_token}.txt')):
      history_file = os.path.join(cwd, f'chat_history{user_token}.txt')

    # Create a new chat history file
    else:
      history_file = os.path.join(cwd, f'chat_history{user_token}.txt') 
      f = open(history_file, 'w')
      f.write('\n')

    response = make_response()

    return response



@app.route("/get")
# Function for the bot response
def get_bot_response():
    userText = request.args.get('msg')
    user_name = request.args.get('varName')
    user_prompt = request.args.get('varPrompt')
    user_token = request.args.get('varUserToken')
    custom_variable_1 = request.args.get('varCustomVariable1')



    # Find user's chat history file
    if os.path.exists(os.path.join(cwd, f'chat_history{user_token}.txt')):
      history_file = os.path.join(cwd, f'chat_history{user_token}.txt')

    # Create a new chat history file
    else:
      history_file = os.path.join(cwd, f'chat_history{user_token}.txt') 
      f = open(history_file, 'w')
      f.write('\n')

    return str(get_response(userText, user_name, user_prompt, user_token, custom_variable_1))

@app.route('/refresh')
def refresh():
    time.sleep(600) # Wait for 10 minutes
    return redirect('/refresh')
    

# Create SSL context 
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) 
context.load_cert_chain(CERT_FILE, KEY_FILE)

# Run the Flask app, don't run if launching with wsgi server
if __name__ == "__main__":
    #Recommended to define a specific host url for security and your own port
    app.secret_key = 'bigsecret'
    app.run(ssl_context=context, host='0.0.0.0', port=8030)
    

