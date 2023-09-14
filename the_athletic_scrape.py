import pandas as pd
from fuzzywuzzy import fuzz

text = """
Tier 1: Bubble generational player and elite NHL player
1
Connor Bedard
REGINA
C
WHL
Tier 2: Elite NHL player
2
Adam Fantilli
MICHIGAN
C
BIG10
3
Matvei Michkov
SKA ST. PETERSBURG
RW
RUSSIA
Tier 3: NHL All-Star
4
Leo Carlsson
OREBRO
C
SWEDEN
5
William Smith
USA U-18
C
NTDP
Tier 4: Top of the lineup player
6
David Reinbacher
KLOTEN
D
SWISS
7
Nate Danielson
BRANDON
C
WHL
8
Dalibor Dvorsky
AIK
C
SWEDEN 2
9
Danil But
YAROSLAVL JR.
LW
RUSSIA JR
10
Dmitriy Simashev
YAROSLAVL JR.
D
RUSSIA JR
Tier 5: Bubble top and middle of the lineup player
11
Ryan Leonard
USA U-18
RW
NTDP
12
Gabriel Perreault
USA U-18
RW
NTDP
13
Samuel Honzek
VANCOUVER
LW
WHL
14
Matthew Wood
UCONN
RW
H EAST
15
Tom Willander
ROGLE JR.
D
SWEDEN JR
16
Brayden Yager
MOOSE JAW
C
WHL
17
Zach Benson
WINNIPEG
LW
WHL
18
David Edstrom
FROLUNDA JR.
C
SWEDEN JR
19
Oliver Moore
USA U-18
C
NTDP
20
Colby Barlow
OWEN SOUND
LW
OHL
Tier 6: Middle of the lineup player
21
Quentin Musty
SUDBURY
LW
OHL
22
Axel Sandin Pellikka
SKELLEFTEA JR.
D
SWEDEN JR
23
Charlie Stramel
WISCONSIN
C
BIG10
24
Eduard Sale
BRNO
LW
CZECHIA
25
Tanner Molendyk
SASKATOON
D
WHL
26
Oliver Bonk
LONDON
D
OHL
27
Calum Ritchie
OSHAWA
C
OHL
28
Otto Stenberg
FROLUNDA JR.
C
SWEDEN JR
29
Gavin Brindley
MICHIGAN
C
BIG10
30
Mikhail Gulyayev
OMSK JR.
D
RUSSIA JR
31
Lukas Dragicevic
TRI-CITY
D
WHL
32
Danny Nelson
USA U-18
C
NTDP
33
Anton Wahlberg
MALMO JR.
C
SWEDEN JR
34
Maxim Strbak
SIOUX FALLS
D
USHL
35
Ethan Gauthier
SHERBROOKE
RW
QMJHL
36
Bradly Nadeau
PENTICTON
LW
BCHL
37
Oscar Fisker Molgaard
HV 71
C
SWEDEN
38
Michael Hrabal
OMAHA
G
USHL
Tier 7: Projected to play NHL games
39
Carson Rehkopf
KITCHENER
LW
OHL
40
Etienne Morin
MONCTON
D
QMJHL
41
Arttu Karki
TAPPARA JR.
D
FINLAND JR
42
Theo Lindstein
BRYNAS
D
SWEDEN
43
Juraj Pekarcik
NITRA
LW
SLOVAKIA
44
Luca Cagnoni
PORTLAND
D
WHL
45
Nico Myatovic
SEATTLE
LW
WHL
46
Kasper Halttunen
HIFK
RW
FINLAND
47
Daniil Karpovich
YEKATERINBURG JR.
D
RUSSIA JR
48
Felix Nilsson
ROGLE JR.
C
SWEDEN JR
49
Carey Terrance
ERIE
C
OHL
50
Beau Akey
BARRIE
D
OHL
51
Caden Price
KELOWNA
D
WHL
52
Cameron Allen
GUELPH
D
OHL
53
Gavin McCarthy
MUSKEGON
D
USHL
54
Andrew Gibson
SAULT STE. MARIE
D
OHL
55
Lenni Hameenaho
ASSAT
RW
FINLAND
56
Coulson Pitre
FLINT
RW
OHL
57
Mathieu Cataford
HALIFAX
C
QMJHL
58
Hunter Brzustewicz
KITCHENER
D
OHL
59
Riley Heidt
PRINCE GEORGE
C
WHL
60
Kalan Lind
RED DEER
LW
WHL
61
Jakub Dvorak
LIBEREC
D
CZECHIA
62
Aram Minnetian
USA U-18
D
NTDP
63
Andrew Strathmann
YOUNGSTOWN
D
USHL
64
Emil Pieniniemi
KARPAT JR.
D
FINLAND JR
65
Koehn Ziemmer
PRINCE GEORGE
RW
WHL
66
Martin Misiak
YOUNGSTOWN
RW
USHL
67
Yegor Rimashevskiy
DYNAMO MOSCOW JR.
RW
RUSSIA JR
68
Andrew Cristall
KELOWNA
LW
WHL
69
Alex Ciernik
SODERTALJE
LW
SWEDEN 2
70
Aiden Fink
BROOKS
RW
AJHL
71
Adam Gajan
CHIPPEWA
G
NAHL
72
Scott Ratzlaff
SEATTLE
G
WHL
73
Trey Augustine
USA U-18
G
NTDP
74
Carson Bjarnason
BRANDON
G
WHL
75
Aydar Suniev
PENTICTON
LW
BCHL
76
Roman Kantserov
MAGNITOGORSK JR.
RW
RUSSIA JR
77
Jacob Fowler
YOUNGSTOWN
G
USHL
Tier 8: Has a chance to play games
78
Alex Pharand
SUDBURY
C
OHL
79
Brandon Svoboda
YOUNGSTOWN
C
USHL
80
Jesse Kiiskinen
PELICANS JR.
RW
FINLAND JR
81
Ethan Miedema
KINGSTON
LW
OHL
82
Milton Oscarson
OREBRO
C
SWEDEN
83
Tristan Bertucci
FLINT
D
OHL
84
Samuel Mayer
PETERBOROUGH
D
OHL
85
Matteo Fabrizi
RED DEER
D
WHL
86
Hannes Hellberg
LEKSAND JR.
RW
SWEDEN JR
87
Zach Nehring
SHATTUCK - ST.MARY'S PREP
RW
HIGH MN
88
Petter Vesterheim
MORA JR.
C
SWEDEN JR
89
Gabriel Szturc
KELOWNA
C
WHL
90
Matthew Mania
SUDBURY
D
OHL
91
Dylan MacKinnon
HALIFAX
D
QMJHL
92
Hoyt Stanley
VICTORIA
D
BCHL
93
Axel Hurtig
ROGLE JR.
D
SWEDEN JR
94
Nick Lardis
HAMILTON
LW
OHL
95
Easton Cowan
LONDON
RW
OHL
96
Hudson Malinoski
BROOKS
C
AJHL
97
Tuomas Uronen
HIFK JR.
RW
FINLAND JR
98
Tyler Peddle
DRUMMONDVILLE
LW
QMJHL
99
Michael Emerson
CHICAGO
RW
USHL
100
Luca Pinelli
OTTAWA
C
OHL
101
Denver Barkey
LONDON
C
OHL
102
Zeb Forsfjall
SKELLEFTEA JR.
C
SWEDEN JR
103
Rasmus Kumpulainen
PELICANS JR.
C
FINLAND JR
104
Frantisek Dej
MODRE KRIDLA SLOVAN
C
SLOVAKIA 2
105
Felix Unger Sorum
LEKSAND JR.
RW
SWEDEN JR
106
Noah Dower Nilsson
FROLUNDA JR.
LW
SWEDEN JR
107
Jayden Perron
CHICAGO
RW
USHL
108
Jesse Nurmi
KOOKOO JR.
LW
FINLAND JR
109
Beckett Hendrickson
USA U-18
C
NTDP
110
Connor Levis
KAMLOOPS
RW
WHL
111
Emil Jarventie
ILVES JR.
LW
FINLAND JR
112
William Whitelaw
YOUNGSTOWN
RW
USHL
113
Noel Nordh
BRYNAS JR.
LW
SWEDEN JR
114
Brady Cleveland
USA U-18
D
NTDP
115
Konstantin Volochko
DINAMO-SHINNIK JR.
D
RUSSIA JR
116
Gracyn Sawchyn
SEATTLE
C
WHL
117
Jaden Lipinski
VANCOUVER
C
WHL
118
Zachary Schulz
USA U-18
D
NTDP
119
Paul Fischer
USA U-18
D
NTDP
120
Drew Fortescue
USA U-18
D
NTDP
121
Albert Wikman
FARJESTAD JR.
D
SWEDEN JR
122
Quinton Burns
KINGSTON
D
OHL
123
Larry Keenan
CULVER ACADEMY
D
HIGH IN
124
Rasmus Larsson
VASTERAS JR.
D
SWEDEN JR
125
Konnor Smith
PETERBOROUGH
D
OHL
126
Axel Landen
HV 71 JR.
D
SWEDEN JR
127
Tanner Adams
TRI-CITY
RW
USHL
128
Nikita Nedopekin
SKA ST. PETERSBURG JR.
C
RUSSIA JR
129
Nikita Ishimnikov
YEKATERINBURG JR.
D
RUSSIA JR
130
Vadim Moroz
MINSK
RW
RUSSIA
131
Max Lundgren
DES MOINES
G
USHL
132
Timur Mukhanov
OMSK JR.
LW
RUSSIA JR
133
Andrei Loshko
CHICOUTIMI
C
QMJHL
134
Alexander Rykov
CHELMET
RW
RUSSIA 2
135
Nikita Susuyev
SPARTAK JR.
RW
RUSSIA JR
136
Artyom Kashtanov
YEKATERINBURG JR.
C
RUSSIA JR
137
Damian Clara
FARJESTAD JR.
G
SWEDEN JR
138
Carsen Musser
USA U-18
G
NTDP
139
Kristers Steinbergs
VALBO U18
G
SWE JR U18
140
Yegor Sidorov
SASKATOON
RW
WHL
141
Ivan Anoshko
DINAMO-SHINNIK JR.
C
RUSSIA JR
142
Ruslan Khazheyev
CHELYABINSK JR.
G
RUSSIA JR

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