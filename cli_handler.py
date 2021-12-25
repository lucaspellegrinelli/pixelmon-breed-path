import argparse

from input_pokemon import InputPokemon

class CLIHandler:
  def __init__(self):
    self.parser = argparse.ArgumentParser()
    self.parser.add_argument("-p", "--pokemons", nargs="+", help="List of pokemons in the team (space separated). Syntax: -p PokemonA PokemonB PokemonC ...", required=True)
    self.parser.add_argument("-em", "--eggmove", action="append", help="Which egg move a pokemon has to have. Syntax: -em Pokemon=Move", required=False)

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

    return input_pokemons