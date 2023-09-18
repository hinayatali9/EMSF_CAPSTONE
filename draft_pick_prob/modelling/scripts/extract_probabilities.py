import numpy as np
import pandas as pd

x = 224  # Number of players to select
num_simulations = 1000  # Number of simulations

def simulate_player_selection(parameters, x):
    selected_players = []
    remaining_parameters = parameters.copy()
    indices=[i for i in range(len(parameters))]
    for _ in range(x):
        # Calculate choice probabilities based on the exponents of parameters
        choice_probabilities = [np.exp(param) for param in remaining_parameters]
        # Normalize choice probabilities
        total_probability = sum(choice_probabilities)
        normalized_probabilities = [prob / total_probability for prob in choice_probabilities]
        # Select a player based on the probabilities
        selected_player = np.random.choice(range(len(remaining_parameters)), p=normalized_probabilities)
        # Add the selected player to the list and remove the corresponding parameter
        selected_players.append(indices[selected_player]+1)
        indices.pop(selected_player)
        remaining_parameters = np.delete(remaining_parameters, selected_player)
        # print(len(remaining_parameters))

    return selected_players


def get_next_pick_probability(players_ids_removed):
    player_ability_parameters_df=pd.read_csv('/Users/hinayatali/Desktop/EMSF_CAPSTONE/draft_pick_prob/player_ability_params/player_parameters.csv')
    player_ability_parameters_df=player_ability_parameters_df.loc[~player_ability_parameters_df['PLAYER_ID'].isin(players_ids_removed)]
    params=player_ability_parameters_df['ABILITY_PARAMS']
    choice_probabilities = [np.exp(param) for param in params]
    total_probability = sum(choice_probabilities)
    normalized_probabilities = [prob / total_probability for prob in choice_probabilities]
    player_ability_parameters_df['NEXT_PICK_PROB']=normalized_probabilities
    return player_ability_parameters_df
    # num_players_left=224-len(players_ids_removed)
    # for _ in range(num_simulations):
    #     selected_players = simulate_player_selection(player_ability_parameters_df['ABILITY_PARAMS'], num_players_left)
    #     simulation_results.append(selected_players)

def get_pick_probability_by_pick(players_ids_removed):
    player_ability_parameters_df=pd.read_csv('/Users/hinayatali/Desktop/EMSF_CAPSTONE/draft_pick_prob/player_ability_params/player_parameters.csv')
    player_ability_parameters_df=player_ability_parameters_df.loc[~player_ability_parameters_df['PLAYER_ID'].isin(players_ids_removed)]
    params=player_ability_parameters_df['ABILITY_PARAMS']
    simulation_results = []
    num_simulations=1000
    for _ in range(num_simulations):
        selected_players = simulate_player_selection(params, x-len(players_ids_removed))
        simulation_results.append(selected_players)
    lists_of_numbers=[]
    for j in range(len(params)):
        first_player=[]
        for i in simulation_results:
            test_array = np.array(i)
            if (j+1) in i:
                res_array = np.where(test_array == j+1)[0][0]+1
                first_player.append(float(res_array))
            else:
                first_player.append(x-len(players_ids_removed)+1)
        lists_of_numbers.append(first_player)
    unique_numbers_per_list = [np.unique(sublist, return_counts=True) for sublist in lists_of_numbers]
    percentage_occurrences_per_list = []
    for _, counts in unique_numbers_per_list:
        total_count = sum(counts)
        percentages = [count / total_count for count in counts]
        percentage_occurrences_per_list.append(percentages)
    heatmap_array=[]
    heatmap_array=np.zeros((len(params),x-len(players_ids_removed)+1))
    for i in range(len(unique_numbers_per_list)):
        for j in range(len(unique_numbers_per_list[i][0])):
            heatmap_array[i][int(unique_numbers_per_list[i][0][j])-1]=percentage_occurrences_per_list[i][int(j)]
    return heatmap_array