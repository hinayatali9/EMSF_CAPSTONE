import numpy as np
import pandas as pd
import cvxpy as cp
import os
from collections import Counter

x = 224  # Number of players to select

personal_path = os.getcwd()
personal_path = personal_path[
    : (personal_path.find("EMSF_CAPSTONE") + len("EMSF_CAPSTONE/"))
].replace("\\", "/")
if personal_path[-1] != "/":
    personal_path += "/"

UNIVERSAL_DF = pd.read_csv(
    str(personal_path) + "draft_pick_prob/player_ability_params/player_parameters.csv"
)


def simulate_player_selection(parameters: list, x: int):
    """
    @param {list} parameters - list of player parameters
    @returns the list of selections given the set of parameters
    """
    selected_players = []
    remaining_parameters = parameters.copy()
    indices = [i for i in range(len(parameters))]
    for _ in range(x):
        # Calculate choice probabilities based on the exponents of parameters
        choice_probabilities = [np.exp(param) for param in remaining_parameters]
        # Normalize choice probabilities
        total_probability = sum(choice_probabilities)
        normalized_probabilities = [
            prob / total_probability for prob in choice_probabilities
        ]
        # Select a player based on the probabilities
        selected_player = np.random.choice(
            range(len(remaining_parameters)), p=normalized_probabilities
        )
        # Add the selected player to the list and remove the corresponding parameter
        selected_players.append(indices[selected_player] + 1)
        indices.pop(selected_player)
        remaining_parameters = np.delete(remaining_parameters, selected_player)

    return selected_players


def get_next_pick_probability(players_ids_removed: list):
    """
    @param {list} players_ids_removed - the list of players that have been taken
    @returns the probability of each player being selected next
    """
    player_ability_parameters_df = pd.read_csv(
        str(personal_path)
        + "draft_pick_prob/player_ability_params/player_parameters.csv"
    )
    player_ability_parameters_df = player_ability_parameters_df.loc[
        ~player_ability_parameters_df["PLAYER_ID"].isin(players_ids_removed)
    ]
    params = player_ability_parameters_df["ABILITY_PARAMS"]
    choice_probabilities = [np.exp(param) for param in params]
    total_probability = sum(choice_probabilities)
    normalized_probabilities = [
        prob / total_probability for prob in choice_probabilities
    ]
    player_ability_parameters_df["NEXT_PICK_PROB"] = normalized_probabilities
    return player_ability_parameters_df


def get_pick_probability_by_pick(players_ids_removed: list, num_simulations: int):
    """
    @param {list} players_ids_removed - the list of players that have been taken
    @param {int} int - number of draft simulations to complete
    @returns the probability of the player being selected at each future pick number
    """
    player_ability_parameters_df = pd.read_csv(
        str(personal_path)
        + "draft_pick_prob/player_ability_params/player_parameters.csv"
    )
    player_ability_parameters_df = player_ability_parameters_df.loc[
        ~player_ability_parameters_df["PLAYER_ID"].isin(players_ids_removed)
    ]
    params = player_ability_parameters_df["ABILITY_PARAMS"]
    simulation_results = []
    for _ in range(num_simulations):
        selected_players = simulate_player_selection(
            params, x - len(players_ids_removed)
        )
        simulation_results.append(selected_players)
    lists_of_numbers = []
    for j in range(len(params)):
        first_player = []
        for i in simulation_results:
            test_array = np.array(i)
            if (j + 1) in i:
                res_array = np.where(test_array == j + 1)[0][0] + 1
                first_player.append(float(res_array))
            else:
                first_player.append(x - len(players_ids_removed) + 1)
        lists_of_numbers.append(first_player)
    unique_numbers_per_list = [
        np.unique(sublist, return_counts=True) for sublist in lists_of_numbers
    ]
    percentage_occurrences_per_list = []
    for _, counts in unique_numbers_per_list:
        total_count = sum(counts)
        percentages = [count / total_count for count in counts]
        percentage_occurrences_per_list.append(percentages)
    heatmap_array = []
    heatmap_array = np.zeros((len(params), x - len(players_ids_removed) + 1))
    for i in range(len(unique_numbers_per_list)):
        for j in range(len(unique_numbers_per_list[i][0])):
            heatmap_array[i][
                int(unique_numbers_per_list[i][0][j]) - 1
            ] = percentage_occurrences_per_list[i][int(j)]
    column_vals = [
        "PICK_" + str(i + len(players_ids_removed) + 1)
        for i in range(x - len(players_ids_removed) + 1)
    ]
    heatmap_array = pd.DataFrame(heatmap_array, columns=column_vals)
    player_ability_parameters_df.reset_index(drop=True, inplace=True)
    heatmap_array.reset_index(drop=True, inplace=True)
    heatmap_array = pd.concat(
        [player_ability_parameters_df[["PLAYER_NAME", "PLAYER_ID"]], heatmap_array],
        axis=1,
    )
    return heatmap_array


