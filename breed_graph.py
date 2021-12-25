import math
import copy
import networkx as nx

from consts import *
from list_utils import intersec, list_intersec

class BreedGraph:
  def __init__(self, all_pokemon_data):
    self.all_pokemon_data = all_pokemon_data
    self.graph = nx.Graph()

    # Creates an undirected graph where each pokemon is a node and each possible breed is an edge
    breed_pairs = set()
    for pkm_a_name, pkm_a_info in all_pokemon_data.items():
      for pkm_b_name, pkm_b_info in all_pokemon_data.items():
        if pkm_a_name == pkm_b_name: continue
        if intersec(pkm_a_info["types"], pkm_b_info["types"]) and intersec(pkm_a_info["egg_groups"], pkm_b_info["egg_groups"]):
          breed_pairs.add((pkm_a_name, pkm_b_name))

    self.graph.add_nodes_from(all_pokemon_data.items())
    self.graph.add_edges_from(breed_pairs)

  def find_path_to_each_relevant_pokemon(self, input_pokemons):
    """
    Returns a dict with the shortest path to each relevant pokemon. Relevant pokemons are pokemons
    included in the final team as well as pokemon required for egg moves. This will be used in a directed
    graph, so ordering is imoprtant
    """
    non_eggmove_pokemons, all_relevant_pokemons, pokemon_forced_breeds = self.get_egg_move_necessary_pokemons(input_pokemons)

    shortest_path_to_pokemons = {}
    shortest_path_length_to_pokemons = {}

    # Find all shortest paths from 'source_pkm' to 'target_pkm' and store it in 'shortest_path_to_pokemons'
    for source_pkm in all_relevant_pokemons:
      for target_pkm in non_eggmove_pokemons:
        if source_pkm == target_pkm: continue

        # Initialize 'target_pkm' in dict
        if target_pkm not in shortest_path_to_pokemons:
          shortest_path_to_pokemons[target_pkm] = []
          shortest_path_length_to_pokemons[target_pkm] = 99999

        try:
          shortest_paths = list(nx.all_shortest_paths(self.graph, source=source_pkm, target=target_pkm))

          # If source or target pokemon are not in the final team, increase its path length artificially to
          # make up for the fact that it is just a step in the path between two pokemons in the actual team
          is_offset = source_pkm not in [p.name for p in input_pokemons] or target_pkm not in [p.name for p in input_pokemons]
          path_length = len(shortest_paths[0]) + is_offset

          # Update shortest paths to get to the 'target_pkm'
          if not shortest_path_to_pokemons[target_pkm] or path_length < shortest_path_length_to_pokemons[target_pkm]:
            shortest_path_to_pokemons[target_pkm] = shortest_paths
            shortest_path_length_to_pokemons[target_pkm] = path_length
          elif path_length == shortest_path_length_to_pokemons[target_pkm]:
            shortest_path_to_pokemons[target_pkm] += shortest_paths
        except: pass

    # If you can go to pokemon A from pokemon B, you can go the other way around (since we haven't added
    # breed specific pokemons yet!)
    for pkm, paths in copy.deepcopy(shortest_path_to_pokemons).items():
      for path in paths:
        from_pkm = path[0]
        if from_pkm in pokemon_forced_breeds: continue
        if from_pkm not in shortest_path_to_pokemons: shortest_path_to_pokemons[from_pkm] = []
        shortest_path_to_pokemons[from_pkm].append(path[::-1])

    # Adds the pokemons with breed restrictions with the relevant directed path
    for pkm, breed_partners in pokemon_forced_breeds.items():
      if pkm not in shortest_path_to_pokemons: shortest_path_to_pokemons[pkm] = []
      for breed_partner in breed_partners:
        shortest_path_to_pokemons[pkm].append([breed_partner, pkm])

    return shortest_path_to_pokemons

  def get_egg_move_necessary_pokemons(self, input_pokemons):
    non_eggmove_pokemons = set()
    all_relevant_pokemons = set()
    pokemon_forced_breeds = {}

    # For each pokemon with egg moves required, find the pokemons necessary for that egg move that
    # can be reached by other members of the team with the shortest path. These pokemons are added to
    # 'non_eggmove_pokemons' and 'all_relevant_pokemons'. These pokemons are also stored in 'pokemon_forced_breeds'
    # key'd with the target team member.
    for pkm in input_pokemons + input_pokemons[::-1]:
      all_relevant_pokemons.add(pkm.name)
      if len(pkm.breed_with) == 0:
        non_eggmove_pokemons.add(pkm.name)
      else:
        best_breed_partners = set()
        best_breed_partners_dist = 999999

        for team_pkm in input_pokemons + input_pokemons[::-1]:
          if team_pkm.name == pkm.name: continue
          for breed_pkm in pkm.breed_with:
            if breed_pkm not in self.graph: continue
            # (Try to) Find the path between the other team member and this pokemon needed by the egg move
            try:
              shortest_paths = list(nx.all_shortest_paths(self.graph, source=team_pkm.name, target=breed_pkm))

              # If its a best path, set it as the best breed partner, if it is the same path length, add it
              # to the best breed partner options
              if len(shortest_paths[0]) < best_breed_partners_dist:
                best_breed_partners = {breed_pkm}
                best_breed_partners_dist = len(shortest_paths[0])
              elif len(shortest_paths[0]) == best_breed_partners_dist:
                best_breed_partners.add(breed_pkm)
            except: pass

        # Update the sets
        non_eggmove_pokemons |= best_breed_partners
        all_relevant_pokemons |= best_breed_partners
        pokemon_forced_breeds[pkm.name] = best_breed_partners

    return non_eggmove_pokemons, all_relevant_pokemons, pokemon_forced_breeds

  def draw_graph(self, input_pokemons, ax=None):
    paths_to_pokemons = self.find_path_to_each_relevant_pokemon(input_pokemons)
    self.draw_graph_from_paths(input_pokemons, paths_to_pokemons, ax=ax)

  def draw_graph_from_paths(self, input_pokemons, paths_to_pokemons, ax=None):
    # Gathers all included pokemons to be nodes and all connections to be edges
    all_included_pokemons = set([pkm.name for pkm in input_pokemons])
    pokemon_connections = set()
    for paths in paths_to_pokemons.values():
      for path in paths:
        for pkm in path:
          all_included_pokemons.add(pkm)

        for from_pkm, to_pkm in zip(path, path[1:]):
          pokemon_connections.add((from_pkm, to_pkm))

    # Creates a list of node sizes and node colors
    node_sizes = []
    node_colors = []
    for pkm in all_included_pokemons:
      is_main_pkm = pkm in [p.name for p in input_pokemons]
      node_sizes.append(MAIN_POKEMON_NODE_SIZE if is_main_pkm else AUX_POKEMON_NODE_SIZE)
      node_colors.append(MAIN_POKEMON_NODE_COLOR if is_main_pkm else AUX_POKEMON_NODE_COLOR)

    # Creates a list of edges labels and colors
    connection_colors = []
    connection_labels = {}
    for name_a, name_b in pokemon_connections:
      pkm_a = self.all_pokemon_data[name_a]
      pkm_b = self.all_pokemon_data[name_b]
      egg_type_intersect = list_intersec(pkm_a["egg_groups"], pkm_b["egg_groups"])[0]
      type_intersect = list_intersec(pkm_a["types"], pkm_b["types"])[0]
      connection_colors.append(TYPE_COLORS[type_intersect])
      connection_labels[(name_a, name_b)] = egg_type_intersect

    # Creates the output directed graph
    drawing_G = nx.DiGraph()
    drawing_G.add_nodes_from(all_included_pokemons)
    drawing_G.add_edges_from(pokemon_connections)

    # Drawing
    pos = nx.spring_layout(drawing_G, k=2/math.sqrt(drawing_G.order()))
    nx.draw_networkx_nodes(drawing_G, pos, nodelist=all_included_pokemons, node_size=node_sizes, node_color=node_colors, ax=ax)
    nx.draw_networkx_labels(drawing_G, pos, font_size=NODE_LABEL_FONT_SIZE, ax=ax)
    nx.draw_networkx_edges(drawing_G, pos, edgelist=pokemon_connections, edge_color=connection_colors, width=EDGE_WIDTH, arrowsize=EDGE_ARROW_SIZE, ax=ax)
    nx.draw_networkx_edge_labels(drawing_G, pos, edge_labels=connection_labels, font_color="black", font_size=EDGE_LABEL_FONT_SIZE, ax=ax)