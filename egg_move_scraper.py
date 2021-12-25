import requests
from bs4 import BeautifulSoup

from utils import Logger

class EggMoveScraper:
  def __init__(self, pixelmon_wiki):
    self.pixelmon_wiki = pixelmon_wiki[:-1] if pixelmon_wiki[-1] == "/" else pixelmon_wiki

  def get_available_parents(self, pokemon, egg_move):
    wiki_url = f"{self.pixelmon_wiki}/{pokemon.capitalize()}"
    Logger.log_current_step(f"Scrapping {pokemon} egg moves from {wiki_url}")
    req_res = requests.get(f"{self.pixelmon_wiki}/{pokemon.capitalize()}", headers={
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    })
    
    soup = BeautifulSoup(req_res.text, "html.parser")
    eggmoves_table = soup.find(id="By_breeding").parent.findNext("table").findChild("tbody").findChild("table").findChild("tbody")

    move_parents = {}
    for row in eggmoves_table.findChildren("tr"):
      data = row.find_all("td")
      if len(data) > 0:
        parents = data[0].get_text().strip()
        move = data[1].get_text().strip()
        move_parents[move.lower()] = parents.lower()
    
    try:
      return move_parents[egg_move].split(", ")
    except:
      raise Exception(f"Pokemon {pokemon} does not learn {egg_move} by breeding")