def probability_available_pick_x(players_ids_removed: list, num_simulations: int):
    """
    @param {list} players_ids_removed - list of player ids that have been selected
    @param {int} num_simulations - number of simulations that have to take place
    @returns the probability a player will be available by any given pick
    """
    df_players = get_pick_probability_by_pick(players_ids_removed, num_simulations)
    probability_available_pick_x = df_players.copy()
    column_numbers = probability_available_pick_x.columns[2:]
    accumulated_probability = 0
    for i in range(len(column_numbers)):
        if i == 0:
            probability_available_pick_x[column_numbers[i]] = 1
            accumulated_probability = 1 - df_players[column_numbers[i]]
        else:
            probability_available_pick_x[column_numbers[i]] = accumulated_probability
            accumulated_probability -= df_players[column_numbers[i]]
    return probability_available_pick_x


def get_pick_values(df: pd.DataFrame, pick_numbers_left: list, picks_taken: list):
    """
    @param {dataframe} df - the dataframe of every player's pick probability, value given ranking,
    position, and team need
    @param {list} pick_numbers_left - the remaining picks the team has
    @param {list} picks_taken - the player ids that have already been taken
    @returns a dataframe with each player's player id, position, team need at that position,
    and the total expected pick value of selecting this player
    """
    players = list(df["PLAYER_ID"])
    positions = list(df["POS"])
    team_needs = list(df["TEAM_NEED"])
    dict_player_value = {}
    list_of_cols = []
    list_of_remaining_picks = pick_numbers_left[1:]
    number_differences = []
    for i in list_of_remaining_picks:
        list_of_cols.append("PICK_" + str(i))
        number_differences.append(i - pick_numbers_left[0])
    for i in range(len(players)):
        dict_player_value[(players[i], positions[i], team_needs[i])] = float(
            df.loc[df["PLAYER_ID"] == players[i]]["PICK_VALUE"].iloc[0]
        )
        test_df = df.loc[df["PLAYER_ID"] != players[i]]
        additional_player_value = 0
        for j in range(len(number_differences)):
            smaller_df = test_df.head(number_differences[j])
            storing_value = 1
            for _, row in smaller_df.iterrows():
                additional_player_value += (
                    storing_value * row["PICK_VALUE"] * row[list_of_cols[j]]
                )
                storing_value = storing_value * (1 - row[list_of_cols[j]])
        dict_player_value[
            (players[i], positions[i], team_needs[i])
        ] += additional_player_value
    data_list = [
        {
            "PLAYER_ID": key[0],
            "GROUPED_POS": key[1],
            "TEAM_NEED": key[2],
            "VALUE": value,
        }
        for key, value in dict_player_value.items()
    ]
    df_new = pd.DataFrame(data_list, index=None)
    return df_new


def rank_pre_processing(df):
    """
    Creates a dictionary with a dataframe filled with players in the league prospect pool for each position
    and age group.
    Players under the age of 19 are grouped with the 19 year old datafarames.

    @param {dataframe} df - Prospect pool dataframe
    @returns a dictionary with multiple prospect pool dataframes for each age and position
    """
    df.loc[(df["Specific POS"] == "LW"), "Specific POS"] = "F"
    df.loc[(df["Specific POS"] == "C"), "Specific POS"] = "F"
    df.loc[(df["Specific POS"] == "RW"), "Specific POS"] = "F"

    ages = [19, 20, 21, 22, 23]
    positions = ["F", "LD", "RD", "G"]
    players = {}

    for position in positions:
        for age in ages:
            if age == 19:
                players["df_" + str(position) + "-" + str(age)] = df[
                    (df["Specific POS"] == position) & (df["AGE"] <= age)
                ]
            else:
                players["df_" + str(position) + "-" + str(age)] = df[
                    (df["Specific POS"] == position) & (df["AGE"] == age)
                ]

    return players


