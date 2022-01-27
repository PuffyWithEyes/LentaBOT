import os
from dotenv import load_dotenv

load_dotenv('.env')

""" Импортируем токен из файла ".env" """
TOKEN = os.environ['TOKEN']
