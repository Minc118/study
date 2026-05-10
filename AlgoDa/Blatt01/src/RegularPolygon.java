import java.util.Arrays;
import java.util.Vector;

// Diese Klasse implementiert nur *zentrierte* reguläre Polygone, also mit midpoint = (0, 0).
/*
正多边形（RegularPolygon类）（20分）
RegularPolygon类表示正多边形，其中心位于原点（0,0），其顶点位于以外接圆半径radius（从中心到每个顶点的距离）为半径的圆上。它由顶点数N和外接圆半径radius唯一确定。请实现相应的构造函数以及复制构造函数
public RegularPolygon(int N, double radius)
public RegularPolygon(RegularPolygon polygon)
以及方法
public void resize(double newradius)
该方法允许更改对象半径。请记住，这还需要相应地更改继承变量vertices中的顶点。
计算顶点坐标可以使用单位圆进行计算。
首先，需要计算从原点出发各点之间的角度，这等于360°/#顶点数。将此角度用于每个顶点的正弦和余弦计算，可以得到半径为1时的坐标。这是可行的，因为从原点到一个顶点的线段构成一个直角三角形的斜边。然后，需要将坐标与给定的半径进行缩放。
 */
public class RegularPolygon extends ConvexPolygon {

    // TODO
    private int N;
    private double radius;

    public RegularPolygon(int N, double radius) {

        super(new Vector2D[N]); // 调用父集构造器，给this.vertices分配长度为N的空数组

        //初始化自身字段
        this.N = N;
        this.radius = radius;

        //内联生成并填充顶点（与“你的方法”一致）
        //每个顶点的弧度增加
        double winkelsize = 2 * Math.PI / N;

        for (int i = 0; i < N; i++){
            double currentwinkel = i * winkelsize;  // 当前的角度
            double cos = Math.cos(currentwinkel);
            double sin = Math.sin(currentwinkel);
            double x = radius * cos;    //Trigonometrische Funktion
            double y = radius * sin;
            vertices[i] = new Vector2D(x, y);
        }

    }
    public RegularPolygon(RegularPolygon polygon) {

        super(new Vector2D[polygon.N]);

        this.N = polygon.N;
        this.radius = polygon.radius;

        double winkelsize = 2 * Math.PI / N;

        for (int i = 0; i < polygon.N; i++){
            double currentwinkel = i * winkelsize;  // 当前的角度
            double cos = Math.cos(currentwinkel);
            double sin = Math.sin(currentwinkel);
            double x = polygon.radius * cos;    //Trigonometrische Funktion
            double y = polygon.radius * sin;
            vertices[i] = new Vector2D(x, y);
        }

    }

    public void resize(double newradius) {
        // TODO
        this.radius = newradius;

        double winkelsize = 2 * Math.PI / N;
        for (int i = 0; i < N; i++){
            double currentwinkel = i * winkelsize;  // 当前的角度
            double cos = Math.cos(currentwinkel);
            double sin = Math.sin(currentwinkel);
            double x = newradius * cos;    //Trigonometrische Funktion
            double y = newradius * sin;
            vertices[i] = new Vector2D(x, y);
        }
    }

    @Override
    public String toString() {
        return "RegularPolygon{" +
                "N=" + N +
                ", radius=" + radius +
                '}';
    }

    public static void main(String[] args) {
        RegularPolygon pentagon = new RegularPolygon(5, 1);
        System.out.println("Der Flächeninhalt des " + pentagon + " beträgt " + pentagon.area() + " LE^2.");
//        RegularPolygon otherpentagon = pentagon;      // Dies funktioniert nicht!
        RegularPolygon otherpentagon = new RegularPolygon(pentagon);
        pentagon.resize(10);
        System.out.println("Nach Vergrößerung: " + pentagon + " mit Fläche " + pentagon.area() + " LE^2.");
        System.out.println("Die Kopie: " + otherpentagon + " mit Fläche " + otherpentagon.area() + " LE^2.");
        /*
        Die erwartete Ausgabe ist:
Der Flächeninhalt des RegularPolygon{N=5, radius=1.0} beträgt 2.377641290737883 LE^2.
Nach Vergrößerung: RegularPolygon{N=5, radius=10.0} mit Fläche 237.7641290737884 LE^2.
Die Kopie: RegularPolygon{N=5, radius=1.0} mit Fläche 2.377641290737883 LE^2.
         */
    }
}
