class Logger:
  verbose = True

  @staticmethod
  def log_current_step(text):
    if Logger.verbose:
      print(f" * {text}")