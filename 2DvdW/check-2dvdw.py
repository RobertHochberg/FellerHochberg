# For each file in the current directory, with name of the for 2D-HxW-L.txt, checks to make sure the 
# coloring given in the file has no monochromatic AP of length > L

import glob
import re

def makes_mono_AP(b, i1, j1, i2, j2, L):
     H, W = len(b), len(b[0])
     color = b[i1][j1]
     di = i2-i1
     dj = j2-j1

     # See if these starting points make an AP that fits. If not, no AP
     lasti, lastj = i1 + (L-1)*di, j1 + (L-1)*dj
     if lasti < 0 or lasti >= H or lastj < 0 or lastj >= W:
          return False
     
     # Now check the AP for monochromaticity
     for h in range(1, L):
          i, j = i1 + h * di, j1 + h * dj
          if b[i][j] != color:
               return False
    
    # If we make it here, it's an AP that fits and it's monochromatic
     return True

     
files = glob.glob("2D-*.txt")
p = re.compile("2D-(\d+)x(\d+)-(\d+).txt")
                   
for fname in files:
    m = p.match(fname)
    if not m: continue

    print("File:", fname, end=": ")
    # Parameters according to the file name
    fH, fW, fL = int(m.group(1)), int(m.group(2)), int(m.group(3))

    # Now open the file and see if it matches the parameters
    f = open(fname, "r")
    line = f.readline()
    H, W, L = tuple(map(int, line.strip().split(" ")))
    #print("Numbers:", fH, fW, fL, H, W, L)
    
    # Check that the file has the right name
    if (H, W, L) != (fH, fW, fL):
        print(f'Error: File name does not match internal contents.')
        exit(1)

    # Read the board from the file
    board = []
    for line in f:
        row = line.strip().split(" ")
        if len(row) != W:
            print("Error: Row has the wrong length.")
            exit(1)
        board.append(row)
    if len(board) != H:
            print("Error: Coloring has too few rows.")
            exit(1)

    # Make sure the board has no monochromatic AP of length greater than L
    # We make this painfully brute-force, to be different from the way the 
    # SAT instance creators generated all the APs
            
    # For each starting point (i1, j1) and each next point (i2, j2) below or to the right,
    # Check for an AP starting with those two elements
    for i1 in range(H):
         for j1 in range(W):
              for i2 in range(H):
                   for j2 in range(j1, W):
                        if j1 == j2 and i1 <= i2: continue
                        #print("isjs", i1, j1, i2, j2)
                        if makes_mono_AP(board, i1, j1, i2, j2, L+1):
                             print(f'Error: Monochromatic AP found starting at ({i1}, {j1})-({i2}, {j2})')
                             exit(1)
    print("Good")
              