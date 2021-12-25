import matplotlib.pyplot as plt

from cli_handler import CLIHandler
from data_loader import DataLoader
from breed_graph import BreedGraph
from egg_move_scraper import EggMoveScraper

if __name__ == "__main__":
  cli = CLIHandler()
  input_pokemons = cli.parse()

  data_loader = DataLoader("data/")
  all_pokemon_data, base_species_map = data_loader.get_pokemon_info()

  eggmove_scraper = EggMoveScraper(pixelmon_wiki="https://pixelmonmod.com/wiki/")

  for pokemon in input_pokemons:
    pokemon.prepare(base_species_map, eggmove_scraper)

  plt.figure(1, figsize=(15, 15), dpi=200)
  breed_graph = BreedGraph(all_pokemon_data)
  breed_graph.draw_graph(input_pokemons)
  plt.savefig(f"plots/breed_path.png")