def fill_missing_teams(df_dict, key, col):
    """
    This function finds the minimum Z-score across each dataframe and applies a lower Z-score value to teams
    without any players in it. This data gets stored in the dataframes such that every team gets a percentile
    ranking later in the code. And these ranking must be lower than the teams with actual prospects for each
    age group and position.

    @param {dictionary} df_dict - a dictionary that contains all position-age dataframes of the seperated prospect pool
    @param {str} key - the name of each dataframe which outlines the position and age. Used as the keys to df_dict
    @param {str} col - the name of the column that needs to be filled in (Z-score in this case)
    @returns the updated df_dict dictionary 
    """
    Teams = [
        "COL",
        "CHI",
        "CBJ",
        "STL",
        "BOS",
        "MTL",
        "VAN",
        "WSH",
        "ARI",
        "NJD",
        "ANA",
        "CGY",
        "PHI",
        "CAR",
        "NYI",
        "WPG",
        "LAK",
        "VGK",
        "SEA",
        "TOR",
        "TBL",
        "EDM",
        "FLA",
        "PIT",
        "NSH",
        "NYR",
        "DET",
        "BUF",
        "OTT",
        "SJS",
        "DAL",
        "MIN",
    ]

    index_set = set(df_dict[key]["Team"])
    min_value = df_dict[key][col].min()

    # Find elements in lst that are not in the index
    missing_elements = [x for x in Teams if x not in index_set]

    # If there are missing elements, add them to the DataFrame with value 0 in column 'A'
    if missing_elements:
        missing_df = pd.DataFrame(
            {col: [(min_value - 1)] * len(missing_elements), "Team": missing_elements}
        )
        df_dict[key] = pd.concat([df_dict[key], missing_df])

    return df_dict


def score_and_rank(df_dict):
    """
    This function first scores the prospects in the entire pool, keeping seperate dataframes and scoring
    systems for different
    age groups and positions. After Z-scores are calculated, the missing teams are filled in and exponentials
    of these scores
    are taken to ensure that every prospect contributes positively to the strength of the team.

    After the scoring is done, the exponential Z-scores are summed over for every team in the respective
    dataframes and the teams
    are ranked. Unncessary columns are removed and what remains is the team name and rank in each
    age/position dataframe.

    @param {dictionary} df_dict - a dictionary that contains all position-age dataframes of the seperated prospect pool
    @returns a dictionary of dataframes with team names and prospect pool rankings for each group
    """
    df_dict_out = {}

    for i in df_dict:
        # Calculate Z-scores
        df = df_dict[i].copy()
        if len(df) == 1:
            df.loc[:, "zscore"] = 0
        else:
            if "G" in i:
                df.loc[:, "zscore"] = (
                    df["Goalie Equivalency"] - df["Goalie Equivalency"].mean()
                ) / df["Goalie Equivalency"].std()
            else:
                df.loc[:, "zscore"] = (df["NHL eP"] - df["NHL eP"].mean()) / df[
                    "NHL eP"
                ].std()
        df_dict[i] = df

        # Provide missing teams with some lower Z-score value to be ranked at the bottom
        df_dict = fill_missing_teams(df_dict, i, "zscore")

        # Transform Z-scores to ensure positive prospect pool contribution for all players
        df_dict[i]["exp_zscore"] = np.exp(df_dict[i]["zscore"])

        df_dict_out[i] = df_dict[i].groupby("Team").sum("exp_zscore")
        df_dict_out[i]["rank"] = df_dict_out[i]["exp_zscore"].rank(
            pct=True
        ) 
        df_dict_out[i].drop(
            columns=[
                "AGE",
                "GP",
                "G",
                "A",
                "P",
                "GAA",
                "SV%",
                "Goalie Equivalency",
                "NHL eP",
                "exp_zscore",
                "zscore",
            ],
            inplace=True,
        )

    return df_dict_out


