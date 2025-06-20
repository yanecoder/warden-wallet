import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = os.getenv("SECRET_KEY") or os.urandom(16).hex()

from app import routes
