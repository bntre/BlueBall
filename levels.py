
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
        ("ij", "A7", 500),
        ("k0", "W",  500),
        ("ab", "A7", 1000),
        ("cd", "A7", 1000, 500),
    ],
    'buttons': [
        ("e", "fg", "A3", 500),
    ],
},

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


] # end of LEVELS