def group_ranker(rank_dfs, weights):
    """
    This function creates final prospect pool rankings for every position by amalgamating the individual
    prospect rankings
    for every age group. A set of weights for every age group is used to determin the weighted sum. All
    newly drafted players
    get combined with the 19 year old dataframe, such that they don't have an overly drastic effect on the rankings.

    @param {dictionary} rank_dfs - Dictionary of dataframes with team names and prospect pool rankings for each age/position group
    @param {float} weights - Weights for each individual ranking, used in weighted sum
    @returns a dataframe of team names and prospect pool rankings for each position
    """
    result = pd.DataFrame()

    for key in rank_dfs:
        position, age = key.split("-")  # split the key into position and age
        weight = weights[int(age)]  

        df = rank_dfs[key].copy()  
        df["rank"] *= weight  # multiply the percentile rankings by the weight

        # add to the existing DataFrame for this position
        if position in result:
            result[position] += df[
                "rank"
            ]  
        else:
            result[position] = df["rank"]

    for key in result:
        result[key] = result[key].rank(pct=True)
        result[key] = 1 - result[key]  # flips percentiles around for optimization model

    return result


def update_prospect_ranker(player_IDs):
    """
    This function updates the prospect pool rankings of the league by taking into account the players who have been drafted thus far.

    @param {list} player_IDs - List of player IDs for players who have been drafted so far
    @returns the dataframe from the group_ranker function
    """

    df_weight = {19: 0.85, 20: 0.7, 21: 0.55, 22: 0.4, 23: 0.25}
    draft_order = []

    df_draft = pd.read_csv(str(personal_path) + "draft_info/draft_pick_numbers.csv")
    df_2023 = pd.read_csv(
        str(personal_path) + "Prospect Pool/MIE479 2023 Player Pool Cleaned.csv"
    )
    df1 = pd.read_csv(str(personal_path) + "Prospect Pool/Initial Prospect Pool.csv")

    # Define the replacement mapping
    replacement_mapping = {
        "Colorado Avalanche": "COL",
        "Chicago Blackhawks": "CHI",
        "St. Louis Blues": "STL",
        "Columbus Blue Jackets": "CBJ",
        "Boston Bruins": "BOS",
        "Montreal Canadiens": "MTL",
        "Vancouver Canucks": "VAN",
        "Washington Capitals": "WSH",
        "Arizona Coyotes": "ARI",
        "New Jersey Devils": "NJD",
        "Anaheim Ducks": "ANA",
        "Calgary Flames": "CGY",
        "Philadelphia Flyers": "PHI",
        "Carolina Hurricanes": "CAR",
        "New York Islanders": "NYI",
        "Winnipeg Jets": "WPG",
        "Los Angeles Kings": "LAK",
        "Vegas Golden Knights": "VGK",
        "Seattle Kraken": "SEA",
        "Toronto Maple Leafs": "TOR",
        "Tampa Bay Lightning": "TBL",
        "Edmonton Oilers": "EDM",
        "Florida Panthers": "FLA",
        "Pittsburgh Penguins": "PIT",
        "Nashville Predators": "NSH",
        "New York Rangers": "NYR",
        "Detroit Red Wings": "DET",
        "Buffalo Sabres": "BUF",
        "Ottawa Senators": "OTT",
        "San Jose Sharks": "SJS",
        "Dallas Stars": "DAL",
        "Minnesota Wild": "MIN",
    }

    # Use the .loc function to replace values
    df_draft.loc[
        df_draft["TEAM_NAME"].isin(replacement_mapping.keys()), "TEAM_NAME"
    ] = df_draft["TEAM_NAME"].map(replacement_mapping)
    df_draft = df_draft["TEAM_NAME"]

    # Organize draft order and place players taken with their respective team's prospect pools
    for i in df_draft[0 : len(player_IDs)]:
        draft_order.append(i)

    for ID in range(len(player_IDs)):
        filtered_row = df_2023[df_2023["PLAYER_ID"] == player_IDs[ID]].copy()
        filtered_row["Team"] = draft_order[ID]
        filtered_row.drop(columns="PLAYER_ID", inplace=True)
        df1 = pd.concat([df1, filtered_row], ignore_index=True)

    # Rank the dataframes and group them
    rank_pre_proc = rank_pre_processing(df1)
    indiv_ranks = score_and_rank(rank_pre_proc)
    ranks_new = group_ranker(indiv_ranks, df_weight)

    return ranks_new


