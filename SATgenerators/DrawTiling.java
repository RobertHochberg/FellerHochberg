import java.io.IOException;
import java.io.PrintWriter;
import java.util.Scanner;
import java.util.HashMap;

/*
 * This class reads a string representation of a tiling, and
 * generates a ps of the result.
 */
public class DrawTiling {
	private static Poly poly;
	private static boolean[][] board;
	private static int[][] tiled;
	private static int HEIGHT = 4;
	private static int WIDTH = 6;
    private static int LENGTH = 2;
	private static String tilingString;

	static Scanner scanner;

	public static void main(String[] args) {
		scanner = new Scanner(System.in);
        readBoard();
        initialize();
        findSolution();
        System.out.println(drawBoardPic());
        generateEpsImage();
	}

	// polyominos are encoded this way:
	// 1 | 4 | 7
	// 2 | 5 | 8
	// 3 | 6 | 9
    // Do some simple setup of the board, polys
	public static void initialize() {
		boolean ttet[] = { true, true, true, false, true, false };
		poly = new Poly(3, 2, ttet, 4, false);
		board = new boolean[HEIGHT + 2][WIDTH + 2];
		tiled = new int[HEIGHT + 2][WIDTH + 2];
	}

	public static void solve(int siStart) {
		int si = 1, sj = 1; // Hold leftmost of topmost open square
		Poly currentPoly;
		boolean canFit; // can the board take the current polyomino?
		String pic;

		int count = 0;
		for (int i = 0; i < tilingString.length(); i++) {
			// set si and sj to be the leftmost of the topmost open squares
			findsisj: for (si = 1; si <= HEIGHT; si++)
				for (sj = 1; sj <= WIDTH; sj++)
					if (!board[si][sj])
						break findsisj;
			char c = tilingString.charAt(i);
			int ornum = (3 + (int) (c - '0')) % 4;
			currentPoly = poly.shapes[ornum];
			int offset = currentPoly.offset;
			if (offset < sj && sj + currentPoly.w - offset < WIDTH + 2 && si + currentPoly.l < HEIGHT + 2) {
				canFit = true;
				for (int pj = 0; pj < currentPoly.w; pj++)
					for (int pi = 0; pi < currentPoly.l; pi++)
						if (currentPoly.b[pj * currentPoly.l + pi] && board[si + pi][sj + pj - offset])
							canFit = false;
				if (!canFit) {
					System.out.println("Illegal Tiling String for w=" + WIDTH + " and h=" + HEIGHT);
					return;
				} else {
					for (int pj = 0; pj < currentPoly.w; pj++)
						for (int pi = 0; pi < currentPoly.l; pi++)
							if (currentPoly.b[pj * currentPoly.l + pi]) {
								board[si + pi][sj + pj - offset] = true;
								tiled[si + pi][sj + pj - offset] = 4 * count + ornum;
							}
					count++;
				}
			}
		}
	}


    // Read a board (H, W, tiling string) from stdin. Assign to tilingString by side effect
	public static void readBoard() {
		Scanner scanner = new Scanner(System.in);
		
		tilingString = "";
		while(!scanner.hasNextInt()) scanner.nextLine();
		HEIGHT = scanner.nextInt();
		WIDTH = scanner.nextInt();
		LENGTH = scanner.nextInt();
		int targetLength = WIDTH * HEIGHT / 4; // # of Ts in the tiling string

		scanner.nextLine();
		while(tilingString.length() < targetLength) {
			String s = scanner.nextLine();
			s = s.replaceAll("[. ]", "");
			tilingString = tilingString + s;
		}
		scanner.close();
	}


    
    // Call the solver. Note that the solver uses the tiling string deterministically.
	public static void findSolution() {
		solve(1);
	}

