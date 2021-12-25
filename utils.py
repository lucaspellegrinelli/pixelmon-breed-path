class Logger:
  verbose = True
  @staticmethod
  def log_current_step(text):
    if Logger.verbose:
      print(f" * {text}")

def list_intersec(a, b):
  return list(set(a) & set(b))

def intersec(a, b):
  return len(list_intersec(a, b)) > 0