def pos_constraints(
    max_pos_const: dict,
    min_pos_const: dict,
    picks_taken: list,
    pick_numbers_left: list,
    team: str,
):
    """
    This function implements the user's positional constraints by updating the maximum and minimum 
    values of each position, based on who has been drafed thus far.
    
    @param {dictionary} max_pos_const - A dictionary of the maximum positional constraints, where the key is a str type 
                                        of the position abbreviation and the item is an integer for the user inputted value
    @param {dictionary} min_pos_const - A dictionary of the minimum positional constraints, where the key is a str type 
                                        of the position abbreviation and the item is an integer for the user inputted value
    @param {list} picks_taken - List of player IDs for players who have been drafted so far
    @param {list} pick_numbers_left - List of pick numbers that the selected team has left to draft
    @param {str} team - Team name
    @returns the updated max_pos_const dictionary for players who have been selected
    @returns a list of positional abbreviations that are not needed, in order to satisfy the minimum positional constraints
    """
    draft_order = []
    needs = []

    df_draft = pd.read_csv(str(personal_path) + "draft_info/draft_pick_numbers.csv")
    df_2023 = pd.read_csv(
        str(personal_path) + "Prospect Pool/MIE479 2023 Player Pool Cleaned.csv"
    )

    # Define the replacement mapping
    replacement_mapping = {
        "Colorado Avalanche": "COL",
        "Chicago Blackhawks": "CHI",
        "St. Louis Blues": "STL",
        "Columbus Blue Jackets": "CBJ",
        "Boston Bruins": "BOS",
        "Montreal Canadiens": "MTL",
        "Vancouver Canucks": "VAN",
        "Washington Capitals": "WSH",
        "Arizona Coyotes": "ARI",
        "New Jersey Devils": "NJD",
        "Anaheim Ducks": "ANA",
        "Calgary Flames": "CGY",
        "Philadelphia Flyers": "PHI",
        "Carolina Hurricanes": "CAR",
        "New York Islanders": "NYI",
        "Winnipeg Jets": "WPG",
        "Los Angeles Kings": "LAK",
        "Vegas Golden Knights": "VGK",
        "Seattle Kraken": "SEA",
        "Toronto Maple Leafs": "TOR",
        "Tampa Bay Lightning": "TBL",
        "Edmonton Oilers": "EDM",
        "Florida Panthers": "FLA",
        "Pittsburgh Penguins": "PIT",
        "Nashville Predators": "NSH",
        "New York Rangers": "NYR",
        "Detroit Red Wings": "DET",
        "Buffalo Sabres": "BUF",
        "Ottawa Senators": "OTT",
        "San Jose Sharks": "SJS",
        "Dallas Stars": "DAL",
        "Minnesota Wild": "MIN",
    }

    # Use the .loc function to replace values
    df_draft.loc[
        df_draft["TEAM_NAME"].isin(replacement_mapping.keys()), "TEAM_NAME"
    ] = df_draft["TEAM_NAME"].map(replacement_mapping)
    df_draft = df_draft["TEAM_NAME"]

    # Organize draft order and track player position for those selecetd thus far
    for i in df_draft[0 : len(picks_taken)]:
        draft_order.append(i)

    for pick in range(len(picks_taken)):
        if draft_order[pick] == team:
            specific_pos = df_2023[df_2023["PLAYER_ID"] == picks_taken[pick]][
                "Specific POS"
            ].values[0]

            # Decrease the maximum and minimum position constraint for who has been selected
            if max_pos_const.get(specific_pos, 0) > 0:
                max_pos_const[specific_pos] -= 1

            if min_pos_const.get(specific_pos, 0) > 0:
                min_pos_const[specific_pos] -= 1
       
    #  If remaining picks = sum of minimum constraints, need to enforce other positions to not be selected
    if len(pick_numbers_left) == sum(min_pos_const.values()):
        for key, item in min_pos_const.items():
            if item == 0:
                needs.append(key) # updates list of non-needed positions

    return max_pos_const, needs


