from consts import VERBOSE

def log_current_step(text):
  if VERBOSE:
    print(f" * {text}")