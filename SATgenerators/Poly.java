public class Poly{
    public int l;
    public int w;
    public int offset;            // offset of first used square in top row
    public boolean b[];
    int numRots;
    boolean flip;
    public Poly[] shapes;
    public int numShapes;
    private static int depthCounter = 0;    // To tell if this class calls its own const.

    public Poly(int l, int w, boolean[] b, int n, boolean f) {
        super();
        this.l = l;
        this.w = w;
        this.b = b;
        this.numRots = n;
        this.flip = f;
        this.numShapes = numRots * (f ? 2 : 1);
        findOffsets();
        depthCounter++;
        if(depthCounter == 1){
            this.shapes = new Poly[numRots * numShapes];
            buildShapes();
        }
        depthCounter--;
    }

    private void buildShapes(){
        int f = (flip ? 2 : 1);
        int c = 0;      // counter
        boolean[] btemp;

        //System.out.println("New Poly");
        for(int i = 1; i <= f; i++){
            for(int j = 0; j < numRots; j++){
                // printout(l, w, b);
                shapes[c] = new Poly(l, w, b, numRots, flip);
                int temp = l;
                l = w;
                w = temp;
                btemp = new boolean[l*w];
                for(int x = 0; x < w; x++)    // rotate 90 degrees cc
                    for(int y = 0; y < l; y++)
                        btemp[l*x+y] = b[w*(l-y-1)+x];
                b = btemp;
                c++;
            }
            btemp = new boolean[l*w];
            for(int x = 0; x < w; x++)    // flip over vertical line
                for(int y = 0; y < l; y++)
                    btemp[l*x+y] = b[l*(w-x-1) + y];
            b = btemp;
        }
    }

    private void printout(int l, int w, boolean[] b){
        for(int i = 0; i < l; i++){
            for(int j = 0; j < w; j++){
                System.out.print(b[j*l+i] ? "*" : " ");
            }
            System.out.print("\n");
        }
        System.out.print("\n");
        System.out.print("\n");
    }

    private void findOffsets(){
        for(int j = 0; j < w; j++)
            if(b[j*l]){
                this.offset = j;
                return;
            }
    }
}