def objective(
    df: pd.DataFrame,
    max_pos_const: dict,
    min_pos_const: dict,
    picks_taken: list,
    pick_numbers_left: list,
    team: str,
    user_weight: float,
):
    """
    @param {dataframe} df - the dataframe of values output from get_pick_values
    @param {dict} pos_const - dictionary of positional constraints
    @param {int} user_weight - the emphasis the user wants to place on team need versus pick value
    @returns the player ID of the optimal selection
    """

    # Define variables
    x = cp.Variable(len(df.index), boolean=True)

    # Define objective
    obj_lp = cp.Maximize(
        x @ df["VALUE"] * user_weight + x @ df["TEAM_NEED"] * (1 - user_weight)
    )

    # Define constraints
    cons_lp = []  # Initialize constraint list

    max, need = pos_constraints(
        max_pos_const, min_pos_const, picks_taken, pick_numbers_left, team
    )

    for position, max_players in max.items():
        cons_lp.append(cp.sum(x[df["GROUPED_POS"] == position]) <= max_players)

    if len(need) > 0:
        for i in need:
            cons_lp.append(cp.sum(x[df["GROUPED_POS"] == i]) == 0)

    cons_lp.append(sum(x) == 1)

    prob_lp = cp.Problem(obj_lp, cons_lp)
    prob_lp.solve()

    x_np_array_lp = x.value.astype(float)  # extract the x values as a np array
    x_values_lp = pd.Series(
        x_np_array_lp, index=df.index
    )  # convert the np array to a Dataframe
    selected = np.where(x_values_lp == 1)[0]  # get assignments

    # Print selected player
    return int(df.iloc[selected]["PLAYER_ID"].iloc[0])


#   return sol, df.iloc[selected]['PLAYER_ID']


def get_value(row, team: str, external_df: pd.DataFrame):
    """
    @param {row} row - the row of player information
    @param {str} team - the team abbreviation
    @param {dataframe} external_df - the dataframe of team needs to use to return values
    @returns the team need for a given player
    """
    if row["POS"] in ["LW", "RW", "C"]:
        return external_df.loc[team, "df_F"]
    elif row["POS"] == "LD":
        return external_df.loc[team, "df_LD"]
    elif row["POS"] == "RD":
        return external_df.loc[team, "df_RD"]
    else:
        return external_df.loc[team, "df_G"]


def name_player(player_id: int, player_names: pd.DataFrame):
    """
    @param {int} player_id - the player id in question
    @param {dataframe} player_names - mapping of player id to player name in a dataframe
    @returns the player's name given the player id
    """
    return str(
        player_names.loc[player_names["PLAYER_ID"] == player_id][
            "PLAYER_NAME"
        ].reset_index(drop=True)[0]
    )


def determine_optimal_pick(
    player_rankings: pd.DataFrame,
    player_position: pd.DataFrame,
    team_needs: pd.DataFrame,
    team: str,
    pick_numbers_left: list,
    picks_taken: list,
    max_pos_const: dict,
    min_pos_const: dict,
    user_weight: float,
):
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
    l_player_val = []
    for i in range(len(player_rankings)):
        l_player_val.append(np.exp(-0.420 * (i**0.391)))
    player_rankings["PICK_VALUE"] = l_player_val
    pick_probs = checking_probability_picks(
        picks_taken, 1000, pick_numbers_left, player_rankings
    )
    new_tab = pd.merge(
        pick_probs, player_position[["PLAYER_ID", "POS"]], how="left", on=["PLAYER_ID"]
    )
    team_needs = update_prospect_ranker(picks_taken)
    new_tab["TEAM_NEED"] = new_tab.apply(
        get_value, axis=1, team=team, external_df=team_needs
    )
    pick_values = get_pick_values(new_tab, pick_numbers_left, picks_taken)
    return objective(
        pick_values,
        max_pos_const,
        min_pos_const,
        picks_taken,
        pick_numbers_left,
        team,
        user_weight,
    )


