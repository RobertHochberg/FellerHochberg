from sys import argv
from pysat.solvers import Glucose4  # Others are available in pysat

solver = Glucose4()

# L is the length of the longest allowed monochromatic AP
H, W, L = map(int, argv[1:4])

# For every starting point (i, j), build APs of length L+1 starting there.
# T/F are the two colors of dots
APs = []  # Will hold our APs
# Each AP is itself a list
# Variables are numbered:
# 1 2 3
# 4 5 6
# 7 8 9
for i in range(1, H+1):
    for j in range(1, W+1):
        for dx in range(-((j-1)//(L)), (W-j)//(L) + 1):
            for dy in range(-((i-1)//(L)), (H-i)//(L) + 1):
                if dx == 0 and dy == 0: continue
                AP = []
                for t in range(L+1):
                    point = (i+t*dy, j+t*dx)
                    AP.append((point[0]-1)*W + point[1])
                APs.append(AP)

# Print the DIMACS cnf formatted problem, and/or create the clauses for the solver
# print("p cnf", H*W, 2*len(APs)) # uncomment to print DIMACS header
for ap in APs:
    solver.add_clause(ap)
    solver.add_clause([-x for x in ap])

    # Uncomment below if you want to print the CNF to stdout
    """
    for v in ap:
        print(v, end=" ")
    print("0")
    for v in ap:
        print(-v, end=" ")
    print("0")
    """

solver.solve()
solution = solver.get_model()

# Print the board if there is a solution, else "No Solution"
if solution:
    colors = ['*' if x > 0 else '-' for x in solution]
    for i in range(H):
        print(" ".join(colors[i*W:(i+1)*W]))
else:
    print("No Solution")