	/**
	 * dn is the "drawing number" for going into the filename
	 */
	public static void generateEpsImage() {

		// Set colorDirection to true to give different directions different colors
		boolean colorDirection = false;

        // Set drawChains to true to draw the Korn-Pak chains atop the tiling
		boolean drawChains = false;

		String chainWidth = "0.05";
		String chainColor = "0.5 1.0 0.5 0.2";
		String betweenWidth = "0.1";
		String betweenColor  = "0.2 0.2 0.2";
		String arrowheadWidth = "0.08";

		PrintWriter p = null;
		try {
            String filename = HEIGHT + "x" + WIDTH + "-" + LENGTH + ".eps";
			p = new PrintWriter(filename);
		} catch (IOException ex) {
			ex.printStackTrace();
		}
		// Add stuff that all our images will have
		p.println("%!PS-Adobe-3.0 EPSF-3.0\n" + "%%BoundingBox: 0 0 " + (10 * WIDTH + 4) + " " + (10 * HEIGHT + 4)
				+ "\n" + "/cp {closepath} bind def\n" + "/ef {eofill} bind def\n" + "/l {lineto} bind def\n"
				+ "/m {moveto} bind def\n" + "/n {newpath} bind def\n" + "/s {stroke} bind def\n"
				+ "0.000 0.000 0.000 setrgbcolor\n" + "0.050 setlinewidth\n" + "1 setlinejoin 1 setlinecap\n");
		p.println("2 " + (10 * HEIGHT + 2) + " translate\n" + "10 -10 scale");


		// Print the tiles
		if (drawChains) {
			p.println("0.8 0.8 1.0 setrgbcolor\n");
			p.println("0.2 setlinewidth\n");
		} else {
			p.println("0.0 0.0 0.0 setrgbcolor\n");
			p.println("0.07 setlinewidth\n");
		}

		// Shade the tile squares
		if(colorDirection){
			for (int i = 1; i <= HEIGHT; i++) {
				for (int j = 1; j <= WIDTH; j++) {
					if (tiled[i][j] > -1) {
						String fillstr = "";
						if (tiled[i][j] % 4 == 0)
							fillstr = " gsave 0.500 0.500 1.000 setrgbcolor 1.000 eofill grestore \n";
						if (tiled[i][j] % 4 == 1)
							fillstr = " gsave 0.500 1.000 0.500 setrgbcolor 1.000 eofill grestore \n";
						if (tiled[i][j] % 4 == 2)
							fillstr = " gsave 1.000 0.500 0.500 setrgbcolor 1.000 eofill grestore \n";
						if (tiled[i][j] % 4 == 3)
							fillstr = " gsave 1.000 0.200 1.000 setrgbcolor 1.000 eofill grestore \n";
						p.print("n " + (j - 1) + " " + (i - 1) + " m " + j + " " + (i - 1) + " l " + j + " " + i + " l "
								+ (j - 1) + " " + i + " l " + (j - 1) + " " + (i - 1) + " l " + fillstr);
					}
				}
			}
		}

		// Draw the lines between the tiles
		p.println(betweenColor + " setrgbcolor\n");
		p.println(betweenWidth + " setlinewidth\n");
		for (int i = 1; i <= HEIGHT; i++) {
			for (int j = 1; j <= WIDTH; j++) {
				// Look right
				if (j < WIDTH && (tiled[i][j]) != (tiled[i][j + 1]))
					p.print("n " + j + " " + (i - 1) + " m " + j + " " + i + " l s\n");
				// look down
				if (i < HEIGHT && (tiled[i][j]) != (tiled[i + 1][j]))
					p.print("n " + (j - 1) + " " + i + " m " + j + " " + i + " l s\n");
			}
		}

		// Print the tiling boundaries
		p.println("0.00 0.00 0.00 setrgbcolor\n");
		p.println(betweenWidth + " setlinewidth\n");
		p.print("n 0 0 m " + WIDTH + " 0 l s\n");
		p.print("n 0 0 m 0 " + HEIGHT + " l s\n");
		p.print("n 0 " + HEIGHT + " m " + WIDTH + " " + HEIGHT + " l s\n");
		p.print("n " + WIDTH + " 0 m " + WIDTH + " " + HEIGHT + " l s\n");

		// Draw the chain graph edges
		p.println(chainWidth + " setlinewidth\n");
		p.println(chainColor + " setrgbcolor\n");
		p.println("1 setlinecap [.1 .2] 0 setdash");
		if (drawChains) {
			// Arrowhead code from https://staff.science.uva.nl/a.j.p.heck/Courses/Mastercourse2005/tutorial.pdf
			p.print("/arrowhead {\n" + "gsave\n" + "currentpoint   % s x1 y1 x0 y0\n"
					+ "4 2 roll exch  % s x0 y0 y1 x1\n" + "4 -1 roll exch % s y0 y1 x0 x1\n"
					+ "sub 3 1 roll   % s x1-x2 y0 y1\n" + "sub exch       % s y0-y1 x1-x2\n"
					+ "atan rotate    % rotate over arctan((y0-y1)/(x1-x2))\n" + "dup scale      % scale by factor s\n"
					+ "-7 2 rlineto 1 -2 rlineto -1 -2 rlineto\n" + "closepath fill  % fill arrowhead\n" + "grestore\n"
					+ "newpath\n" + "} def\n");
			for (int i = 1; i < HEIGHT; i += 2) {
				for (int j = 1; j <= WIDTH; j += 2) {
					// Overkill hashmap to count # of squares around a point
					HashMap<Integer, Integer> h = new HashMap<Integer, Integer>();
					for (int di = 0; di <= 1; di++) {
						for (int dj = 0; dj <= 1; dj++) {
							int t = tiled[i + di][j + dj];
							if (!h.containsKey(t))
								h.put(t, 0);
							h.put(t, h.get(t) + 1);
						}
					}
					Integer[] keys = h.keySet().toArray(new Integer[h.keySet().size()]);
					int most = h.get(keys[0]) == 3 ? keys[0] : keys[1];
					int tox = 0, toy = 0;
					for (int di = -1; di <= 2; di++) {
						for (int dj = -1; dj <= 2; dj++) {
							if (i + di < 1 || i + di > HEIGHT || j + dj < 1 || j + dj > WIDTH)
								continue;
							if ((di == 0 || di == 1) && (dj == 0 || dj == 1))
								continue;
							if (tiled[i + di][j + dj] == most) {
								tox = dj == -1 ? -2 : (dj == 2 ? 2 : 0);
								toy = di == -1 ? -2 : (di == 2 ? 2 : 0);
							}
						}
					}
					p.print("n " + j + " " + i + " m " + (j + tox) + " " + (i + toy) + " l s\n" + "n " + (j + tox) + " "
							+ (i + toy) + " m " + arrowheadWidth + " " + j + " " + i + " arrowhead\n");
				}
			}
		} // End of drawing chains


        // Postfix. Draw the thing on the page.
		p.println(" s");
		p.print("\nshowpage");
		p.close();
	}

	private static String drawBoardPic() {
		String pic = "";

		for (int i = 1; i <= HEIGHT; i++) {
			// Draw borders above tile row i
			pic = pic + "+";
			for (int j = 1; j <= WIDTH; j++) {
				if (i == 1 || tiled[i][j] != tiled[i - 1][j])
					pic = pic + "--";
				else
					pic = pic + "  ";
				pic = pic + "+";
			}
			pic = pic + "\n";

			// Draw borders between the tiles in row i
			pic = pic + "|  ";
			for (int j = 1; j < WIDTH; j++) {
				if (tiled[i][j] != tiled[i][j + 1])
					pic = pic + "|  ";
				else
					pic = pic + "   ";
			}
			pic = pic + "|\n";
		}

		// Draw borders below the bottom row
		pic = pic + "+";
		for (int j = 1; j <= WIDTH; j++) {
			pic = pic + "--+";
		}

		return pic;
	}
}
