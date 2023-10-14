import numpy as np
import pandas as pd
import cvxpy as cp

x = 224  # Number of players to select

def simulate_player_selection(parameters, x):
    """
    @param {list} parameters - list of player parameters
    @returns the list of selections given the set of parameters
    """
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
    """
    @param {list} players_ids_removed - the list of players that have been taken
    @returns the probability of each player being selected next
    """
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

def get_pick_probability_by_pick(players_ids_removed, num_simulations):
    """
    @param {list} players_ids_removed - the list of players that have been taken
    @param {int} int - number of draft simulations to complete
    @returns the probability of the player being selected at each future pick number
    """
    player_ability_parameters_df=pd.read_csv('/Users/hinayatali/Desktop/EMSF_CAPSTONE/draft_pick_prob/player_ability_params/player_parameters.csv')
    player_ability_parameters_df=player_ability_parameters_df.loc[~player_ability_parameters_df['PLAYER_ID'].isin(players_ids_removed)]
    params=player_ability_parameters_df['ABILITY_PARAMS']
    simulation_results = []
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
    column_vals=['PICK_'+ str(i+len(players_ids_removed)+1) for i in range(x-len(players_ids_removed)+1)]
    heatmap_array=pd.DataFrame(heatmap_array, columns=column_vals)
    player_ability_parameters_df.reset_index(drop=True, inplace=True)
    heatmap_array.reset_index(drop=True, inplace=True)
    heatmap_array=pd.concat([player_ability_parameters_df[['PLAYER_NAME', 'PLAYER_ID']], heatmap_array], axis=1)
    return heatmap_array

def probability_available_pick_x(players_ids_removed, num_simulations):
    """
    @param {list} players_ids_removed - list of player ids that have been selected
    @param {int} num_simulations - number of simulations that have to take place
    @returns the probability a player will be available by any given pick
    """
    df_players=get_pick_probability_by_pick(players_ids_removed, num_simulations)
    probability_available_pick_x=df_players.copy()
    column_numbers=probability_available_pick_x.columns[2:]
    accumulated_probability=0
    for i in range(len(column_numbers)):
        if i==0:
            probability_available_pick_x[column_numbers[i]]=1
            accumulated_probability=1-df_players[column_numbers[i]]
        else:
            probability_available_pick_x[column_numbers[i]]=accumulated_probability
            accumulated_probability-=df_players[column_numbers[i]]
    return probability_available_pick_x

def get_pick_values(df, pick_numbers_left, picks_taken):
    """
    @param {dataframe} df - the dataframe of every player's pick probability, value given ranking, position, and team need
    @param {list} pick_numbers_left - the remaining picks the team has
    @param {list} picks_taken - the player ids that have already been taken
    @returns a dataframe with each player's player id, position, team need at that position, and the total expected pick value of selecting this player
    """
    player_dict={}
    df=df.sort_values('PICK_VALUE', ascending=False)
    player_id_values=df[['PLAYER_ID', 'PICK_VALUE']]
    list_of_remaining_picks=pick_numbers_left[1:]
    list_of_cols=[]
    list_of_new_cols=[]
    for i in list_of_remaining_picks:
        list_of_cols.append("PICK_" + str(i))
        list_of_new_cols.append("SUM_PROB_" + str(i))
    df_subset = df.groupby('POS').head(4)
    for i, row in df_subset.iterrows():
        id=(row['PLAYER_ID'],row['POS'], row['TEAM_NEED'])
        player_dict[id]=row['PICK_VALUE']
        new_df=probability_available_pick_x(picks_taken+[int(row['PLAYER_ID'])], 100)
        df_values=pd.merge(new_df, player_id_values, how='left', on=['PLAYER_ID'])
        df_values=df_values.sort_values('PICK_VALUE', ascending=False)
        df_values[list_of_new_cols]=df_values[list_of_cols].cumsum()
        for j in range(len(list_of_new_cols)):
            calculating_pick_value=df_values.loc[df_values[list_of_new_cols[j]]<1]
            pick_value=(calculating_pick_value['PICK_VALUE']*calculating_pick_value[list_of_cols[j]]).sum()
            player_dict[id]+=pick_value
    data_list = [{'PLAYER_ID': key[0], 'GROUPED_POS': key[1], 'TEAM_NEED': key[2], 'VALUE': value} for key, value in player_dict.items()]
    df_new = pd.DataFrame(data_list, index=None)
    return df_new

