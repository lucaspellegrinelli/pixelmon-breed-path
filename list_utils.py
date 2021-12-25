def list_intersec(a, b):
  return list(set(a) & set(b))

def intersec(a, b):
  return len(list_intersec(a, b)) > 0