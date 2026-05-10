import java.util.Iterator;
import java.util.List;

/**
 * Class that represents a maze with N*N junctions.
 * 
 * @author Vera Röhr
 */
public class Maze{
    private final int N;
    private Graph M;    //Maze
    public int startnode;
        
	public Maze(int N, int startnode) {
		
        if (N < 0) throw new IllegalArgumentException("Number of vertices in a row must be nonnegative");
        this.N = N;
        this.M= new Graph(N*N);
        this.startnode= startnode;
        buildMaze();
	}
	
    public Maze (In in) {
    	this.M = new Graph(in);
    	this.N= (int) Math.sqrt(M.V());
    	this.startnode=0;
    }

	
    /**
     * Adds the undirected edge v-w to the graph M.
     *
     * @param  v one vertex in the edge
     * @param  w the other vertex in the edge
     * @throws IllegalArgumentException unless both {@code 0 <= v < V} and {@code 0 <= w < V}
     */

    //检测M中是否已有v-w边：自环视为已存在
    public void addEdge(int v, int w) {
        testVertex(v); // 检查顶点v是否合法
        testVertex(w); // 检查顶点w是否合法

        M.addEdge(v, w); // 添加无向边v-w到图M
    }

    // 检查顶点v是否在合法范围内
    public void  testVertex(int v){
        if (v < 0 || v >= N * N) {
            throw new IllegalArgumentException("Vertex " + v + " is not between 0 and " + (N * N - 1));
        }
    }
    /**
     * Returns true if there is an edge between 'v' and 'w'
     * @param v one vertex
     * @param w another vertex
     * @return true or false
     */
    //检测M中是否已有v-w边：自环视为已存在
    public boolean hasEdge( int v, int w){
        testVertex(v); // 检查顶点v是否合法
        testVertex(w); // 检查顶点w是否合法

        if (v == w) {
            return true; // 自环视为已存在
        }
        Iterator<Integer> it = M.adj(v).iterator(); // 获取v的邻接节点迭代器
        while (it.hasNext()) { // 遍历邻接节点
            int neighb = it.next();
            if (neighb == w) {
                return true; // 找到邻接节点w
            }
        }
        return false;
    }	
    
    /**
     * Builds a grid as a graph.
     * @return Graph G -- Basic grid on which the Maze is built
     */
    public Graph mazegrid() {
        Graph G = new Graph(N * N); // 创建一个N*N的图
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                int v = i * N + j; // 计算顶点编号

                if (i < N - 1) { // 下方邻接
                    G.addEdge(v, (i + 1) * N + j);//因为下方邻接的顶点编号为(i + 1) * N + j
                }

                if (j < N - 1) { // 右侧邻接
                    G.addEdge(v, i * N + (j + 1)); // 右侧邻接的顶点编号为i * N + (j + 1)
                }
            }
        }
        return G;
    }
    
    /**
     * Builds a random maze as a graph.
     * The maze is build with a randomized DFS as the Graph M.
     */
    private void buildMaze() {
		//
        Graph G = mazegrid(); // 获取基础网格图
        RandomDepthFirstPaths dfs = new RandomDepthFirstPaths(G, startnode); // 使用随机深度优先搜索
        dfs.randomNonrecursiveDFS(G); // 执行随机非递归深度优先搜索 - 生成随机迷宫

       int[] ePar = dfs.edge(); // 获取前驱数组 - 每个顶点的前驱节点
       for (int i = 0; i < N * N; i++) { // 遍历所有顶点
            if ( i == startnode) continue; // 跳过起始节点
           int v = ePar[i]; // v是顶点i的前驱节点 - 父节点
           addEdge(v, i); // 添加边v-i到图M
       }
    }

    /**
     * Find a path from node v to w
     * @param v start node
     * @param w end node
     * @return List<Integer> -- a list of nodes on the path from v to w (both included) in the right order.
     */
    public List<Integer> findWay(int v, int w){
        DepthFirstPaths dfs = new DepthFirstPaths(M, v); // 使用深度优先搜索从v开始
        if (!dfs.hasPathTo(w)) { // 检查是否存在从v到w的路径
            return null; // 如果没有路径，返回null
        }
        return dfs.pathTo(w); // 返回从v到w的路径
    }
    
    /**
     * @return Graph M
     */
    public Graph M() {
    	return M;
    }

    public static void main(String[] args) {
		// FOR TESTING
    }


}

