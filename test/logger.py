from datetime import datetime
import logging
from colorama import init

init(autoreset=True)

logging.basicConfig(filename=datetime.now().strftime('logs/validator_log_%Y_%m_%d.log'), level=logging.INFO, format='%(message)s', filemode='w')

def log_print(message):
  print(message)
  logging.info(message)

def log_print_green(message):
  print('\033[32;1m' + message)
  logging.info(message)

def log_print_cyan(message):
  print('\033[36;1m' + message)
  logging.info(message)

def log_print_red(message):
  print('\033[31;1m' + message)
  logging.info(message)

