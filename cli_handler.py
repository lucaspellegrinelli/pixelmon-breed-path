import argparse

from input_pokemon import InputPokemon
from utils import Logger

class CLIHandler:
  def __init__(self):
    self.parser = argparse.ArgumentParser()
    self.parser.add_argument("-p", "--pokemons", nargs="+", help="List of pokemons in the team (space separated). Syntax: -p PokemonA PokemonB PokemonC ...", required=True)
    self.parser.add_argument("-em", "--eggmove", action="append", help="Which egg move a pokemon has to have. Syntax: -em Pokemon=Move", required=False)
    self.parser.add_argument("-v", "--verbose", action="store_true", help="Control if messages reporting the progress of the software will be shown", required=False)
    self.parser.add_argument("-s", "--size", type=int, help="Width and height of the final image in inches", default=15, required=False)
    self.parser.add_argument("-dpi", "--dpi", type=int, help="DPI of the final image in inches", default=200, required=False)

  def parse(self):
    cli_args = self.parser.parse_args()

    egg_moves = {}
    for egg_move_str in cli_args.eggmove:
      target_pkm, target_move = egg_move_str.split("=")
      egg_moves[target_pkm] = target_move
    
    input_pokemons = []
    for pokemon in cli_args.pokemons:
      input_pokemons.append(InputPokemon(
        name=pokemon,
        egg_move=egg_moves[pokemon] if pokemon in egg_moves else None
      ))

    Logger.verbose = cli_args.verbose
    return input_pokemons, cli_args