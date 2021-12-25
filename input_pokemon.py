class InputPokemon:
  def __init__(self, name, egg_move=None):
    self.name = ""
    self.original_name = name
    self.egg_move = egg_move
    self.breed_with = []

  def prepare(self, base_species_map, eggmove_scraper):
    if self.original_name.lower() not in base_species_map:
      raise Exception(f"Couldn't find any pokemon with the name {self.original_name}")

    self.name = base_species_map[self.original_name.lower()]
    if self.egg_move:
      self.breed_with = set([
        base_species_map[pokemon.lower()] for pokemon in
          eggmove_scraper.get_available_parents(self.name, self.egg_move.lower())
            if pokemon.lower() in base_species_map
      ])

  def __repr__(self):
    egg_move_str = f" (with {self.egg_move})" if self.egg_move else ""
    return self.name + egg_move_str