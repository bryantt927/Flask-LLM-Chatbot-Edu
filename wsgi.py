from app import app as application  # Assuming app.py is named yourapplication

if __name__ == "__main__":
  import sys
  sys.path.insert(0, '/var/www/html/FlaskChatbot/Flask-LLM-Chatbot-Edu')  # Adjust the path accordingly

  # Recommended for production: Avoid multiple workers reloading code
  application = create_app()  # If using app factory pattern

  from wsgiref.simple_server import make_server
  httpd = make_server('', 8030, application)  # Port 8030 for demonstration
  print("Serving on port 8030")
  httpd.serve_forever()
