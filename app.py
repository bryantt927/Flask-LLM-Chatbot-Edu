# Import necessary libraries
from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
from urllib.parse import urlparse 
import os
import time
import ssl
import uuid


#include SSL cert and OpenAI key in a .env file
load_dotenv()
CERT_FILE = os.environ['CERT_FILE']
KEY_FILE = os.environ['KEY_FILE']
client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

explicit_input=''
# Create a Flask web application
app = Flask(__name__)
CORS(app)  # Initialize CORS for the entire app

user_id = str(uuid.uuid4())
cwd = os.getcwd()
history_file = os.path.join(cwd, f'chat_history{user_id}.txt')

# Function to complete chat input using OpenAI's GPT-3.5 Turbo
def chatcompletion(user_input, varName, varPrompt, varCustomVariable1, varCustomVariable2, chat_history):
    output = client.chat.completions.create(model="gpt-3.5-turbo-0301",
    temperature=1,
    presence_penalty=0,
    frequency_penalty=0,
    max_tokens=2000,
    messages=[
        {"role": "system", "content": f"{varPrompt}. Conversation history: {chat_history}"},
        {"role": "user", "content": f"{user_input}. {explicit_input}"},
    ])

    chatgpt_output = output.choices[0].message.content
    updated_chat_history = chat_history + f'\nUser: {user_input}\nArabicBot: {chatgpt_output}\n'
    return chatgpt_output, updated_chat_history

# Function to handle user chat input
def chat(user_input, varName, varPrompt, varCustomVariable1, varCustomVariable2, chat_history, history_file):
    name = varName 
    chatgpt_raw_output, updated_chat_history = chatcompletion(user_input, varName, varPrompt, varCustomVariable1, varCustomVariable2, chat_history)
    with open(history_file, 'a') as f:
        f.write(updated_chat_history)
    return chatgpt_raw_output

# Function to get a response from the chatbot
def get_response(userText, varName, varPrompt, varCustomVariable1, varCustomVariable2, chat_history, history_file):
    return chat(userText, varName, varPrompt, varCustomVariable1, varCustomVariable2, chat_history, history_file)
    
def creat_new_chat_history_file():
    with open(history_file, 'w') as f:
        f.write('\n')
        
creat_new_chat_history_file()

# Define app routes

# You only need this route if you are not embedding this html into a webpage or your LMS
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get")
# Function for the bot response
def get_bot_response():
    userText = request.args.get('msg')
    varName = request.args.get('varName')
    varPrompt = request.args.get('varPrompt')
    varCustomVariable1 = request.args.get('varCustomVariable1')
    varCustomVariable2 = request.args.get('varCustomVariable2')
    chat_history = ''
    response = get_response(userText, varName, varPrompt, varCustomVariable1, varCustomVariable2, chat_history, history_file)
    return str(response)

@app.route('/refresh')
def refresh():
    time.sleep(600) # Wait for 10 minutes
    return redirect('/refresh')
    

# Create SSL context 
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) 
context.load_cert_chain(CERT_FILE, KEY_FILE)

# Run the Flask app
if __name__ == "__main__":
    #Recommended to define a specific host url for security and your own port
    app.run(ssl_context=context, host='0.0.0.0', port=8030)