def simulate_draft(
    player_rankings: pd.DataFrame,
    player_position: pd.DataFrame,
    team_needs: pd.DataFrame,
    player_names: pd.DataFrame,
    team: str,
    pick_numbers_left: list,
    picks_taken: list,
    pos_const: dict,
    user_weight: float,
):
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
    l_player_val = []
    players_drafted = []
    for i in range(len(player_rankings)):
        l_player_val.append(np.exp(-0.420 * (i**0.391)))
    player_rankings["PICK_VALUE"] = l_player_val
    player_rankings = player_rankings.drop(["PLAYER_NAME"], axis=1)
    picks_taken = []
    for i in range(1, x + 1):
        if i in pick_numbers_left:
            returned = determine_optimal_pick(
                player_rankings,
                player_position,
                team_needs,
                player_names,
                team,
                pick_numbers_left,
                picks_taken,
                pos_const,
                user_weight,
            )
            picks_taken.append(returned[1])
            players_drafted.append(returned[1])
            pick_numbers_left.pop(0)
        else:
            print(
                f"The probability the top three players on your list are available at pick {pick_numbers_left[0]}"
                + " are as follows: "
            )
            players = probability_available_pick_x(picks_taken, 300)
            sorted_players = pd.merge(
                players, player_rankings, how="left", on=["PLAYER_ID"]
            ).sort_values(by="PICK_VALUE", ascending=False)
            print(
                sorted_players[["PLAYER_NAME", "PICK_" + str(pick_numbers_left[0])]]
                .head(3)
                .to_string(index=False)
            )
            player_taken = simulate_one_player_taken(picks_taken)
            picks_taken.append(player_taken)
            print(f"{name_player(player_taken, player_names)} was selected")


def simulate_one_player_taken(picks_taken: list):
    """
    @param {list} picks_taken - the player ids of the players already taken
    @returns a randomly selected player based on the probabilities calculated
    """
    player_ability_parameters_df = pd.read_csv(
        str(personal_path)
        + "draft_pick_prob/player_ability_params/player_parameters.csv"
    )
    player_ability_parameters_df = player_ability_parameters_df.loc[
        ~player_ability_parameters_df["PLAYER_ID"].isin(picks_taken)
    ]
    params = player_ability_parameters_df["ABILITY_PARAMS"]
    choice_probabilities = [np.exp(param) for param in params]
    total_probability = sum(choice_probabilities)
    normalized_probabilities = [
        prob / total_probability for prob in choice_probabilities
    ]
    selected_player = np.random.choice(range(len(params)), p=normalized_probabilities)
    return player_ability_parameters_df.iloc[selected_player]["PLAYER_ID"]


def probability_available_pick_specified(
    players_ids_removed: list, num_simulations: int, pick_number: int
):
    """
    @param {list} player_ids_removed - list of player ids that have been taken
    @param {int} num_simulations - number of simulations to run
    @param {int} pick_number - the pick number that will be checked for pick probability
    @returns the probability each player is available by the pick specified
    """
    return get_pick_probability_by_next_pick(
        players_ids_removed, num_simulations, pick_number
    )


def get_pick_probability_by_next_pick(
    players_ids_removed, num_simulations, pick_number
):
    """
    @param {list} players_ids_removed - the list of players that have been taken
    @param {int} int - number of draft simulations to complete
    @returns the probability of the player being selected at each future pick number
    """
    player_ability_parameters_df = UNIVERSAL_DF
    player_ability_parameters_df = player_ability_parameters_df.loc[
        ~player_ability_parameters_df["PLAYER_ID"].isin(players_ids_removed)
    ]
    params = player_ability_parameters_df["ABILITY_PARAMS"]
    player_ids = list(player_ability_parameters_df["PLAYER_ID"])
    df_new = player_ability_parameters_df[["PLAYER_ID", "ABILITY_PARAMS"]].copy()
    df_new["order"] = range(1, len(params) + 1)
    df_new["PICK_" + str(pick_number)] = 1
    simulation_results = []
    simulation_results = simulate_player_selection_vectorized(
        params, player_ids, pick_number - len(players_ids_removed) - 1, num_simulations
    )
    simulation_results = [item for sublist in simulation_results for item in sublist]
    counter = Counter(simulation_results)
    df_new["PICK_" + str(pick_number)] = df_new[
        "PICK_" + str(pick_number)
    ].astype(float)
    for element, count in counter.items():
        df_new.loc[df_new["PLAYER_ID"] == element, "PICK_" + str(pick_number)] -= (
            count / num_simulations
        )
    df_new.loc[df_new["PICK_" + str(pick_number)] < 0, "PICK_" + str(pick_number)] = 0
    return df_new[["PLAYER_ID", "PICK_" + str(pick_number)]]


