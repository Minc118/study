
/******************************************************************************
 *  Compilation:  javac DepthFirstPaths.java
 *  Execution:    java DepthFirstPaths G s
 *  Dependencies: Graph.java
 ******************************************************************************/

/**
 *  The {@code DepthFirstPaths} class represents a data type for finding
 *  paths from a source vertex <em>s</em> to every other vertex
 *  in an undirected graph.
 *  <p>
 *  This implementation uses depth-first search.
 *  The constructor takes time proportional to <em>V</em> + <em>E</em>,
 *  where <em>V</em> is the number of vertices and <em>E</em> is the number of edges.
 *  Each call to {@link #hasPathTo(int)} takes constant time;
 *  each call to {@link #pathTo(int)} takes time proportional to the length
 *  of the path.
 *  It uses extra space (not including the graph) proportional to <em>V</em>.
 *  <p>
 *  For additional documentation, see <a href="https://algs4.cs.princeton.edu/41graph">Section 4.1</a>   
 *  of <i>Algorithms, 4th Edition</i> by Robert Sedgewick and Kevin Wayne.
 *
 *  @author Robert Sedgewick
 *  @author Kevin Wayne
 *  
 *  DISCLAIMER:
 *  These methods have been partly adjusted to fit the excersise.
 */
import java.util.*;

public class DepthFirstPaths {
    private boolean[] marked; // marked[v] = 已访问的顶点 - 标记顶点
    private int[] edgeTo; // edgeTo[v] = last adjacent node on s-v path - 前驱顶点
    private int[] distTo; // distTo[v] = number of edges s-v path - 源顶点到顶点v的距离
    private final int s; // source vertex - 源顶点
    private Queue<Integer> preorder; // vertices in preorder - 先序遍历的顶点
    private Queue<Integer> postorder; // vertices in postorder - 后序遍历的顶点

    /**
     * Computes a path between {@code s} and every other vertex in graph {@code G}.
     * 
     * @param G the graph
     * @param s the source vertex
     * @throws IllegalArgumentException unless {@code 0 <= s < V}
     */
    public DepthFirstPaths(Graph G, int s) {
        postorder = new LinkedList<Integer>(); // 初始化后序队列
        preorder = new LinkedList<Integer>();   // 初始化先序队列
        this.s = s; // 设置源顶点
        edgeTo = new int[G.V()]; // 初始化前驱数组
        marked = new boolean[G.V()]; // 初始化标记数组
        distTo = new int[G.V()]; // 初始化距离数组


        validateVertex(s); // 验证源顶点s是否合法
    }

    public void dfs(Graph G) {
        dfs(G, s);
    }

    // depth first search from v
    // 深度优先递归核心
    // 递归遍历图的每个节点
    private void dfs(Graph G, int v) {
        marked[v] = true;
        preorder.add(v); //记录先序 - 在访问节点时添加到队列
        for (int w : G.adj(v)) {        // 遍历邻接节点
            validateVertex(w); // 验证邻接节点w是否合法
            if (!marked[w]) {  // 如果w未被访问
                edgeTo[w] = v;   //设置前驱
                distTo[w] = distTo[v] + 1; //更新距离
                dfs(G, w);          // 递归访问邻接节点w
            }
        }
        postorder.add(v); //记录后序 - 在访问完所有邻接节点后添加到队列
    }


