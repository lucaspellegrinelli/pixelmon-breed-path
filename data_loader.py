import pandas as pd
import os

from utils import Logger

class DataLoader:
  def __init__(self, data_folder):
    self.data_folder = data_folder

  def load_all_dataframes(self):
    Logger.log_current_step("Loading pokemon data")
    pokemons_df = pd.read_csv(os.path.join(self.data_folder, "pokemon.csv"))
    species_df = pd.read_csv(os.path.join(self.data_folder, "pokemon_species.csv"))
    egg_groups_df = pd.read_csv(os.path.join(self.data_folder, "pokemon_egg_groups.csv"))
    types_df = pd.read_csv(os.path.join(self.data_folder, "pokemon_types.csv"))
    type_names_df = pd.read_csv(os.path.join(self.data_folder, "types.csv"))
    egg_groups_names_df = pd.read_csv(os.path.join(self.data_folder, "egg_groups.csv"))

    # The usual name for "indeterminate" egg group is "amorphous"
    egg_groups_names_df.loc[egg_groups_names_df["identifier"] == "indeterminate", "identifier"] = "amorphous"

    types_df = types_df.merge(type_names_df, left_on="type_id", right_on="id")
    egg_groups_df = egg_groups_df.merge(egg_groups_names_df, left_on="egg_group_id", right_on="id")
    return pokemons_df, species_df, egg_groups_df, types_df

  def get_pokemon_info(self):
    pokemons_df, species_df, egg_groups_df, types_df = self.load_all_dataframes()

    # Adds 'base_species_id' to species_df. This is the ID of the first evolution of an evolution chain
    base_form_id = {}
    Logger.log_current_step("Preprocessing pokemon data")
    for _, row in species_df.iterrows():
      if not pd.isna(row["evolves_from_species_id"]):
        if row["evolves_from_species_id"] not in base_form_id:
          base_form_id[row["id"]] = row["evolves_from_species_id"]
        else:
          base_form_id[row["id"]] = base_form_id[row["evolves_from_species_id"]]
      else:
        base_form_id[row["id"]] = row["id"]

    species_df["base_species_id"] = base_form_id.values()

    # Creates an array of objects which represents each pokemon. Each object has the pokemon id, base evolution id,
    # name, types and egg groups.
    all_pokemon_info = []
    for _, row in pokemons_df.iterrows():
      species = species_df[species_df["id"] == row["species_id"]].iloc[0]
      types = types_df[types_df["pokemon_id"] == row["id"]]["identifier"].to_list()
      egg_groups = egg_groups_df[egg_groups_df["species_id"] == species["id"]]["identifier"].to_list()

      all_pokemon_info.append({
        "id": row["id"],
        "name": row["identifier"],
        "base_species_id": int(species["base_species_id"]),
        "type_1": types[0],
        "type_2": types[1] if len(types) > 1 else "none",
        "egg_group_1": egg_groups[0],
        "egg_group_2": egg_groups[1] if len(egg_groups) > 1 else "none",
        "types": types,
        "egg_groups": egg_groups
      })

    # Removes evolutions that change nothing in types/egg groups so we don't end up with unnecesary nodes
    # in the final graph
    pokemon_info_df = pd.DataFrame.from_dict(all_pokemon_info)
    grouped_pokemon_info_df = pokemon_info_df.groupby(by=["type_1", "type_2", "egg_group_1", "egg_group_2", "base_species_id"], as_index=False)
    
    base_species_map = {}
    for _, value in grouped_pokemon_info_df.groups.items():
      base_species = pokemon_info_df.iloc[min(value)]
      for pkm_df_id in value:
        pkm = pokemon_info_df.iloc[pkm_df_id]
        base_species_map[pkm["name"]] = base_species["name"]

    grouped_pokemon_info_df = grouped_pokemon_info_df.first().sort_values(by="id").reset_index(drop=True)
    grouped_pokemon_info_df = grouped_pokemon_info_df.set_index("name")
    return grouped_pokemon_info_df.to_dict("index"), base_species_map