def objective(df, pos_const, user_weight):
    """
    @param {dataframe} df - the dataframe of values output from get_pick_values
    @param {dict} pos_const - dictionary of positional constraints
    @param {int} user_weight - the emphasis the user wants to place on team need versus pick value
    @returns the player ID of the optimal selection
    """

    # Define variables
    x = cp.Variable(len(df.index), boolean=True)

    # Define objective
    obj_lp = cp.Maximize(x@df['VALUE']*user_weight+x@df['TEAM_NEED']*(1-user_weight))

    # Define constraints
    cons_lp = []  # Initialize constraint list

    for position, max_players in pos_const.items():
        cons_lp.append(cp.sum(x[df['GROUPED_POS'] == position]) <= max_players)
    cons_lp.append(sum(x)==1)

    prob_lp = cp.Problem(obj_lp,cons_lp)
    sol = prob_lp.solve()

    x_np_array_lp = x.value.astype(float)  # extract the x values as a np array
    x_values_lp = pd.Series(x_np_array_lp, index = df.index)  # convert the np array to a Datafram
    selected = np.where(x_values_lp == 1)[0]  # get assignments

    # Print selected player
    return int(df.iloc[selected]['PLAYER_ID'])
#   return sol, df.iloc[selected]['PLAYER_ID']

def get_value(row, team, external_df):
    """
    @param {row} row - the row of player information
    @param {str} team - the team abbreviation
    @param {dataframe} external_df - the dataframe of team needs to use to return values
    @returns the team need for a given player
    """
    if row['POS'] in ['LW', 'RW', 'C']:
        return external_df.loc[team, 'df_F']
    elif row['POS'] == 'LD':
        return external_df.loc[team, 'df_LD']
    elif row['POS'] == 'RD':
        return external_df.loc[team, 'df_RD']
    else:
        return external_df.loc[team, 'df_G']
    
def name_player(player_id, player_names):
    """
    @param {int} player_id - the player id in question
    @param {dataframe} player_names - mapping of player id to player name in a dataframe
    @returns the player's name given the player id
    """
    return str(player_names.loc[player_names["PLAYER_ID"]==player_id]['PLAYER_NAME'].reset_index(drop=True)[0])

def determine_optimal_pick(player_rankings, player_position, team_needs, team, pick_numbers_left, picks_taken, pos_const, user_weight):
    """
    @param {dataframe} player_rankings - the rankings of the player input by the user in a pandas dataframe
    @param {dataframe} player_position - dataframe of each player's position
    @param {dataframe} team_needs - dataframe of each team's needs at each position
    @param {str} team - player's team abbreviation
    @param {list} pick_numbers_left - the team's picks remaining
    @param {list} picks_taken - the list of player ids that have already been taken
    @param {dict} pos_const - a dictionary containing the positional constraints input by the user
    @param {float} user_weight - the emphasis a team wants to place on position versus player value
    @returns the player id of the optimal selection
    """
    # player_rankings=player_rankings.drop(['PLAYER_NAME'], axis=1)
    pick_probs=probability_available_pick_x(picks_taken, 100)
    new_tab=pd.merge(pick_probs, player_rankings, how='left', on=['PLAYER_ID'])
    new_tab=pd.merge(new_tab, player_position[['PLAYER_ID','POS']], how='left', on=['PLAYER_ID'])
    new_tab['TEAM_NEED']=new_tab.apply(get_value, axis=1, team=team, external_df=team_needs)
    pick_values=get_pick_values(new_tab, pick_numbers_left, picks_taken)
    return objective(pick_values, pos_const, user_weight)

