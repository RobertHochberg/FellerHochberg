# Builds and prints a DIMACS cnf formula for finding a tiling of an HxW rectangle
# without an AP of tiles of length greater than L
#
# Usage: python3 build_SAT.py 20 24 3
#   To create a CNF to search for a tiling of a 20x24 rectangle with no AP of length > 3

from sys import argv


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
def make_all_tets():
    rv = []
    numTets = 0
    for i in range(H):
        for j in range(W):
            for dir in ['u', 'd', 'l', 'r']:
                if dir == 'u' and not (i%4, j%4) in [(3, 2), (1, 3), (1, 0), (3, 1)]: continue
                if dir == 'd' and not (i%4, j%4) in [(0, 2), (2, 3), (2, 0), (0, 1)]: continue
                if dir == 'l' and not (i%4, j%4) in [(2, 3), (3, 1), (0, 1), (1, 3)]: continue
                if dir == 'r' and not (i%4, j%4) in [(2, 0), (3, 2), (0, 2), (1, 0)]: continue
                if len(squares_of((i, j, dir))) == 4:
                    rv.append((i, j, dir))
                    numTets += 1
    print("c There are a total of %d Ts on this %dx%d board" % (len(rv), H, W))
    return rv



# Compute the number of variables and clauses so that we can print the header line
# We do these counts as we build the clauses, but because we print as we go, we just
# have a separate, easy-to-debug function that, alas, repeats some work.
def print_header(H, W, L, all_tets, s_to_tet, tet_to_idx):
    # count the number of clauses in ONCE
    countOnce = 0
    for i in range(H): # loop over the squares
        for j in range(W):
            tets = len(s_to_tet[(i, j)])
            countOnce += (tets * (tets-1)) / 2


    # Count the number of NOAP clauses, for the header line
    countAP = 0
    for i in range(1, H):   # (j, i) is the upper-left start of AP
        for j in range(1, W-1):
            for di in range(-((i-1)//L), (H-1-i)//L + 1):  # (dj, di) is the AP step
                for dj in range( (W-2-j)//L + 1):
                    if di == 0 and dj == 0:
                        continue
                    isAP = True
                    for t in range(L+1): # Up tetromino
                        if (i + t * di, j + t * dj, 'u') not in tet_to_idx:
                            isAP = False
                            break
                    if isAP:
                        countAP += 2
                    
    for i in range(1, H-1):   # (j, i) is the upper-left start of AP
        for j in range(1, W):
            for di in range(-((i-1)//L), (H-2-i)//L + 1):  # (dj, di) is the AP step
                for dj in range( (W-1-j)//L + 1):
                    if di == 0 and dj == 0:
                        continue
                    isAP = True
                    for t in range(L+1): # Left tetromino
                        if (i + t * di, j + t * dj, 'l') not in tet_to_idx:
                            isAP = False
                            break
                    if isAP:
                        countAP += 2

    numClauses = W*H + countOnce + countAP
    print("p cnf %d %d" % (len(all_tets), numClauses))

# Build maps
# tts maps tetrominos to the list of squares they cover
# stt maps squares to the list of tetrominos that cover that square
# tti maps tetrominos to their location in the list of all_tets
def make_maps(H, W, all_tets):
    # Loop over the variables = tetrominos
    # Map each tetromino to its squares, and
    # Map each square to the list of tetrominos that cover it
    # Also map each tetromino to its location in the list of tets
    stt = {(i, j):[] for i in range(H) for j in range(W)}
    tti = {}
    idx = 1
    for t in all_tets:
        tti[t] = idx
        idx += 1
        tts = squares_of(t)
        for s in tts:
            if s not in stt:
                stt[s] = [t]
            else:
                stt[s].append(t)  
    return stt, tti



# The function that prints the CNF
def build_and_print_CNF(H, W, L, s_to_tets, tet_to_idx, ASSUM):
    # Build the COVER clause, which says that each square is covered
    for i in range(H):
        for j in range(W):
            for t in s_to_tets[(i, j)]:
                print(str(tet_to_idx[t]) + " ", end="")
            print(" 0")


    # Build the ONCE clause, that says no overlapping tetrominos are selected
    for i in range(H): # loop over the squares
        for j in range(W):
            tets = s_to_tets[(i, j)]
            for t1 in range(len(tets)): # loop over the pairs of Ts covering this square
                for t2 in range(t1+1, len(tets)):
                    print ("-" + str(tet_to_idx[tets[t1]]) + " -" + str(tet_to_idx[tets[t2]]) + " 0") # Not both Ts picked


    countAP = 0 # Number of arithmetic progressions of length L+1

    # Build the NOAP clause, that says there is no AP longer than L, the max length
    for i in range(1, H):   # (j, i) is the upper-left start of AP
        for j in range(1, W-1):
            for di in range(-((i-1)//L), (H-1-i)//L + 1):  # (dj, di) is the AP step
                for dj in range( (W-2-j)//L + 1):
                    if di == 0 and dj == 0:
                        continue
                    
                    clause = ""
                    for t in range(L+1): # Up tetromino
                        if (i + t * di, j + t * dj, 'u') not in tet_to_idx:
                            clause = ""
                            break
                        clause = clause + "-" + str(tet_to_idx[(i + t * di, j + t * dj, 'u')]) + " "
                    if len(clause) > 0:
                        print(clause + "0")
                        countAP += 1
                        
                    clause = ""
                    for t in range(L+1): # Down tetromino
                        if (H - 1 - (i + t * di), j + t * dj, 'd') not in tet_to_idx:
                            clause = ""
                            break
                        clause = clause + "-" + str(tet_to_idx[(H - 1 - (i + t * di), j + t * dj, 'd')]) + " "
                    if len(clause) > 0:
                        print(clause + "0")
                        countAP += 1
                    
    for i in range(1, H-1):   # (j, i) is the upper-left start of AP
        for j in range(1, W):
            for di in range(-((i-1)//L), (H-2-i)//L + 1):  # (dj, di) is the AP step
                for dj in range( (W-1-j)//L + 1):
                    if di == 0 and dj == 0:
                        continue
                    
                    clause = ""
                    for t in range(L+1): # Left tetromino
                        if (i + t * di, j + t * dj, 'l') not in tet_to_idx:
                            clause = ""
                            break
                        clause = clause + "-" + str(tet_to_idx[(i + t * di, j + t * dj, 'l')]) + " "
                    if len(clause) > 0:
                        print(clause + "0")
                        countAP += 1
                    
                    clause = ""
                    this_clause = []
                    for t in range(L+1): # Right tetromino
                        if (i + t * di, W - 1 - (j + t * dj), 'r') not in tet_to_idx:
                            clause = ""
                            break
                        clause = clause + "-" + str(tet_to_idx[(i + t * di, W - 1 - (j + t * dj), 'r')]) + " "
                    if len(clause) > 0:
                        print(clause + "0")
                        countAP += 1

    # Print the assumption clauses, requiring certain tets in the solution
    for t in ASSUM:
        print(t, 0)


# Main
if __name__ == "__main__":
    if len(argv) < 4: argv = ['dummy', 8, 8, 2]
    H = int(argv[1]) # height of board
    W = int(argv[2]) # width of board
    L = int(argv[3]) # The max allowed length of AP

    # Add extra parameters in positions >= 4 if you would like the CNF to require that the tiles
    # with given indices in the all_tets list are present in the searched-for tilings. 
    # These are collected in the ASSUM list.
    #
    # So python3 build_SAT.py 20 24 3 1 17 searches for 
    ASSUM = list(map(int, argv[4:]))

    # Create all tetrominos that could be in a solution
    all_tets = make_all_tets()

    # Build the maps: square->Ts and T->idx
    s_to_tets, tet_to_idx = make_maps(H, W, all_tets)

    # Build the header for the CNF instance
    print_header(H, W, L, all_tets, s_to_tets, tet_to_idx)

    # Generate and print the CNF instance
    build_and_print_CNF(H, W, L, s_to_tets, tet_to_idx, ASSUM)