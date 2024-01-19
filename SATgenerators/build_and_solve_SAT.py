# Builds a CNF formula, and solves it.
from sys import argv
from pysat.solvers import Glucose4  # Others are available in pysat

if len(argv) < 4: argv = [0, 8, 8, 2]
H = int(argv[1]) # height of board
W = int(argv[2]) # width of board
L = int(argv[3]) # The max allowed length of AP
ASSUM = list(map(int, argv[4:]))

solver = Glucose4()


# A tetromino on the board is described by a triple (i, j, dir)
# (i, j) is the "center" of the tetromino, and dir is up, down, left or right.
# Thus, for example, the Ts covering (0, 0) are in the list:
# [(0, 1, 'd'), (1, 0, 'r')]
# And the Ts covering (0, 1) are in the list:
# [(0, 1, 'd'), (0, 2, 'd'), (1, 1, 'u'), (1, 1, 'l'), (1, 1, 'r')]

# Here we define a function that takes an (i, j, dir) tuple, and returns a
# list of the (up to) four (i, j) pairs (squares) that the corresponding
# tetromino covers
def squares_of(v):
    i, j, d = v
    answer = []
    if d == 'u':
        answer = [(i, j), (i, j-1), (i, j+1), (i-1, j)]
    if d == 'd':
        answer = [(i, j), (i, j-1), (i, j+1), (i+1, j)]
    if d == 'l':
        answer = [(i, j), (i, j-1), (i+1, j), (i-1, j)]
    if d == 'r':
        answer = [(i, j), (i-1, j), (i, j+1), (i+1, j)]
    return [(s[0], s[1]) for s in answer if s[0] >= 0 and s[0] < H and s[1] >= 0 and s[1] < W]


# Start by building a list of all Ts that lie inside the board
# Note that we use ideas from Walkup's paper to create the modular conditions that limit
# the number of Ts that we need to consider.
all_tets = []
numTets = 0
for i in range(H):
    for j in range(W):
        for dir in ['u', 'd', 'l', 'r']:
            if dir == 'u' and not (i%4, j%4) in [(3, 2), (1, 3), (1, 0), (3, 1)]: continue
            if dir == 'd' and not (i%4, j%4) in [(0, 2), (2, 3), (2, 0), (0, 1)]: continue
            if dir == 'l' and not (i%4, j%4) in [(2, 3), (3, 1), (0, 1), (1, 3)]: continue
            if dir == 'r' and not (i%4, j%4) in [(2, 0), (3, 2), (0, 2), (1, 0)]: continue
            if len(squares_of((i, j, dir))) == 4:
                all_tets.append((i, j, dir))
                numTets += 1


# Loop over the variables = tetrominos
# Map each tetromino to its squares, and
# Map each square to the list of tetrominos that cover it
tet_to_s = {}
s_to_tets = {(i, j):[] for i in range(H) for j in range(W)}
tet_to_idx = {}
idx = 1
for t in all_tets:
    tet_to_idx[t] = idx
    idx += 1
    tet_to_s[t] = squares_of(t)
    for s in tet_to_s[t]:
        if s not in s_to_tets:
            s_to_tets[s] = [t]
        else:
            s_to_tets[s].append(t) 

# Build the COVER clause, which says that each square is covered
for i in range(H):
    for j in range(W):
        this_clause = []
        for t in s_to_tets[(i, j)]:
            this_clause.append(tet_to_idx[t])
        solver.add_clause(this_clause)


# Build the ONCE clause, that says no overlapping tetrominos are selected
for i in range(H): # loop over the squares
    for j in range(W):
        tets = s_to_tets[(i, j)]
        for t1 in range(len(tets)): # loop over the pairs of Ts covering this square
            for t2 in range(t1+1, len(tets)):
                solver.add_clause([-tet_to_idx[tets[t1]], -tet_to_idx[tets[t2]]])
                

countAP = 0

