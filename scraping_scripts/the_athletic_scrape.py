import pandas as pd
from fuzzywuzzy import fuzz

text = """
Tier 1
1
Connor Bedard
C1, REGINA
🇨🇦
C
WHL






Tier 2
2
Matvei Michkov
RW1, SOCHI
🇷🇺
RW
KHL



3
Adam Fantilli
C2, U. OF MICHIGAN
🇨🇦
C
NCAA



4
Leo Carlsson
C3, ÖREBRO
🇸🇪
C
SHL



5
William Smith
C4, U18
🇺🇸
C
NTDP





Tier 3
6
Zach Benson
LW1, WINNIPEG
🇨🇦
LW
WHL



7
Gabriel Perreault
LW2, U18
🇺🇸
LW
NTDP



8
Dalibor Dvorsky
C5, AIK
🇸🇰
C
HOCKEYALLSVENSKAN




9
Oliver Moore
C6, U18
🇺🇸
C
NTDP




10
Matthew Wood
RW2, UCONN
🇨🇦
RW
NCAA


11
Ryan Leonard
RW3, U18
🇺🇸
RW
NTDP



12
David Reinbacher
RHD1, KLOTEN
🇦🇹
RHD
NL



13
Andrew Cristall
LW3, KELOWNA
🇨🇦
LW
WHL




14
Eduard Sale
LW4, BRNO
🇨🇿
LW
CZECHIA




15
Brayden Yager
C7, MOOSE JAW
🇨🇦
C
WHL




16
Axel Sandin Pellikka
RHD2, SKELLEFTEA
🇸🇪
RHD
SHL


Tier 4
17
Colby Barlow
LW5, OWEN SOUND
🇨🇦
LW
OHL



18
Quentin Musty
LW6, SUDBURY
🇺🇸
LW
OHL


19
Calum Ritchie
C8, OSHAWA
🇨🇦
C
OHL




20
Nate Danielson
C9, BRANDON
🇨🇦
C
WHL



21
Mikhail Gulyayev
LHD1, OMSKIE
🇷🇺
LHD
MHL



22
Bradly Nadeau
LW7, PENTICTON
🇨🇦
LW
BCHL

23
Riley Heidt
C10, PRINCE GEORGE
🇨🇦
C
WHL


24
Gavin Brindley
C11, MICHIGAN
🇺🇸
C
NCAA


25
Samuel Honzek
LW8, VANCOUVER
🇸🇰
LW
WHL

26
Daniil But
LW9, YAROSLAVL
🇷🇺
LW
MHL


27
Tom Willander
RHD3, ROGLE
🇸🇪
RHD
J20

28
Otto Stenberg
C12, FROLUNDA
🇸🇪
C
J20



Tier 5
29
Jayden Perron
RW4, CHICAGO
🇨🇦
RW
USHL



30
Ethan Gauthier
RW5, SHERBROOKE
🇨🇦
RW
QMJHL


31
Koehn Ziemmer
RW6, PRINCE GEORGE
🇨🇦
RW
WHL

32
Etienne Morin
LHD2, MONCTON
🇨🇦
LHD
QMJHL


33
Alex Ciernik
LW10, SÖDERTÄLJE
🇸🇰
LW
HOCKEYALLSVENSKAN


34
Kasper Halttunen
RW7, HIFK
🇫🇮
RW
LIIGA





35
Dmitri Simashev
LHD3, YAROSLAVL
🇷🇺
LHD
KHL

36
Lukas Dragicevic
RHD4, TRI-CITY
🇨🇦
RHD
WHL

37
Charlie Stramel
C13, U. OF WISCONSIN
🇺🇸
C
NCAA



38
Nick Lardis
LW11, HAMILTON
🇨🇦
LW
OHL

39
Oscar Fisker Mølgaard
C15, HV71
🇩🇰
C
SHL

40
Hunter Brzustewicz
RHD5, KITCHENER
🇺🇸
RHD
OHL


41
Oliver Bonk
RHD6, LONDON
🇨🇦
RHD
OHL

42
Tanner Molendyk
LHD4, SASKATOON
🇨🇦
LHD
WHL

43
Noah Dower Nilsson
LW12, FROLUNDA
🇸🇪
LW
J20

44
Gracyn Sawchyn
C14, SEATTLE
🇺🇸
C
WHL

45
Luca Cagnoni
LHD5, PORTLAND
🇨🇦
LHD
WHL

46
Caden Price
LHD6, KELOWNA
🇨🇦
LHD
WHL

47
Carson Rehkopf
LW13, KITCHENER
🇨🇦
LW
OHL

48
Mathieu Cataford
C16, HALIFAX
🇨🇦
C
QMJHL

49
David Edstrom
C17, FROLUNDA
🇸🇪
C
J20

50
Danny Nelson
C18, U18
🇺🇸
C
NTDP



51
Luca Pinelli
C19, OTTAWA
🇨🇦
C
OHL

52
Aram Minnetian
RHD7, U18
🇺🇸
RHD
NTDP

53
Lenni Hameenaho
RW8, ASSAT
🇫🇮
RW
LIIGA

54
Aydar Suniev
LW14, PENTICTON
🇷🇺
LW
BCHL


55
Trey Augustine
G1, U18
🇺🇸
G
NTDP


56
Michael Hrabal
G2, OMAHA
🇨🇿
G
USHL


57
William Whitelaw
RW9, YOUNGSTOWN
🇺🇸
RW
USHL

58
Theo Lindstein
LHD7, BRYNÄS
🇸🇪
LHD
SHL

59
Jesse Kiiskinen
RW10, PELICANS
🇫🇮
RW
LIIGA



60
Beau Akey
RHD8, BARRIE
🇨🇦
RHD
OHL

61
Alexander Rykov
RW11, CHELYABINSK
🇷🇺
RW
VHL

62
Kalan Lind
LW15, RED DEER
🇨🇦
LW
WHL

63
Andrew Strathmann
LHD8, YOUNGSTOWN
🇺🇸
LHD
USHL

64
Jacob Fowler
G3, YOUNGSTOWN
🇺🇸
G
USHL

65
Roman Kantserov
RW12, MAGNITOGORSK
🇷🇺
RW
MHL

66
Nico Myatovic
LW17, SEATTLE
🇨🇦
LW
WHL

67
Juraj Pekarcik
LW16, NITRA
🇸🇰
LW
SLOVAKIA

68
Adam Gajan
G4, GREEN BAY
🇸🇰
G
USHL

Tier 6
69
Scott Ratzlaff
G5, SEATTLE
🇨🇦
G
WHL

70
Anton Wahlberg
C20, MALMO
🇸🇪
C
J20

71
Maxim Strbak
RHD9, SIOUX FALLS
🇸🇰
RHD
USHL

72
Coulson Pitre
RW14, FLINT
🇨🇦
RW
OHL

73
Aiden Fink
RW13, BROOKS
🇨🇦
RW
AJHL

74
Carey Terrance
C21, ERIE
🇺🇸
C
OHL

75
Felix Nilsson
C22, ROGLE
🇸🇪
C
J20

76
Tristan Bertucci
LHD9, FLINT
🇨🇦
LHD
OHL

77
Gavin McCarthy
RHD10, MUSKEGON
🇺🇸
RHD
USHL

78
Jesse Nurmi
LW18, KOOKOO
🇫🇮
LW
LIIGA U20

79
Emil Jarventie
LW19, ILVES
🇫🇮
LW
LIIGA U20

80
Arttu Karki
LHD10, TAPPARA
🇫🇮
LHD
LIIGA U20

81
Jaden Lipinski
C23, VANCOUVER
🇨🇦
C
WHL

82
Connor Levis
RW15, KAMLOOPS
🇨🇦
RW
WHL

83
Denver Barkey
C24, LONDON
🇨🇦
C
OHL

84
Tanner Ludtke
C25, LINCOLN
🇺🇸
C
USHL

85
Jakub Dvorak
LHD11, LIBEREC
🇨🇿
LHD
CZECHIA

86
Ethan Miedema
LW20, KINGSTON
🇨🇦
LW
OHL

87
Martin Misiak
RW16, YOUNGSTOWN
🇸🇰
RW
USHL

88
Matthew Mania
RHD11, SUDBURY
🇺🇸
RHD
OHL

89
Carson Bjarnason
G6, BRANDON
🇨🇦
G
WHL

90
Cam Squires
RW17, CAPE BRETON
🇨🇦
RW
QMJHL

91
Felix Unger Sorum
RW18, LEKSANDS
🇸🇪
RW
J20

92
Cameron Allen
RHD12, GUELPH
🇨🇦
RHD
OHL

93
Rasmus Kumpulainen
C26, PELICANS
🇫🇮
C
LIIGA U20

94
Mazden Leslie
RHD13, VANCOUVER
🇨🇦
RHD
WHL

95
Beckett Hendrickson
C27, U18
🇺🇸
C
NTDP

96
Noel Nordh
LW21, BRYNAS
🇸🇪
LW
J20

97
Easton Cowan
C28, LONDON
🇨🇦
C
OHL

98
Hoyt Stanley
RHD14, VICTORIA
🇨🇦
RHD
BCHL

99
Zach Nehring
RW19, SHATTUCK
🇺🇸
RW
USHS

100
Angus MacDonell
C29, MISSISSAUGA
🇨🇦
C
OHL

"""

