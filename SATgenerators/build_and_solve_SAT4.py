# Builds a DIMACS cnf formula, for minisat
# Searches for an AP-free tiling for SQUARES ONLY that is 90-degree rotationally symmetric
# We place only d tiles

from sys import argv
from pysat.solvers import Glucose3, Glucose4

H = int(argv[1]) # height of board
W = int(argv[2]) # width of board
L = int(argv[3]) # The max allowed length of AP

solver = Glucose4()


# A tetromino on the board is described by a triple (i, j, dir)
# (i, j) is the "center" of the tetromino, and dir is up, down, left or right.
# Thus, for example, the Ts covering (0, 0) are in the list:
# [(0, 1, 'd'), (1, 0, 'r')]
# And the Ts covering (0, 1) are in the list:
# [(0, 1, 'd'), (0, 2, 'd'), (1, 1, 'u'), (1, 1, 'l'), (1, 1, 'r')]

# Here we define a function that takes an (i, j, dir) tuple, and returns a
# list of the (up to) eight (i, j) pairs (squares) that the corresponding
# tetromino, and its three 90-degree rotations about the square center, covers
def sixteen_squares_of(v):
    i, j, d = v
    answer = []
    if d == 'd':
        pre_answer = [(i, j), (i, j-1), (i, j+1), (i+1, j)]
        # Add the rotated copies
        answer = [s for s in pre_answer]
        for (y, x) in pre_answer: answer.append((W-1-x, y)) # 90
        for (y, x) in pre_answer: answer.append((H-1-y, W-1-x)) # 180
        for (y, x) in pre_answer: answer.append((x, H-1-y)) # 270
    return [(s[0], s[1]) for s in answer if s[0] >= 0 and s[0] < H and s[1] >= 0 and s[1] < W]


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
all_tets = []
numTets = 0
for i in range(H):
    for j in range(W):
        for dir in ['d']:
            if dir == 'd' and not (i%4, j%4) in [(0, 2), (2, 3), (2, 0), (0, 1)]: continue
            if len(sixteen_squares_of((i, j, dir))) == 16:
                all_tets.append((i, j, dir))
                numTets += 1
#print("c There are a total of %d Ts on this %dx%d board" % (len(all_tets), H, W))


# Loop over the variables = tetrominos
# Map each tetromino to its squares, and
# Map each square to the list of tetrominos that cover it
tet_to_s = {}
s_to_tet = {(i, j):[] for i in range(H) for j in range(W)}
tet_to_idx = {}
idx = 1
for t in all_tets:
    tet_to_idx[t] = idx
    idx += 1
    tet_to_s[t] = sixteen_squares_of(t)
    for s in tet_to_s[t]:
        if s not in s_to_tet:
            s_to_tet[s] = [t]
        else:
            s_to_tet[s].append(t)
           

# count the number of clauses in ONCE
countOnce = 0
for i in range(H): # loop over the squares
    for j in range(W):
        tets = len(s_to_tet[(i, j)])
        countOnce += (tets * (tets-1)) / 2



# Count the number of NOAP clauses, that say there is no AP longer than L, the max length
countAP = 0
for i in range(1, H):   # (j, i) is the upper-left start of AP
    for j in range(1, W-1):
        for di in range(-((i-1)//L), (H-1-i)//L + 1):  # (dj, di) is the AP step
            for dj in range( (W-2-j)//L + 1):
                if di == 0 and dj == 0:
                    continue
                isAP = True
                for t in range(L+1): # Down tetromino
                    if (H - 1 - (i + t * di), j + t * dj, 'd') not in tet_to_idx:
                        isAP = False
                        break
                if isAP:
                    countAP += 1

#print( "c countAP =", countAP )
#print( "c", W*H, countOnce, countAP )
numClauses = W*H + countOnce + countAP
#print("p cnf %d %d" % (numTets, numClauses))

# Build the COVER clause, which says that each square is covered
for i in range(H):
    for j in range(W):
        this_clause = []
        for t in s_to_tet[(i, j)]:
            this_clause.append(tet_to_idx[t])
            #print( str(tet_to_idx[t]) + " ", end="")
        #print("0")
        solver.add_clause(this_clause)

# Build the ONCE clause, that says no overlapping tetrominos are selected
for i in range(H): # loop over the squares
    for j in range(W):
        tets = s_to_tet[(i, j)]
        for t1 in range(len(tets)): # loop over the pairs of Ts covering this square
            for t2 in range(t1+1, len(tets)):
                solver.add_clause([-tet_to_idx[tets[t1]], -tet_to_idx[tets[t2]]])
                #print ("-" + str(tet_to_idx[tets[t1]]) + " -" + str(tet_to_idx[tets[t2]]) + " 0") # Not both Ts picked

# Build the NOAP clause, that says there is no AP longer than L, the max length
for i in range(1, H):   # (j, i) is the upper-left start of AP
    for j in range(1, W-1):
        for di in range(-((i-1)//L), (H-1-i)//L + 1):  # (dj, di) is the AP step
            for dj in range( (W-2-j)//L + 1):
                if di == 0 and dj == 0:
                    continue
                   
                clause = ""
                this_clause = []
                for t in range(L+1): # Down tetromino
                    if (H - 1 - (i + t * di), j + t * dj, 'd') not in tet_to_idx:
                        clause = ""
                        this_clause = []
                        break
                    clause = clause + "-" + str(tet_to_idx[(H - 1 - (i + t * di), j + t * dj, 'd')]) + " "
                    this_clause.append(-tet_to_idx[(H - 1 - (i + t * di), j + t * dj, 'd')])
                if len(clause) > 0:
                    #print(clause + "0")
                    solver.add_clause(this_clause)


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
                b[W-j-1][i] = W*H + v # 90
                b[H-i-1][W-j-1] = 2*W*H + v # 180
                b[j][H-i-1] = 3*W*H + v # 270

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
    map_90 = {'d':'r', 'u':'l', 'l':'d', 'r':'u'}
    map_180 = {'d':'u', 'u':'d', 'l':'r', 'r':'l'}
    map_270 = {'d':'l', 'u':'r', 'l':'u', 'r':'d'}
    tiles = [all_tets[v-1] for v in solution if v > 0]
    sym_tiles_90 = [(W-j-1, i, map_90[d]) for i, j, d in tiles] # 90-degree symmetric tiles
    sym_tiles_180 = [(H-i-1, W-j-1, map_180[d]) for i, j, d in tiles] # 180-degree symmetric tiles
    sym_tiles_270 = [(j, H-i-1, map_270[d]) for i, j, d in tiles] # 270-degree symmetric tiles
    reps = sorted([(min(squares_of(t)), t[2]) for t in (tiles + sym_tiles_90 + sym_tiles_180 + sym_tiles_270)])
    dir_map = {'d':'0', 'r':'1', 'u':'2', 'l':'3'}
    tilestring = "".join([dir_map[t[1]] for t in reps])
    print(tilestring)



#print("countAP =", countAP)
solver.solve()
solution = solver.get_model() # Can also call solver.enum_models() to see all solutions
print(H, W, L)
#print(solution)
print_tiling_string(solution)
draw(solution)