# Build the NOAP clause, that says there is no AP longer than L, the max length
for i in range(1, H):   # (j, i) is the upper-left start of AP
    for j in range(1, W-1):
        for di in range(-((i-1)//L), (H-1-i)//L + 1):  # (dj, di) is the AP step
            for dj in range( (W-2-j)//L + 1):
                if di == 0 and dj == 0:
                    continue
                
                this_clause = []
                for t in range(L+1): # Up tetromino
                    if (i + t * di, j + t * dj, 'u') not in tet_to_idx:
                        #clause = ""
                        this_clause = []
                        break
                    this_clause.append(-tet_to_idx[(i + t * di, j + t * dj, 'u')])
                if len(this_clause) > 0:
                    solver.add_clause(this_clause)
                    countAP += 1
                    
                this_clause = []
                for t in range(L+1): # Down tetromino
                    if (H - 1 - (i + t * di), j + t * dj, 'd') not in tet_to_idx:
                        this_clause = []
                        break
                    this_clause.append(-tet_to_idx[(H - 1 - (i + t * di), j + t * dj, 'd')])
                if len(this_clause) > 0:
                    #print(clause + "0")
                    solver.add_clause(this_clause)
                    countAP += 1
                
for i in range(1, H-1):   # (j, i) is the upper-left start of AP
    for j in range(1, W):
        for di in range(-((i-1)//L), (H-2-i)//L + 1):  # (dj, di) is the AP step
            for dj in range( (W-1-j)//L + 1):
                if di == 0 and dj == 0:
                    continue
                
                this_clause = []
                for t in range(L+1): # Left tetromino
                    if (i + t * di, j + t * dj, 'l') not in tet_to_idx:
                        this_clause = []
                        break
                    this_clause.append(-tet_to_idx[(i + t * di, j + t * dj, 'l')])
                if len(this_clause) > 0:
                    solver.add_clause(this_clause)
                    countAP += 1
                
                this_clause = []
                for t in range(L+1): # Right tetromino
                    if (i + t * di, W - 1 - (j + t * dj), 'r') not in tet_to_idx:
                        this_clause = []
                        break
                    this_clause.append(-tet_to_idx[(i + t * di, W - 1 - (j + t * dj), 'r')])
                if len(this_clause) > 0:
                    solver.add_clause(this_clause)
                    countAP += 1


# Print a string representation of the tiling to stdout
def draw(solution):
    if not solution: return

    # Fill a board with the tetromino numbers
    b = [[0 for j in range(W)] for i in range(H)]
    for v in solution:
        if v > 0:
            t = all_tets[v-1]
            ss = squares_of(t)
            for i, j in ss:
                b[i][j] = v

    # Draw the board
    print("+--"*W+"+")
    for i in range(H):
        print("|", end="")
        for j in range(W-1):
            print("  " + (" " if (b[i][j] == b[i][j+1]) else "|"), end = "")
        print("  |")
        for j in range(W):
            print("·" + ("--" if i == H-1 or b[i][j] != b[i+1][j] else "  "), end="")
        print("+")


# The "tiling string" gives a compact represenation of a tiling by Ts
# The idea is that one goes row-by-row through the rectangle. Each time a blank
# square is encountered, use the next symbol in the tiling string to determine
# the direction of T to use, according to dir_map below
#
# There is a Java program in this repo that turns tiling strings into tilings
def print_tiling_string(solution):
    tiles = [all_tets[v-1] for v in solution if v > 0]
    reps = sorted([(min(squares_of(t)), t[2]) for t in tiles])
    dir_map = {'d':'0', 'r':'1', 'u':'2', 'l':'3'}
    tilestring = "".join([dir_map[t[1]] for t in reps])
    print(tilestring)

solver.solve(assumptions=ASSUM)
solution = solver.get_model()
if solution:
    #print(solution) // Print list of T's. Used ones are positive.
    print(H, W, L)
    print_tiling_string(solution)
    draw(solution)

