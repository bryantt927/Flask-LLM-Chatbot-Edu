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
i = 1

# Find an available chat history file
while os.path.exists(os.path.join(cwd, f'chat_history{i}.txt')):
    i += 1

history_file = os.path.join(cwd, f'chat_history{i}.txt')

# Create a new chat history file
with open(history_file, 'w') as f:
    f.write('\n')

# Initialize chat history
chat_history = ''

# Function to complete chat input using OpenAI's GPT-3.5 Turbo
def chatcompletion(user_input, varName, varPrompt, varCustomVariable1, varCustomVariable2, explicit_input, chat_history):
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

    return chatgpt_output

# Function to handle user chat input
def chat(user_input, varName, varPrompt, varCustomVariable1, varCustomVariable2):
    global chat_history, name, chatgpt_output
    name = varName 
    current_day = time.strftime("%d/%m", time.localtime())
    current_time = time.strftime("%H:%M:%S", time.localtime())
    chat_history += f'\nUser: {user_input}\n'
    chatgpt_raw_output = chatcompletion(user_input, varName, varPrompt, varCustomVariable1, varCustomVariable2, explicit_input, chat_history).replace(f'{name}:', '')
    chatgpt_output = f'{name}: {chatgpt_raw_output}'
    chat_history += chatgpt_output + '\n'
    with open(history_file, 'a') as f:
        f.write('\n'+ current_day+ ' '+ current_time+ ' User: ' +user_input +' \n' + current_day+ ' ' + current_time+  ' ' +  chatgpt_output + '\n')
        f.close()
    return chatgpt_raw_output

# Function to get a response from the chatbot
def get_response(userText, varName, varPrompt, varCustomVariable1, varCustomVariable2):
    return chat(userText, varName, varPrompt, varCustomVariable1, varCustomVariable2)

# Define app routes

# You only need this route if you are not embedding this html into a webpage or your LMS
@app.route("/")
def set_cookie():
    print("in root route")
    print("Session is " + str(session.get('logged_in')) + " START")  
    if session.get('logged_in') == True:
        print("already logged in, add to log file")
    elif session.get('logged_in') != True:
        session['logged_in'] = True
        print("logging in user now, create new file")
    print("Session is " + str(session.get('logged_in')) + " END")
    response = make_response("Cookie set!") 
    #print("response headers ONE" + response.headers)
    response.set_cookie("username", "John Doe", path="/", domain="chatbot.dickinson.edu") 
          # Initializing response object 
    print(response.headers)
    return response

    #return render_template("index.html")
    #resp = make_response(render_template("index.html"))
    #resp.set_cookie('somecookiename', 'I am cookie')
    #return resp 

@app.route("/get")
# Function for the bot response
def get_bot_response():
    print("GET Route Session is " + str(session.get('logged_in')) + " START") 
    username = request.cookies.get("username")
    print("Username is " + str(username))
    if session.get('logged_in') == True:
        print("already logged in, add to log file GET")
    elif session.get('logged_in') != True:
        session['logged_in'] = True
        print("logging in user now, create new file GET")
    userText = request.args.get('msg')
    varName = request.args.get('varName')
    varPrompt = request.args.get('varPrompt')
    varCustomVariable1 = request.args.get('varCustomVariable1')
    varCustomVariable2 = request.args.get('varCustomVariable2')
    return str(get_response(userText, varName, varPrompt, varCustomVariable1, varCustomVariable2))

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
    app.run(ssl_context=context, host='0.0.0.0', port=8030, debug=True)
    

