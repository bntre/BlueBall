r"""

Level map coding:
    W       Wall
    B       Box
    Ln      Laser (direction)
    G       Glass
    Jn      Glass Laser (direction)
    H       Hero
    F       Finish
    *       Checkpoint
    An      Arrow (index)
    Snn     Spike (index1, index2)
    P       Push-button
    D       Double
    Tnn     Teleport (direction, color)
    
    Lowercase letter - alias for a cell (for setting dynamics)


Permanent dynamics:
    (<animation path cells>, <moving blocks>, <frame delay in ms>, [optional phase])
        animation path cells        e.g. "abcb"
        moving blocks               e.g. "A5/A6" ("/" for next row)
    E.g.:
        'dynamics': [
            ("ab", "A2A0A0A1", 750)


Button dynamics:
    (<button cell>, <animation path cells>, <moving blocks>, <frame delay in ms>)
    E.g.:
        'buttons': [
            ("a", "bc", "A1S00", 100),

"""

LEVELS = [

# Debug level - deleted on startup
{   'id': 0,
    'name': "temp",
    'map': """
W   W   W   W   W   W   W   W   W   W   W   W   W
W   F                   i                   *   W
W                               T3B             W
L0          J3                  B               W
W                                               W
W       G                                       L1
W                       j                       W
W   B   B                   B                   W
W                   T0B                         W
W           W   H                           *   W
W                                       S12 S11 W
W               B                               W
W                   T01         T11 T03         W
T1A k               T0A                     S25 W
W                               T13         S24 W
W               D                   a   c   S23 W
W   Pe                  V           b   d       W
W   f               g   V                       W
""",
    'dynamics': [
        ("ij", " A7/A7", 500),
        ("k0", "W",  500),
        ("ab", "A7", 1000),
        ("cd", "A7", 1000, 500),
    ],
    'buttons': [
        ("e", "fg", "A3", 500),
    ],
},

#---------------------------------------------------------
# Episode 1

{   'id': "1.1",
    'name': "Bypass",
    'map': """
W   W   W   W   W   W   W   W   W
W   W   F                   W   W
W   W   W                   W   W
W                           W   W
W       W   L0              W   W
W                           W   W
W   W   W                   W   W
W   W   H                   W   W
W   W   W   W   W   W   W   W   W
""" },

{   'id': "1.2",
    'name': "Put a barrier",
    'map': """
W   W   W   W   W   W
W   F               W
W   L0              W
W           B       W
W           H       W
W   W   W   W   W   W
""" },

{   'id': "1.3", 
    'name': "Three boxes",
    'map': """
W   W   W   W   W           F
W   W   L0                  W
W   W       W   B           L1
L0                  W       W
W   W       W       W       W
W   W   B   W       W       W
    H                   B    
W   W   W   W   W           W
""" },

{   'id': "1.4", 
    'name': "Diagonals",
    'map': """
L7              H           W   W   W   
            B               W   W   W   
            W               W   W   W   
        B               L5  W   W   W   
            B           W   W   W       
    B                                   
                                        
                            W           
                                    L1  
L4                  F                   
""" },

{   'id': "1.5", 
    'name': "Star",
    'map': """
L7                      L3                  H   L5  
            B               B                       
                                    B               
                                                    
    B                                               
                                                    
L0                          W   L0          L1  W   
                                                F   
                                                    
                                                    
                                                    
                                                    
                                                    
""" },

{   'id': "1.6",
    'name': "Train to hell",
    'map': """
W   W   W   W   W   W   W   W   W   W   W   W
W   a                                   b   W
W                                           W
W   W                               W   W   W
W   F                               W   H   W
W                                           W
W                                           W
W   W   W   W   W   W   W   W   W   W   W   W
""",
    'dynamics': [
        ("ab", "L3", 500)
    ]
},

{   'id': "1.7",
    'name': "Action",
    'map': """
W   W   W   W   W   W   W   W   W   W   W
W   F           a                   L1  W
W                           c           W
W   L0                                  W
W                                       W
W   L0                                  W
W                                       W
W                                       W
W   L0          b                   W   W
W                           d       H   W
W   W   W   W   W   W   W   W   W   W   W
""",
    'dynamics': [
        ("ab", "L2", 500),
        ("cd", "L3", 500),
    ]
},

{   'id': "1.8",
    'name': "Jogging",
    'map': """
W   W   W   F   W   W
L0      a           W
L0                  W
L0                  W
L0                  W
L0                  W
L0                  W
L0      b           W
L0                  W
W   W   W   W   H   W
""",
    'dynamics': [
        ("ab", "A5/A6", 500),
    ]
},

{   'id': "1.9",
    'name': "Toughie",
    'map': """
W   W   W   F   W   W   W       L3                  W   
W   W   W       W   W   W                           W   
W   W   a       L0                                  W   
L0                                                  W   
L0                                  B               W   
L0      b                                           W   
W   W       W   W   W   W   W   W   W   W   W       W   
W   W   W                                           W   
W   W   W       W   L3  L3  L3  L3  L3  L3  L3  W   W   
W   W   W   *   W   c                   d           W   
W   W   W       L0                                  W   
L0  e   g                                           W   
L0  f   h                                           W   
W   W   W   W   W   W   W   W   W   W   W   W   H   W   
""",
    'dynamics': [
        ("ab", "A5/A6",  500),
        ("cd", "A2A0A1", 1000),
        ("ef", "A7", 2000),
        ("gh", "A7", 2000, 1000),
    ]
},

{   'id': "1.10",
    'name': "Jogging 2",
    'map': """
W   W   L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  L3  W   W   
W                                                                                                               F   W   
W   a                                                                                               b               W   
W                                                                   G                                               W   
W                                                           L3                          L3                          W   
W                       L3          L2          L1                      L2  G   G               L2                  W   
W                                                                                                       L3          W   
W                                                                       L3              L1  W   W   W               W   
W   H                                                                                                               W   
W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   
""",
    'dynamics': [
        ("ab", "A2A0A0A1", 750),
    ]
},

{   'id': "1.11",
    'name': "Look at this",
    'map': """
    a               b   W       G           c   
f                       G       J3              
                        G               W       
            H           G               W       
                        W               W       
g                                       W       
W   G   G   G   G   i               j   W       
                G                       W       
F               G   G   W   W   W   W   W       
                                                
                        B       W   W   W       
                        W   W   e           d   
""",
    'dynamics': [
        ("ab",   "L3", 1000),
        ("cded", "L2",  500),
        ("fg",   "L0", 1000),
        ("ij",   "A3",  500),
    ]
},

{   'id': "1.12",
    'name': "Jogging 3",
    'map': """
W   W   W   W   W   W   W   W   W   W   W   L3  W   
W                                           a   W   
W                                               W   
W   H                                           W   
W                                               W   
W                                               W   
W   W   W   W   W   W       G   G   G   G       W   
W                           G                   W   
W       G   G   G   G   G   G                   W   
W                           G                   W   
W   W   W   W   W   W       G                   W   
W                           G                   W   
W       G   G   G   G   G   G                   W   
W                                               W   
W                                               W   
W       J3      J3      J3      J3      J3      W   
W                                               W   
W                                               W   
W                                               W   
W                                               W   
W                                               W   
W                                               W   
W   W   W   W   W       W   W   W   W   W       W   
W                                               W   
W       G   G   G   G   G   G   G   G   G       W   
W           G   G   G                           W   
W   W           G           G   G               W   
W       G       G       G       G               W   
W       G       G       G       G               W   
W       G       G       G       G               W   
W       G               G       G               W   
W       G   G   G   G   G   G   G               W   
W                                               W   
W       G   G   G   G   G   G   G   G   G       W   
W                                       F   Bb  L1  
W   W   W   W   W   W   W   W   W   W   W   W   W   
""",
    'dynamics': [
        ("ab", "J1", 675),
    ]
},


#---------------------------------------------------------
# Episode 2

{   'id': "2.1",
    'name': "The button",
    'map': """
W   W   W   W   W   W   
W               F   W   
W   c   b           W   
W   W   Pa  W   W   W   
W           H       W   
W   W   W   W   W   W   
""",
    'buttons': [
        ("a", "bc", "A2", 500),
    ]
},

{   'id': "2.2",
    'name': "Three buttons",
    'map': """
W   W   W   W   W   W   W   W   W   W   W   W   
W   F   W   W   W   W   W   Pd  W   W   H   W   
W   e           f   W   W       W   W       W   
W                   W   W       W   W       W   
W                       W   B       W       W   
W                       W           W       W   
W                   h   Pg      b   Pa      W   
W   W   W   W   W   i   W   W   c   W   W   W   
""",
    'buttons': [
        ("a", "bc", "A6", 500),
        ("d", "ef", "A1", 500),
        ("g", "hi", "A6", 500),
    ]
},

{   'id': "2.3",
    'name': "Spike",
    'map': """
W   W   W   W   W   W   
W   W           F   W   
W   W               W   
d   c       W   W   W   
W   W               W   
b   a       W   W   W   
W   W           H   W   
W   W   W   W   W   W   
""",
    'dynamics': [
        ("ab", "A3S00", 750),
        ("cd", "A3S00", 750),
    ]
},

{   'id': "2.4",
    'name': "Black pocket",
    'map': """
W   W   W   W   W   W   W   W   W   W   W   W   W   
W   b   c       Pa                              W   
W               W   W   W   W   W   W   W   H   W   
W                       W   W   W   Pd  W       W   
W   F   W   S00 e                       f       W   
W   W   W   W   W   W   W   W   W   W   W   W   W   
""",
    'buttons': [
        ("a", "bc", "A1S00", 100),
        ("d", "ef", "A1S00", 100),
    ]
},

{   'id': "2.5",
    'name': "Caves",
    'map': """
W   W   W   W   W   W   W   W   W   W   
W   a   W   c   W   e   W   g   W   H   
    b       d       f       h           
                                        
                                        
    W   W   i   W   W   W   W   W   W   
    S31 S30 j   S30 S33 S31         F   
    S32             S34 S32 n   m       
        l   S22     S35     p   o       
    S20 k   S21 s               r       
W   W       W   W   W   W   W   W   W   
""",
    'dynamics': [
        ("ab", "A7/S31/S32", 800, 0),
        ("cd", "A7/S31/S32", 800, 200),
        ("ef", "A7/S31/S32", 800, 400),
        ("gh", "A7/S31/S32", 800, 600),
        ("ij", "A7/S30",     800),
        ("kl", "S20/A7",    1000),
        ("mn", "S10A3",      800),
        ("op", "S10A3",     1000),
        ("rs", "S10A3",      600),
    ]
},

{   'id': "2.6",
    'name': "Circle",
    'map': """
    F   S12 S11 W       W   S00         
    S20         S30     S30     S22     
    W   S00     S20 b           S21     
        S12 S11 W   a           W       
d   c       S10 W                       
                            S10 W       
            S20     S20         S30     
        S10 W       W   S01 S02 H       
""",
    'dynamics': [
        ("ab", "WS00/WS01S02/S30", 1000),
        ("cd", "WS00/S31/S32", 1000),
    ]
},

{   'id': "2.7",
    'name': "Waves",
    'map': """
W   W   W   W   W   W   W   W   W   W   
W               H                   W   
W   W   W                   W   W   W   
a       b           k       l           
c   d   e           m   n   o           
f       g           p       q           
h   i   j           r   s   t           
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
W   W   W                   W   W   W   
    u       v   Pw  Px      y           
S22                                 S22 
S21 S20             F           S20 S21 
""",
    'dynamics': [
        ("ba",   "A3S01S02////A3S01S02////A3S01S02////A3S01S02", 500),
        ("dedc", "A3S01S02////A3S01S02////A3S01S02////A3S01S02", 500),
        ("fg",   "A3S01S02////A3S01S02////A3S01S02",             500),
        ("ihij", "A3S01S02////A3S01S02////A3S01S02",             500),
        ("kl",   "S12S11A3////S12S11A3////S12S11A3////S12S11A3", 500),
        ("nmno", "S12S11A3////S12S11A3////S12S11A3////S12S11A3", 500),
        ("qp",   "S12S11A3////S12S11A3////S12S11A3",             500),
        ("stsr", "S12S11A3////S12S11A3////S12S11A3",             500),
    ],
    'buttons': [
        ("w", "uv", "A1S00/A1S00/A1S00", 80),
        ("x", "yx", "S10A2/S10A2/S10A2", 80),
    ]
},

{   'id': "2.8",
    'name': "Teleport",
    'map': """
W   W   W   W   W   W   W   W
W           T19              
W   F       W               H
W           W                
W           T09              
W   W   W   W   W   W   W   W
""",
},

{   'id': "2.9",
    'name': "Four rooms",
    'map': """
W   W   W   W   W   W   W   W   W   W   W   W   
W                   W   F       c   W       W   
W           B       W           b           W   
W       Pa          W   W   W               W   
W               d       e   W               W   
W   W   W   W       G       W   W   W   T30 W   
W               g       f                   W   
W                   W       W       W       W   
W       T20         W           H           W   
W                   W       W       W       W   
W                   W                       W   
W   W   W   W   W   W   W   W   W   W   W   W   
""",
    'dynamics': [
        ("defg", "A8", 500),
        ("efgd", "A8", 500),
        ("fgde", "A8", 500),
    ],
    'buttons': [
        ("a", "bc", "A5", 100),
    ]
},

{   'id': "2.10",
    'name': "Down and up",
    'map': """
W   W   W   W   W   W   W   W   W   W   W   W   
W           H           W   F               W   
T10                 a   T00 S00 n   m           
T11 b                   T01 S00                 
T12     c               T02 S00                 
T13         d           T03 S01 S02             
T14             e       T04 S00                 
T15                 f   T05 S00                 
T16 g                   T06 S00                 
T17     h               T07 S01 S02             
T18         i           T08 S00                 
T19             j       T09 S00                 
T1A                 k   T0A S00                 
W   W   W       W   W   W   S01 S02             
W   W   W       W   W   W   S00                 
W   W   W       W   W   W   W                   
W   W   W       S33 S31 S30 S31             W   
W   W   W       S34 S32     S32     S12 S11 W   
W   W   W       S35                 S25     W   
W   W   W               S22 S22 S22 S24     W   
W   W   W   *   S20 S20 S21 S21 S21 S23     W   
W   W   W   W   W   W   W   W   W   W   W   W   
""",
    'dynamics': [
        ("a1", "S10A2S00", 500),
        ("b1", "S10A2S00", 500),
        ("c1", "S10A2S00", 500),
        ("d1", "S10A2S00", 500),
        ("e1", "S10A2S00", 500),
        ("f1", "S10A2S00", 500),
        ("g1", "S10A2S00", 500),
        ("h1", "S10A2S00", 500),
        ("i1", "S10A2S00", 500),
        ("j1", "S10A2S00", 500),
        ("k1", "S10A2S00", 500),
        ("mn", " S10W/S12S11W/ S10W/ S10W/ S10W/S12S11W/ S10A3/ S10W/ S10W/S12S11W/ S10W/ S10W/ S10W/S12S11W/", 1500)
    ]
},

{   'id': "2.11",
    'name': "Labyrinth",
    'map': """
W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W
W   H           W                                                   W   
W       W   W   W   W   W   W       W   W   W   W   W   W   W       W   
W                   W                                       W   W   W
W       W       W   W       W   W   W   W   W       W       W       W
W   W   W           W                   W           W       W       W
W               W   W   W   W       W   W   S20     W   W           W
W       W               W               W   W       W               W
W       W       W       W       W   W       W       W       W   W   W
W       W   W   W               W   W               W               W
W       W       W   W   W       W           W       W   W   W       W
W               W       W   W   W       W   W       W               W
W   W   W       W                           W       W       W       W
W           W   W       W   W   W   W   W   W   W   W       W       W
W                       W                                   W       W
W       W   W   W   W   W   W       W   W   W   W   W   W   W       W
W                                               W               F   W
W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W
""",
},

{   'id': "2.12",
    'name': "Nether",
    'map': """
W   T2B W   W   W   W   W   W   W       W       W   W           *       p           T0A
W   i                                   S30     S30 W       W   W   W   q           W
W       W   W   W   W                       j       W       W   W   W               W
W       T1A     H                   W       k       W   l                           W
W       W                           W   W           W                               W
W       W   W   W   c   W       W   W               W   m                           W
W       W   W   W   d   W       W   W   S20     S20 W                               W
W       W   W   W               W   W   W       W   W                               W
W       a   b           f   e       W   S30     S30 W                               W
W       W       B   h   W   W   W   W               W   W   W   W   W   W   W       W
W       W       Pr  g   W   W   W   W   W           W       S30     S31     S30     W
W       W   W   W       W   W   W   W               W       n       S32             W
W           B   Pt  W                               W       o                       W
W       W   W   W       Ps  B           S20     S20 W                               W
W       W                               W       W   W                               W
W   T3B W   W   W   W   W   W   W   W   W   W   W   W       S20             S20 F   W
""",
    'dynamics': [
        ("ab", "A3S00",  800),
        ("cd", "A7/S30", 800),
        ("ef", "S10A3",  800),
        ("gh", "S20/A7", 800),
        ("i3", "S20/A6/S30/S20/A6/S30/S20/A6/S30///S20/A6/S30", 800),
        ("jk", "S20/A7/S30/////S20/A7/S30", 800),
        ("lm", "S25 S25 S25 /S24 S24 S24 /S23 S23 S23 /A7 A7 A7 ", 800),
        ("ml", " S25 S25 S25/ S24 S24 S24/ S23 S23 S23/ A7 A7 A7", 800),
        ("on", "S22   S22/S21 S20 S21/A7WWWA7W/  S30", 800),
    ],
    'buttons': [
        ("r", "pq", "S20/A6", 100),
        ("s", "pq", " S20/ A6", 100),
        ("t", "pq", "  S20/  A6", 100),
    ]
},


#---------------------------------------------------------
# Episode 3

{   'id': "3.1",
    'name': "The double",
    'map': """
W   W   W   W
W       F   W
W   H       W
W   W   W   W
W           W
W   D       W
W   W   W   W
""",
},

{   'id': "3.2",
    'name': "The double in danger",
    'map': """
W   W   W   W
W   D   S30 W
W           W
W   W   W   W
W   H       W
W       F   W
W   W   W   W
""",
},

{   'id': "3.3",
    'name': "Hero in danger",
    'map': """
W   W   W   W   W   W   L3  W   W   
W   W   W   W   W   W   a   b   W   
W       D   W   W       H   W   W   
W       Pc      W               W   
W               W           F   W
W   W   W   W   W   W   W   W   W   
""",
    'buttons': [
        ("c", "ab", "A1", 500)
    ]
},

{   'id': "3.4",
    'name': "Elevator",
    'map': """
W   D   Pa          W   
W   W   W       S20 W   
W   W   W   W   W   W   
W   W   W       F   W   
W   H       b       W
W   W   W   c   W   W
""",
    'buttons': [
        ("a", "bc", "A6", 100)
    ]
},

{   'id': "3.5",
    'name': "Double pass",
    'map': """
W   W   W   W   W   W   W   W   W   W
W                       S30 W   S31 W
W           W   S00             S32 W
W   S00                         D   W
W   W   W   L3  W   W   W   W   W   W
W   F   S30                 S30     W
W           W                       W
W                       S20     H   W
W   W   W   W   W   W   W   W   W   W
""",
},

{   'id': "3.6",
    'name': "Frame",
    'map': """
W   W   W   W   W   W   W   W   W   W   
W   L3                      L1      W   
W                                   S10
W           W   S00     S10 W       S10
W       H           D               S10
W                                   S10
W                   F               S10
W   L0                      L2      S10
W   W   W   W   W   W   W   W   W   W   
""",
},

{   'id': "3.7",
    'name': "Don't be afraid",
    'map': """
W   W   W   W   W
T11 a   b       W
W           H   W
W               W
W               W
W   Pc      D   W
W               L1
W       T01 F   W
W               W
W   W   W   W   W
""",
    'buttons': [
        ("c", "ab", "A1", 100),
    ]
},

{   'id': "3.8",
    'name': "The face",
    'map': """
W   W   W   W   W   W   W   W   W   
T15     D   T06 W   T16     D   T05 
T11     S20 T02 W   T12         T01 
W   W   W   W       W   W   W   W   
W   W   W   W   W   W   W   W   W   
W   T10         H           T00 W   
W   W   F                   W   W   
W   W   W   W   W   W   W   W   W   
""",
},

{   'id': "3.9",
    'name': "Quadruple pass",
    'map': """
W   W   W   W   W   W   W   W   W   W   W   W   W   W
T15             S31 H   T06 T10         S30     D   T01
W               S32     W   W                       W
W   S25                 W   W                       W   
W   S24                 W   W                   S22 W   
W   S23                 W   W           F       S21 W   
W   W   W   W   W   W   W   W   W   W   W   W   W   W   
T11                 D   T05 T16     S30         D   T00
W                       W   W                       W
W       S25             W   W   S01 S02             W
W       S24     S22     W   W                       W
W       S23     S21     W   W                       W
W   W   W   W   W   W   W   W   W   W   W   W   W   W   
""",
},

{   'id': "3.10",
    'name': "We are not welcome",
    'map': """
V       V   V   V   V   V           V   
V       V   V   V   V   V       V       
    V   W   S00 F   D   V       V   H   
    V       V       V   W   W   W       
    V       V                           
W   V   W   W   W       W   W   W   W   
""",
},

{   'id': "3.11",
    'name': "Side by side",
    'map': """
        Pa  L3  S00 D       H   
        B                       
            V                   
        V       b   c           
        V           V           
        F       V               
""",
    'buttons': [
        ("a", "bc", "S12S11A1", 100),
    ]
},

{   'id': "3.12",
    'name': "Hardcore",
    'map': """
W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   L3                      L3  j   k   
W   W   W   W   W   W   Pa  W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   l   m                               
W   W   W   W   W   W   B   W   b               W   W   W   W   W   W   W   W   W   W                                       
    S33                 V   S31 c                           T01 T10     S30 W   e   W       B           V                   
    S34         V           S32                                             W       W                                   S10 
H   S35                                         S20         T06 T11             d   *                               F       
            S22     V           W   S25 S22     W                       S10 W   W   W               W                   p   
            S21                     S24 S21                     S20         W   W   L0              n   o               q   
W   W   W   W   W   W   S00 g   f   S23 W   W   W   W   W   W   W   W   W   W   W   L0                                  S10 
W   W   W   W   W   W   S10 W   W   W   W   W   W   W   W   W   W   W   W   W   W   W                   W               S10 
W   W   W   W   W   W       W   W   W   W   W   W   W   W   W   W   W   W   W   W   W                                   S10 
S31                 S33             S30 S31 S30     S30     T09 T16         W       W                                   S10 
S32                 S34                 S32                             S10 W       W                                   S10 
D                   S35                         S20         T00 T19         V                                           S10 
    i                       S22 S22 S22 S22     W                           W   W   W                                       
S20 h   S20                 S21 S21 S21 S21                 S20             W   W   W                                       
W       W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   L2                                  
""",
    'dynamics': [
        ("bc", "A7WWA7/S31S31S30S31/S32S32 S32", 1000),
        ("fg", "L2", 1000),
        ("hi", "S20/A7", 800),
        ("jk", "L3", 800),
        ("lm", "A3//////////////A3", 1000),
        ("no", "J2/J3", 1000),
        ("pq", "L1", 1000),
    ],
    'buttons': [
        ("a", "de", "A5////////A5", 200),
    ]
},

] # end of LEVELS