def checking_probability_picks(
    players_ids_removed: list, num_simulations: int, picks: int, starting_df
):
    player_ability_parameters_df = UNIVERSAL_DF
    player_ability_parameters_df = player_ability_parameters_df.loc[
        ~player_ability_parameters_df["PLAYER_ID"].isin(players_ids_removed)
    ]
    params = player_ability_parameters_df["ABILITY_PARAMS"]
    player_ids = list(player_ability_parameters_df["PLAYER_ID"])
    pick_availability = simulate_player_selection_vectorized(
        params, player_ids, picks[-1] - (len(players_ids_removed) - 1), 1000
    )
    for i in picks:
        simulation_results = [
            item
            for sublist in pick_availability
            for item in sublist[0 : (i - len(players_ids_removed) - 1)]
        ]
        counter = Counter(simulation_results)
        df_new = player_ability_parameters_df[["PLAYER_ID"]].copy()
        df_new["PICK_" + str(i)] = 1
        df_new.loc["PICK_" + str(i)] = df_new["PICK_" + str(i)].astype(float)
        for element, count in counter.items():
            df_new.loc[df_new["PLAYER_ID"] == element, "PICK_" + str(i)] -= (
                count / num_simulations
            )
        df_new.loc[df_new["PICK_" + str(i)] < 0, "PICK_" + str(i)] = 0
        starting_df = pd.merge(starting_df, df_new, how="left", on=["PLAYER_ID"])
    starting_df = starting_df.dropna()
    return starting_df


def simulate_player_selection_vectorized(
    parameters: list, player_ids, x: int, num_simulations: int
):
    selected_players = []
    sims = []
    for _ in range(num_simulations):
        selected_players = []
        remaining_parameters = parameters.copy()
        indices = [i for i in range(len(parameters))]
        player_ids_remaining = player_ids
        for _ in range(x):
            # Calculate choice probabilities based on the exponents of parameters
            choice_probabilities = [np.exp(param) for param in remaining_parameters]
            # Normalize choice probabilities
            total_probability = sum(choice_probabilities)
            normalized_probabilities = [
                prob / total_probability for prob in choice_probabilities
            ]
            # Select a player based on the probabilities
            selected_player = np.random.choice(
                range(len(remaining_parameters)), p=normalized_probabilities
            )
            # Add the selected player to the list and remove the corresponding parameter
            selected_players.append(player_ids_remaining[selected_player])
            indices.pop(selected_player)
            player_ids_remaining = np.delete(player_ids_remaining, selected_player)
            remaining_parameters = np.delete(remaining_parameters, selected_player)
        sims.append(selected_players)
    return sims


def player_value(
    player_rankings: pd.DataFrame,
    player_position: pd.DataFrame,
    picks_taken: list,
    user_weight: float,
    team_name: str,
) -> pd.DataFrame:
    l_player_val = []
    for i in range(len(player_rankings)):
        l_player_val.append(np.exp(-0.420 * (i**0.391)))
    player_rankings["PICK_VALUE"] = l_player_val
    player_rankings = player_rankings.loc[
        ~player_rankings["PLAYER_ID"].isin(picks_taken)
    ]
    player_rankings = pd.merge(
        player_rankings,
        player_position[["PLAYER_ID", "POS"]],
        how="left",
        on=["PLAYER_ID"],
    )
    team_needs = update_prospect_ranker(picks_taken)
    player_rankings["TEAM_NEED"] = player_rankings.apply(
        get_value, axis=1, team=team_name, external_df=team_needs
    )
    player_rankings["VALUE"] = player_rankings[
        "PICK_VALUE"
    ] * user_weight + player_rankings["TEAM_NEED"] * (1 - user_weight)
    return player_rankings[["PLAYER_ID", "VALUE"]]
