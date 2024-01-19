# FellerHochberg
Files associated with "T-Tetrominos in Arithmetic Progression" in Discrete Mathematics

Left aligned Header | Right aligned Header | Center aligned Header
| :--- | ---: | :---:
Content Cell  | Content | Content Cell
Content Cell  | Content Cell | Content Cell
# The SAT Generators Directory
Contains various python and Java files for creating CNF formulas in DIMACS format. These correspond to questions of the form "_Can a 20x20 rectangle be tiled with Ts, without an AP of length greater than 2?_" and are satisfiable if and only if the answer is "yes." 

Program | Details
------- | -------
`build_SAT.py` | Generates CNF formula, dumps it to standard output.<br>Usage: `python3 build_SAT.py 4 20 2`<br>builds a formula asking if a 4x20 rectangle can be tiled with no AP longer than 2
`build_and_solve_SAT.py | Generates and solves CNFs using pysat. Prints a compact string representation of a solution if there is one, and an ASCII picture of the solution.<br>This output can be given to the java program DrawTiling, which will generate an encapsulated PostScript image. See the code for "chain" and "shading" options.
`DrawTiling.java` | Generates encapsulated PostScript files from tiling strings.<br>Compile: `javac DrawTiling.java`<br>Typical Run: `python3 build_and_solve_SAT.py 40 40 3 \| java DrawTiling`<br>Or you can read from a file: `java DrawTiling < file.txt` where the file's first line contains H W L, and the second line is the tiling string.