def simulate_draft(player_rankings, player_position, team_needs, player_names, team,  pick_numbers_left, picks_taken, pos_const, user_weight):
    """
    @param {dataframe} player_rankings - the rankings of the player input by the user in a pandas dataframe
    @param {dataframe} player_position - dataframe of each player's position
    @param {dataframe} team_needs - dataframe of each team's needs at each position
    @param {dataframe} player_names - mapped dataframe of player id to player name
    @param {str} team - player's team abbreviation
    @param {list} pick_numbers_left - the team's picks remaining
    @param {list} picks_taken - the list of player ids that have already been taken
    @param {dict} pos_const - a dictionary containing the positional constraints input by the user
    @param {float} user_weight - the emphasis a team wants to place on position versus player value
    @will simulate the entire draft through print statements
    """
    l_player_val=[]
    players_drafted=[]
    for i in range(len(player_rankings)):
        l_player_val.append(np.exp(-0.420*(i**0.391)))
    player_rankings['PICK_VALUE']=l_player_val
    player_rankings=player_rankings.drop(['PLAYER_NAME'], axis=1)
    picks_taken=[]
    for i in range(1, x+1):
        if i in pick_numbers_left:
            returned=determine_optimal_pick(player_rankings, player_position, team_needs, player_names, team, pick_numbers_left, picks_taken, pos_const, user_weight)
            print(returned)
            print(print(f"You selected {name_player(returned[1], player_names)}"))
            picks_taken.append(returned[1])
            players_drafted.append(returned[1])
            pick_numbers_left.pop(0)
        else:
            print(f"The probability the top three players on your list are available at pick {pick_numbers_left[0]} are as follows: ")
            players=probability_available_pick_x(picks_taken, 300)
            sorted_players=pd.merge(players, player_rankings, how='left', on=['PLAYER_ID']).sort_values(by='PICK_VALUE', ascending=False)
            print(sorted_players[["PLAYER_NAME", "PICK_"+str(pick_numbers_left[0])]].head(3).to_string(index=False))
            player_taken=simulate_one_player_taken(picks_taken)
            picks_taken.append(player_taken)
            print(f"{name_player(player_taken, player_names)} was selected")
            
def simulate_one_player_taken(picks_taken):
    """
    @param {list} picks_taken - the player ids of the players already taken
    @returns a randomly selected player based on the probabilities calculated
    """
    player_ability_parameters_df=pd.read_csv('/Users/hinayatali/Desktop/EMSF_CAPSTONE/draft_pick_prob/player_ability_params/player_parameters.csv')
    player_ability_parameters_df=player_ability_parameters_df.loc[~player_ability_parameters_df['PLAYER_ID'].isin(picks_taken)]
    params=player_ability_parameters_df['ABILITY_PARAMS']
    choice_probabilities = [np.exp(param) for param in params]
    total_probability = sum(choice_probabilities)
    normalized_probabilities = [prob / total_probability for prob in choice_probabilities]
    selected_player = np.random.choice(range(len(params)), p=normalized_probabilities)
    return player_ability_parameters_df.iloc[selected_player]['PLAYER_ID']

    
def probability_available_pick_specified(players_ids_removed, num_simulations, pick_number):
    """
    @param {list} player_ids_removed - list of player ids that have been taken
    @param {int} num_simulations - number of simulations to run
    @param {int} pick_number - the pick number that will be checked for pick probability
    @returns the probability each player is available by the pick specified
    """
    df_players=get_pick_probability_by_pick(players_ids_removed, num_simulations)
    probability_available_pick_x=df_players.copy()
    column_numbers=probability_available_pick_x.columns[2:]
    accumulated_probability=0
    for i in range(len(column_numbers)):
        if i==0:
            probability_available_pick_x[column_numbers[i]]=1
            accumulated_probability=1-df_players[column_numbers[i]]
        else:
            probability_available_pick_x[column_numbers[i]]=accumulated_probability
            accumulated_probability-=df_players[column_numbers[i]]
    return probability_available_pick_x[['PLAYER_ID', 'PICK_'+str(pick_number)]]   