lines = text.split('\n')
data = []

i = 0
while i < len(lines):
    line = lines[i].strip()
    if line.startswith('Tier'):
        i += 1
        continue
    if line.isdigit():
        ranking = line
        player = lines[i+1].strip()
        data.append([ranking, player])
        i += 5
    else:
        i += 1

# Create a DataFrame from the data and write it to a CSV file
df1 = pd.DataFrame(data, columns=['RANK', 'PLAYER_NAME'])

# Read the second CSV file
df2 = pd.read_csv('PLAYER_IDS.csv')  # Replace 'file2.csv' with your second CSV file

# Initialize an empty DataFrame for the merged data
merged_df = pd.DataFrame(columns=['RANK', 'PLAYER_NAME', 'PLAYER_ID'])

# For each player in df1, find the best fuzzy match in df2 and add it to merged_df if the match score is above 90%
for index, row in df1.iterrows():
    best_match = None
    best_score = -1

    for index2, row2 in df2.iterrows():
        score = fuzz.ratio(row['PLAYER_NAME'], row2['PLAYER_NAME'])
        if score > best_score:
            best_match = row2
            best_score = score

    if best_score > 90:
         merged_df.loc[len(merged_df)] = [row['RANK'], row['PLAYER_NAME'], best_match['PLAYER_ID']]
    else:
        print(row['PLAYER_NAME'], best_score)

# Write the merged dataframe to a new CSV file
merged_df[["PLAYER_NAME","PLAYER_ID","RANK"]].to_csv('merged.csv', index=False)