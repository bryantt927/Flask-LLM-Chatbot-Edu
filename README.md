# Flask-LLM-Chatbot-Edu
A Flask chatbot application that can run on a server with Flask and Python installed.  Copy and paste the html from templates/index.html into any page on your LMS or CMS

![Python Version](https://img.shields.io/badge/Python-3.9-blue)
![Flask Version](https://img.shields.io/badge/Flask-3.0.2-green)


## Features

- Embed a chatbot that interfaces with the OpenAI API by adding html and javascript into any website
- Set the name of your bot and introductory prompt with whom you students can converse

## Getting Started

### Prerequisites

- Ley from OpenAI for their API
- Python 3.7+ installed on your system.
- Flask 2.0.1 and OpenAI Python SDK installed.
- Set up your OpenAI API key.

### Installation

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/bryantt927/Flask-LLM-Chatbot.git
    ```

2. 2. Navigate to the project directory:https://github.com/bryantt927/Flask-LLM-Chatbot-Edu
```bash
cd Flask-LLM-Chatbot-Edu
```
3. Install the required Python packages:
```bash
pip install -r requirements.txt
```
This command will install required Python packages and dependencies required for your chatbot application.

4. Configure your OpenAI API key:
You will want need to make changes to files for your local installation

a. Open .env in a text editor or code editor of your choice and set the variables

b. Open /templates/index.html in a text editor or code editor of your choice.  You will likely want to change the commented html for the following

- <div class="title">Enter the description of your conversation or activity here for the chatbot:</div>
- https://dknlampstu2.dickinson.edu:8030/get  (change to url being used by webserver running Flask and port)
- url: "https://dknlampstu2.dickinson.edu:8030", (same)
- varName (the name of the bot, currently 'Tadao')
- varPrompt (the prompt that will define the bots context and behavior)


5. Usage

a. Start the Flask app:
```bash
python app.py
```
b. Open your web browser and go to a webpage where the bot will appear

c. Edit the page and copy and paste the html from templates/index.html  (Note, many wysiwyg editor will remove CSS and Script tags you will need. You can often prevent this by choosing "plain text" as your editor.

Your chatbot app is now fully configured and ready for use. 

