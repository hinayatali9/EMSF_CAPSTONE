def rank_pre_processing(df):
  '''
  Creates a dictionary with a dataframe filled with players in the league prospect pool for each position and age group.
  Players under the age of 19 are grouped with the 19 year old datafarames.

  Input: Prospect pool dataframe
  Output: Dictionary with multiple prospect pool dataframes for each age and position
  '''
  df.loc[(df['Specific POS']=='LW'), 'Specific POS'] = 'F'
  df.loc[(df['Specific POS']=='C'), 'Specific POS'] = 'F'
  df.loc[(df['Specific POS']=='RW'), 'Specific POS'] = 'F'

  ages = [19,20,21,22,23]
  positions = ['F','LD','RD','G']
  players = {}

  for position in positions:
    for age in ages:
      if age == 19:
        players['df_' + str(position) + '-' + str(age)] = df[(df['Specific POS']==position) & (df['AGE']<=age)]
      else:
        players['df_' + str(position) + '-' + str(age)] = df[(df['Specific POS']==position) & (df['AGE']==age)]

  return players


def fill_missing_teams(df_dict, key, col):
    '''
    This function finds the minimum Z-score across each dataframe and applies a lower Z-score value to teams 
    without any players in it. This data gets stored in the dataframes such that every team gets a percentile 
    ranking later in the code. And these ranking must be lower than the teams with actual prospects for each 
    age group and position. 
    '''
    Teams = ['COL','CHI','CBJ','STL','BOS','MTL','VAN','WSH','ARI','NJD','ANA',
        'CGY','PHI','CAR','NYI','WPG','LAK','VGK','SEA','TOR','TBL','EDM','FLA',
        'PIT','NSH','NYR','DET','BUF','OTT','SJS','DAL','MIN']

    index_set = set(df_dict[key]['Team'])
    min_value = df_dict[key][col].min()

    # Find elements in lst that are not in the index
    missing_elements = [x for x in Teams if x not in index_set]

    # If there are missing elements, add them to the DataFrame with value 0 in column 'A'
    if missing_elements:
        missing_df = pd.DataFrame({col: [(min_value-1)]*len(missing_elements), 'Team':missing_elements})
        df_dict[key] = pd.concat([df_dict[key], missing_df])

    return df_dict


def score_and_rank(df_dict):
  '''
  This function first scores the prospects in the entire pool, keeping seperate dataframes and scoring systems for different 
  age groups and positions. After Z-scores are calculated, the missing teams are filled in and exponentials of these scores
  are taken to ensure that every prospect contributes positively to the strength of the team. 
  
  After the scoring is done, the exponential Z-scores are summed over for every team in the respective dataframes and the teams
  are ranked. Unncessary columns are removed and what remains is the team name and rank in each age/position dataframe.

  Input: Dictionary of dataframes for the entire prospect pool, with all metrics included.
  Output: Dictionary of dataframes with team names and prospect pool rankings for each group. 
  '''
  df_dict_out = {}

  for i in df_dict:
    if len(df_dict[i])==1:
      df_dict[i]['zscore'] = 0
    else:
      if 'G' in i:
        df_dict[i]['zscore'] = (df_dict[i]['Goalie Equivalency'] - df_dict[i]['Goalie Equivalency'].mean())/df_dict[i]['Goalie Equivalency'].std()
      else:
        df_dict[i]['zscore'] = (df_dict[i]['NHL eP'] - df_dict[i]['NHL eP'].mean())/df_dict[i]['NHL eP'].std()

    df_dict = fill_missing_teams(df_dict, i, 'zscore')
    df_dict[i]['exp_zscore'] = np.exp(df_dict[i]['zscore'])

    df_dict_out[i] = df_dict[i].groupby('Team').sum('exp_zscore')
    df_dict_out[i]['rank'] = df_dict_out[i]['exp_zscore'].rank(pct=True)#ascending = False)
    df_dict_out[i].drop(columns=['AGE','GP','G','A','P','GAA','SV%','Goalie Equivalency','NHL eP','exp_zscore','zscore'], inplace = True)

  return df_dict_out


def group_ranker(rank_dfs, weights):
  '''
  This function creates final prospect pool rankings for every position by amalgamating the individual prospect rankings 
  for every age group. A set of weights for every age group is used to determin the weighted sum. All newly drafted players
  get combined with the 19 year old dataframe, such that they don't have an overly drastic effect on the rankings.  

  Input: Dictionary of dataframes with team names and prospect pool rankings for each age/position group.
  Output: Dataframe of team names and prospect pool rankings for each position. 
  '''
  result = pd.DataFrame()

  for key in rank_dfs:
    position, age = key.split('-')  # split the key into position and age
    weight = weights[int(age)]  # get the weight for this age

    df = rank_dfs[key].copy() # get the DataFrame for this key
    df['rank'] *= weight  # multiply the percentile rankings by the weight

    if position in result:
        result[position] += df['rank']  # add to the existing DataFrame for this position
    else:
        result[position] = df['rank']

  for key in result:
    result[key] = result[key].rank(pct=True)
    result[key] = 1 - result[key] # flips percentiles around for optimization model

  return result