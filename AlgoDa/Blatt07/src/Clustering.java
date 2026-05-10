import java.util.*;
import java.awt.Color;

/**
 * This class solves a clustering problem with the Prim algorithm.
 */
public class Clustering {
	EdgeWeightedGraph G;
	List <List<Integer>>clusters; 
	List <List<Integer>>labeled; 
	
	/**
	 * Constructor for the Clustering class, for a given EdgeWeightedGraph and no labels.
	 * @param G a given graph representing a clustering problem
	 */
	public Clustering(EdgeWeightedGraph G) {
            this.G=G;
	    clusters= new LinkedList <List<Integer>>();
	}
	
    /**
	 * Constructor for the Clustering class, for a given data set with labels
	 * @param in input file for a clustering data set with labels
	 */
	public Clustering(In in) {
            int V = in.readInt();
            int dim= in.readInt();
            G= new EdgeWeightedGraph(V);
            labeled=new LinkedList <List<Integer>>();
            LinkedList labels= new LinkedList();
            double[][] coord = new double [V][dim];
            for (int v = 0;v<V; v++ ) {
                for(int j=0; j<dim; j++) {
                	coord[v][j]=in.readDouble();
                }
                String label= in.readString();
                    if(labels.contains(label)) {
                    	labeled.get(labels.indexOf(label)).add(v);
                    }
                    else {
                    	labels.add(label);
                    	List <Integer> l= new LinkedList <Integer>();
                    	labeled.add(l);
                    	labeled.get(labels.indexOf(label)).add(v);
                    	System.out.println(label);
                    }                
            }
             
            G.setCoordinates(coord);
            for (int w = 0; w < V; w++) {
                for (int v = 0;v<V; v++ ) {
                	if(v!=w) {
                	double weight=0;
                    for(int j=0; j<dim; j++) {
                    	weight= weight+Math.pow(G.getCoordinates()[v][j]-G.getCoordinates()[w][j],2);
                    }
                    weight=Math.sqrt(weight);
                    Edge e = new Edge(v, w, weight);
                    G.addEdge(e);
                	}
                }
            }
	    clusters= new LinkedList <List<Integer>>();
	}
	
    /**
	 * This method finds a specified number of clusters based on a MST.
	 *
	 * It is based in the idea that removing edges from a MST will create a
	 * partition into several connected components, which are the clusters.
	 * @param numberOfClusters number of expected clusters
	 */
	public void findClusters(int numberOfClusters){
		// numebr of clusters期望聚类个数k - 1<= k <= V - 1
		if (numberOfClusters < 1) { //如果期望聚类个数小于1，则抛出异常
			throw new IllegalArgumentException("Number of clusters must be at least 1");
		}
		// 构造最小生成树 - PrimMST是一个类，用来计算最小生成树
		PrimMST primMST = new PrimMST(G); // new PrimMST(G)是调用PrimMST类的构造函数，传入图G作为参数 - new是用来创建一个新的对象

		//将最小生成树的边存储在一个列表中，避免类型转换问题
		List<Edge>  mstEdges = new ArrayList<Edge>(); // 创建一个新的ArrayList对象mstEdges，用来存储最小生成树的边
		for (Edge e : primMST.edges()) { //遍历最小生成树的边
			mstEdges.add(e); //将每条边添加到mstEdges列表中
		}

		//先按自然顺序升序排列，再反转得到降序排列
		Collections.sort(mstEdges); //collections是一个工具类，提供了对集合的操作方法 - sort是一个静态方法，用来对集合进行排序
		Collections.reverse(mstEdges); //reverse是一个静态方法，用来反转集合的顺序
		//删除最大的（numberOfClusters-1）条边：
		int schnitt  = Math.min(numberOfClusters - 1, mstEdges.size()); //计算要删除的边数，取期望聚类个数减1和最小生成树边数减1的最小值
		for (int i = 0; i < schnitt; i++) { //循环删除最大的（numberOfClusters-1）条边
			mstEdges.remove(0); //从mstEdges列表中删除第一个元素，即最大的边
		}

		//将剩余的边分成若干个连通分量，作为聚类结果
		UF uf = new UF(G.V()); //创建一个新的并查集对象uf，用来存储连通分量
		for (Edge e : mstEdges) { //遍历剩余的边
			uf.union(e.either(), e.other(e.either())); //将边的两个顶点所在的连通分量合并

		}

		//将每个连通分量作为一个聚类结果存储在clusters列表中
		List<List<Integer>> B = new ArrayList<>(G.V()); //创建一个新的列表B，用来存储每个连通分量
		for (int i = 0; i < G.V(); i++) { //初始化B列表的每个元素为一个空列表

			B.add(new ArrayList<Integer>()); //添加一个新的空列表到B列表中,为了存储每个连通分量的顶点
		}

		for (int i = 0; i < G.V(); i++) { //遍历图的每个顶点
			int root = uf.find(i); //找到顶点i所在的连通分量的根节点
			B.get(root).add(i); //将顶点i添加到对应的连通分量列表中，为了存储每个连通分量的顶点
		}


		clusters.clear(); //清空clusters列表，以便存储新的聚类结果
		for (List<Integer> bucket : B) {
				if (bucket.isEmpty() == false) { //如果连通分量不为空
					clusters.add(bucket); //将连通分量添加到clusters列表中
				}
		}

	}
	
	/**
	 * This method finds clusters based on a MST and a threshold for the coefficient of variation.
	 *
	 * It is based in the idea that removing edges from a MST will create a
	 * partition into several connected components, which are the clusters.
	 * The edges are removed based on the threshold given. For further explanation see the exercise sheet.
	 *
	 * @param threshold for the coefficient of variation
	 */
	public void findClusters(double threshold){
		// TODO
	}
	
	/**
	 * Evaluates the clustering based on a fixed number of clusters.
	 * @return array of the number of the correctly classified data points per cluster
	 */
	public int[] validation() {
		// TODO
	}
	
	/**
	 * Calculates the coefficient of variation.
	 * For the formula see exercise sheet.
	 * @param part list of edges
	 * @return coefficient of variation
	 */
	public double coefficientOfVariation(List <Edge> part) {
		// TODO
	}
	
	/**
	 * Plots clusters in a two-dimensional space.
	 */
	public void plotClusters() {
		int canvas=800;
	    StdDraw.setCanvasSize(canvas, canvas);
	    StdDraw.setXscale(0, 15);
	    StdDraw.setYscale(0, 15);
	    StdDraw.clear(new Color(0,0,0));
		Color[] colors= {new Color(255, 255, 255), new Color(128, 0, 0), new Color(128, 128, 128), 
				new Color(0, 108, 173), new Color(45, 139, 48), new Color(226, 126, 38), new Color(132, 67, 172)};
	    int color=0;
		for(List <Integer> cluster: clusters) {
			if(color>colors.length-1) color=0;
		    StdDraw.setPenColor(colors[color]);
		    StdDraw.setPenRadius(0.02);
		    for(int i: cluster) {
		    	StdDraw.point(G.getCoordinates()[i][0], G.getCoordinates()[i][1]);
		    }
		    color++;
	    }
	    StdDraw.show();
	}
	

    public static void main(String[] args) {
		// FOR TESTING
    }
}

