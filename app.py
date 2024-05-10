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


#Set variables for your local installation in the .env file.  The will be loaded as variables here
load_dotenv()
CERT_FILE = os.environ['CERT_FILE'] #path to your cert file, /etc/directory/blah/name.crt
KEY_FILE = os.environ['KEY_FILE'] #path to your key file, /etc/directory/blah/name.key
HOST = os.environ['HOST']  # ip address of sever, 0.0.0.0
SECRET_KEY = os.environ['SECRET_KEY'] # Can be any random text
PORT = os.environ['PORT'] # PORT open on your sever Flask can use, Flask defaults to 5000
CUTOFF_LINE_INDEX = int(os.environ['CUTOFF_LINE_INDEX']) # Specify the number of interactions to include as a history to the LLM each time starting with the most recent.  By limiting the history, you can prevent excessive charges, but the bot will "forget" any interactions before the cut off.  The full history will still be contained in the text file created in the same directory for each user using their user_token



client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'], # From your OpenAI account, something like sk-iouhiu8883BlahBlah 
)

# Create a Flask web application
app = Flask(__name__)
CORS(app)  # Initialize CORS for the entire app



# Initialize variables for chat history
explicit_input = ""
chatgpt_output = 'Chat log: /n'
cwd = os.getcwd()
chat_history = ''


def find_last_empty_line(chat_history):
  """
  This function finds the indices of all empty lines in a string containing chat history.

  Args:
      chat_history: A string containing the chat conversation.

  Returns:
      A list containing the indices of all empty lines (0-based indexing), 
      with the first index being the closest to the end of the string.
  """
  lines = chat_history.splitlines()  # Split the chat history into lines
  empty_line_indices = []
  for i in range(len(lines) - 1, -1, -1):  # Iterate lines in reverse order
    if not lines[i].strip():
      empty_line_indices.append(i)
  return empty_line_indices

def get_conversation_after_empty_line(chat_history, CUTOFF_LINE_INDEX):
  """
  This function extracts the conversation starting from a specified empty line (counting from the end) 
  from a string containing chat history.

  Args:
      chat_history: A string containing the chat conversation.
      CUTOFF_LINE_INDEX: The index of the empty line to use as the cutoff (counting from the end, 0-based indexing).

  Returns:
      A string containing the conversation starting from the specified empty line, 
      or the entire conversation if there's no variable specified or the cutoff is greater.
  """
  empty_line_indices = find_last_empty_line(chat_history)
  lines = chat_history.splitlines()  # Split the chat history into lines again
  
  if CUTOFF_LINE_INDEX < 0 or CUTOFF_LINE_INDEX >= len(empty_line_indices):
    return "\n".join(lines[len(empty_line_indices):])

  last_empty_line_index = empty_line_indices[CUTOFF_LINE_INDEX]
  return "\n".join(lines[last_empty_line_index + 1:])




# Function to complete chat input using OpenAI's GPT-3.5 Turbo
def chatcompletion(user_input, user_name, user_prompt, user_token, custom_variable_1, explicit_input, chat_history):
    # Specify the empty line index to use as cutoff (0-based indexing)
    chat_history = get_conversation_after_empty_line(chat_history, CUTOFF_LINE_INDEX)
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
    
    # Each time set chat_history equal to user's log of chat_history, find with token.
    history_file = os.path.join(cwd, f'chat_history{user_token}.txt') 
    f = open(history_file, 'r')
    chat_history = f.read()
    current_day = time.strftime("%d/%m", time.localtime())
    current_time = time.strftime("%H:%M:%S", time.localtime())
    chat_history += f'\nUser: {user_input}\n'
    chatgpt_raw_output = chatcompletion(user_input, user_name, user_prompt, user_token, custom_variable_1, explicit_input, chat_history).replace(f'{user_name}:', '')
    chatgpt_output = f'{user_name}: {chatgpt_raw_output}'
    chat_history += chatgpt_output + '\n'
    history_file = os.path.join(cwd, f'chat_history{user_token}.txt')
    with open(history_file, 'a') as f:
        f.write('\n'+ current_day+ ' '+ current_time+ ' User: ' +user_input +' \n' + current_day+ ' ' + current_time+  ' ' +  chatgpt_output + '\n')
        f.close()
    return chatgpt_raw_output

# Function to get a response from the chatbot
def get_response(userText, user_name, user_prompt, user_token, custom_variable_1):
    return chat(userText, user_name, user_prompt, user_token, custom_variable_1)

# Define app routes

# This is triggered when the page is loaded, read the user_token set as cookie in html and sent via query string
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
    # Variables from query string, note varCustomVariable isn't used.  Is there in case would like to customize
    # html further, such as including the LLM model in the html etc.
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
    app.secret_key = SECRET_KEY
    app.run(ssl_context=context, host=HOST, port=PORT)
    

