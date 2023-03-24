
LEVELS = [

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
    'name': "Walk in a circle",
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
    'map': """
W   W   W   W   W   W   
W               F   W   
W   c   b           W   
W   W   Pa  W   W   W   
W           H       W   
W   W   W   W   W   W   
""",
    'buttons': [
        ("a", "bc", "A3", 500),
    ]
},

{   'id': "2.2",
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
        ("a", "bc", "A7", 500),
        ("d", "ef", "A3", 500),
        ("g", "hi", "A7", 500),
    ]
},

{   'id': "2.3",
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
    'map': """
W   W   W   W   W   W   W   W   W   W   W   W   W   
W   b   c       Pa                              W   
W               W   W   W   W   W   W   W   H   W   
W                       W   W   W   Pd  W       W   
W   F   W   S00 e                       f       W   
W   W   W   W   W   W   W   W   W   W   W   W   W   
""",
    'buttons': [
        ("a", "bc", "A3S00", 100),
        ("d", "ef", "A3S00", 100),
    ]
},

{   'id': "2.5",
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

{   'id': "2.8",
    'map': """
W   W   W   W   W   W   W   W
W           T16              
W   F       W               H
W           W                
W           T06              
W   W   W   W   W   W   W   W
""",
},

{   'id': "2.9",
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
        ("mnm", " S10W/S12S11W/ S10W/ S10W/ S10W/S12S11W/ S10A3/ S10W/ S10W/S12S11W/ S10W/ S10W/ S10W/S12S11W/", 1500)
    ]
},

{   'id': "2.11",
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



] # end of LEVELS