    //非递归深度优先搜索
    // 使用栈来模拟递归的行为
    // 非递归版dfs从源节点开始，使用栈来存储待访问的节点
    public void nonrecursiveDFS(Graph G) {
        // 初始化标记数组和其他变量
        marked = new boolean[G.V()];
        // to be able to iterate over each adjacency list, keeping track of which
        // vertex in each adjacency list needs to be explored next
        //为每个顶点准备领居迭代器
        Iterator<Integer>[] adj = (Iterator<Integer>[]) new Iterator[G.V()];  // 创建邻接节点迭代器数组
        for (int v = 0; v < G.V(); v++) // 初始化每个顶点的邻接节点迭代器
            adj[v] = G.adj(v).iterator(); // 获取顶点v的邻接节点迭代器 - adj[v] 是一个迭代器数组，每个元素对应图中一个顶点的邻接节点列表。

        // depth-first search using an explicit stack
        Stack<Integer> stack = new Stack<Integer>(); // 创建栈来存储待访问的节点
        stack.push(s); // 将源节点s压入栈
        marked[s] = true; // 标记源节点s为已访问
        distTo[s] = 0; // 距离 - 源节点到自身的距离为0
        preorder.add(s); // 记录先序 - 在访问节点时添加到队列
        while (!stack.isEmpty()) { // 当栈不为空时继续 - 栈中存储待访问的节点
            int v = stack.peek();  // 获取栈顶元素

            if (adj[v].hasNext()) { // 如果当前顶点v还有未访问的邻接节点
                int w = adj[v].next(); // 获取下一个邻接节点w
                if (!marked[w]) {        // 如果w未被访问
                    marked[w] = true;  // 标记w为已访问
                    edgeTo[w] = v; // 设置前驱
                    distTo[w] = distTo[v] + 1; // 更新距离
                    preorder.add(w); // 记录先序 - 在访问节点时添加到队列
                    stack.push(w);
                }
            }
            // 所有邻接节点都已访问
            else { // 如果没有节点被压入栈
                stack.pop();
                postorder.add(v); // 记录后序 - 在访问完所有邻接节点后添加到队列
            }

        }
    }

    /**
     * Is there a path between the source vertex {@code s} and vertex {@code v}?
     * 
     * @param v the vertex
     * @return {@code true} if there is a path, {@code false} otherwise
     * @throws IllegalArgumentException unless {@code 0 <= v < V}
     */
    public boolean hasPathTo(int v) {
        validateVertex(v);
        return marked[v];
    }

    /**
     * Returns a path between the vertex {@code v} and the source vertex {@code s},
     * or
     * {@code null} if no such path.
     * 
     * @param v the vertex
     * @return the sequence of vertices on a path between the vertex
     *         {@code v} and the source vertex {@code s}, as an Iterable (beginning
     *         and end are included)
     * @throws IllegalArgumentException unless {@code 0 <= v < V}
     * 
     */
    public List<Integer> pathTo(int v) {
        validateVertex(v); // 验证顶点v是否有效
        if (!marked[v]) {
            return null; // 如果v未被访问，返回null
        }

        List<Integer> listEnd = new ArrayList<>(); // 创建一个ArrayList来存储结果 - 为什么用ArrayList？因为它提供了动态数组的功能，能够方便地存储和访问路径中的节点。
        for (int x = v; x != s; x = edgeTo[x]) {
            listEnd.add(x); // 将当前节点x添加到路径的前端
        }

        listEnd.add(s); // 将源节点s添加到路径的前端
        
        return listEnd; // 返回从s到v的路径 - 将Deque转换为ArrayList以便于使用
    }

    /**
     * Returns the vertices in postorder. This method differs from the original.
     * 
     * @return the vertices in postorder, as a queue of vertices
     */
    public Queue<Integer> post() {
        return postorder;
    }

    /**
     * Returns the vertices in preorder. This method differs from the original.
     * 
     * @return the vertices in preorder, as a queue of vertices
     */
    public Queue<Integer> pre() {
        return preorder;
    }

    /**
     * Returns the class variable edgeTo. This method differs from the original.
     * 
     * @return egdeTo
     */
    public int[] edge() {
        return edgeTo;
    }

    /**
     * Returns the class variable distTo. This method differs from the original.
     * 
     * @return distTo
     */
    public int[] dist() {
        return distTo;
    }

    // throw an IllegalArgumentException unless {@code 0 <= v < V}
    private void validateVertex(int v) {
        int V = marked.length;
        if (v < 0 || v >= V)
            throw new IllegalArgumentException("vertex " + v + " is not between 0 and " + (V - 1));
    }
}
