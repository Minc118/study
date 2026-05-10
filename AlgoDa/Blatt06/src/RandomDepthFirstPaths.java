import java.util.*;

public class RandomDepthFirstPaths {
    private boolean[] marked; // marked[v] = is there an s-v path?
    private int[] edgeTo; // edgeTo[v] = last edge on s-v path
    private final int s; // source vertex

    /**
     * Computes a path between {@code s} and every other vertex in graph {@code G}.
     * 
     * @param G the graph
     * @param s the source vertex
     * @throws IllegalArgumentException unless {@code 0 <= s < V}
     */
    public RandomDepthFirstPaths(Graph G, int s) {
        this.s = s;
        edgeTo = new int[G.V()];
        marked = new boolean[G.V()]; // G.V() = number of vertices in G - 图G中的顶点数
        validateVertex(s);
    }

    public void randomDFS(Graph G) {
        randomDFS(G, s); // 从源节点s开始进行随机深度优先搜索
    }

    // depth first search from v
    //递归随机DFS
    private void randomDFS(Graph G, int v) {
        marked[v] = true; // 标记当前节点为已访问
        List<Integer> nbors = new ArrayList<>(G.adj(v)); // 获取邻接节点列表 - G.adj(v) 返回顶点v的邻接节点 - nbors 是一个列表，包含了所有与顶点v相连的顶点
        Collections.shuffle(nbors); // 打乱邻接节点的顺序 - collections.shuffle() 方法会随机打乱列表中的元素顺序
        for (int w : nbors) { // 遍历邻接节点 - w:nbors中的每个顶点
            if (!marked[w]) { // 如果邻接节点未被访问
                edgeTo[w] = v; // 设置前驱节点
                randomDFS(G, w); // 递归访问邻接节点
            }
        }
    }
    public void randomNonrecursiveDFS(Graph G) {
        // 非递归随机DFS
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(s); // 将源节点压入栈
        marked[s] = true; // 标记源节点为已访问

        while (!stack.isEmpty()) {
            int v = stack.peek(); // 获取栈顶节点

            //乱序领居列表
            List<Integer> nbors = new ArrayList<>(G.adj(v));
            Collections.shuffle(nbors); // 打乱邻接节点的顺序

            boolean Pushed = false; // 标记是否有节点被压入栈
            for (int w : nbors) {
                if (!marked[w]) { // 如果邻接节点未被访问
                    edgeTo[w] = v; // 设置前驱节点
                    marked[w] = true; // 标记邻接节点为已访问
                    stack.push(w); // 将邻接节点压入栈
                    Pushed = true; // 有节点被压入栈
                }
            }
            if (!Pushed) {
                // 如果没有节点被压入栈，说明当前节点的所有邻接节点都已访问
                // 可以在这里处理后序逻辑（如果需要）
                stack.pop(); // 继续处理下一个节点
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
     *         {@code v} and the source vertex {@code s}, as an Iterable
     * @throws IllegalArgumentException unless {@code 0 <= v < V}
     * 
     */
    public List<Integer> pathTo(int v) {
        // TODO

        validateVertex(v); // 验证顶点v是否有效
        if (!marked[v]) {
            return null; // 如果v未被访问，返回null
        }
        Deque<Integer> path = new LinkedList<>(); // 创建一个双端队列来存储路径
        for (int x = v; x != s; x = edgeTo[x]) {
            path.push(x); // 将当前节点x添加到路径的前端
        }
        path.push(s); // 将源节点s添加到路径的前端
        return new ArrayList<>(path); // 返回从s到v的路径
    }

    public int[] edge() {
        return edgeTo;
    }

    // throw an IllegalArgumentException unless {@code 0 <= v < V}
    private void validateVertex(int v) {
        int V = marked.length;
        if (v < 0 || v >= V)
            throw new IllegalArgumentException("vertex " + v + " is not between 0 and " + (V - 1));
    }

}
