# FellerHochberg
Files associated with "T-Tetrominos in Arithmetic Progression" in Discrete Mathematics, by Emily Feller and Robert Hochberg.

# The SATgenerators Directory
Contains various python and Java files for creating CNF formulas in DIMACS format. These correspond to questions of the form "_Can a 20x20 rectangle be tiled with Ts, without an AP of length greater than 2?_" and are satisfiable if and only if the answer is "yes." 

Program | Details
------- | -------
`build_SAT.py` | Generates CNF formula, dumps it to standard output.<br>Usage: `python3 build_SAT.py 4 20 2`<br>builds a formula asking if a 4x20 rectangle can be tiled with no AP longer than 2
`build_and_solve_SAT.py` | Generates and solves CNFs using pysat. Prints a compact string representation of a solution if there is one, and an ASCII picture of the solution.<br>This output can be given to the java program DrawTiling, which will generate an encapsulated PostScript image.
`build_and_solve_SAT2.py` | Same as above, but searches for 180-degree, rotationally-symmetric tilings.
`build_and_solve_SAT4.py` | Same as above, but searches for 90-degree, rotationally-symmetric tilings of squares.
`DrawTiling.java`<br>`Poly.java` | Generates encapsulated PostScript files from tiling strings.<br>Compile: `javac DrawTiling.java` <br>Typical Run: `python3 build_and_solve_SAT.py 24 40 3 \| java DrawTiling`<br>Or you can read from a file: `java DrawTiling < file.txt` where the file's first line contains H W L, and the second line is the tiling string. Subsequent lines are ignored.<br>This saves the output to a file called `24x40-3.eps` for the example above, or `HxW-L.eps` in general.  See the code for "chain" and "shading" options.


# The Graphics Directory
Contains encapsulated PostScript and PDF pictures of tilings of rectangles. These tilings are extreme in the sense that they achieve the shortest length longest-AP among all tilings of the given rectangle. The EPS files were drawn by DrawTiling.java in the SATgenerators Directory. PDF file were created from the EPS files using the popular eps2pdf utility.

File names are of the form `HxW-L.eps` or `HxW-L.pdf`. H and W represent the height and width of the rectangle. L is the length of the longest AP in the given tiling.

# The 2DvdW Directory
Contains Python code for generating and solving CNFs that ask for a 2-coloring of an HxW rectangle with no monochromatic AP of length greater than L.

Usage:<br>
`python3 2dvdW.py 5 65 3` to search for a 2-coloring of a 5x62 rectangle with no monochromatic AP of length greater than 3.<br>
`python3 2dvdW.py 5 65 0` to find the smallest L such that a 5x62 rectangle has a 2-coloring with no monochromatic AP of length greater than L. It also produces that coloring.<br>
Whenever a coloring is found, it is saved in a file with name of the form 2D-5x65-4.txt<br>

Colorings of large rectangles that we have found are also present in this directory, of the form `2D-HxW-L.txt`, where `L` is the length of the longest monochromatic AP found in the coloring.

