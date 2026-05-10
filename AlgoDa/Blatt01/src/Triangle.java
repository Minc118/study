import java.util.Arrays;
/*Triangle类必须至少拥有以下两个构造函数：

public Triangle(Vector2D a, Vector2D b, Vector2D c) {
public Triangle(Triangle triangle)

第一个构造函数创建一个具有三个给定顶点的Triangle对象，第二个是一个复制构造函数。它创建一个Triangle对象，其顶点与传入的三角形（语法上）相同。

此外，需要重写area()方法，并返回三角形的面积。例如，可以使用海伦公式根据给定的顶点计算三角形的面积。提示：Vector2D实现了length()方法，并在main()方法中包含了您可以使用的海伦公式实现。

此外，请重写toString()方法。类似于对ConvexPolygon的要求（见3.1小节），它应该返回三角形的字符串表示。格式为Triangle{[vertex1, vertex2, vertex3]}，其中顶点（vertex1等）的格式为(x, y)。模板文件Triangle.java中的main方法包含一个预期输出的示例，例如：

Triangle{[(0.0, 0.0), (10.0, 0.0), (5.0, 5.0)]}
 */

public class Triangle extends ConvexPolygon {
    // constuctor with 3 point
    // 初始数组并且保存三个顶点
    //询问调用父类结构
    public Triangle(Vector2D a, Vector2D b, Vector2D c) {
        // 设置attribute
//        this.vertices= new Vector2D[]{a,b,c};
        super(new Vector2D[]{a, b, c});
    }

    //copy constructor
    //手动输入数值
    public Triangle(Triangle triangle) {  // triangle 是一个引用 reference 指向堆上的一个Triangle对象
        // 将对应的数值复制到copy constructor中
        super( new Vector2D[]{triangle.vertices[0],triangle.vertices[1],triangle.vertices[2]});
        //通过点操作符，我们访问该对象的字段vertices，他本身是一个Vector2D[]数组的引用
    }

    // formel von Heron: u = a + b + c
    //Flaecheninhalt A des Dreiecks: sqrt(u/2 * (u/2 - a)*(u/2 - b)*(u/2 - c))
    @Override
    public double area() {
        // from Vector2D file
        //use a,b,c 来代表3个顶点
        Vector2D a = vertices[0];
        Vector2D b = vertices[1];
        Vector2D c = vertices[2];

        Vector2D side1 = new Vector2D(b.getX() - a.getX(),b.getY() - a.getY());
        Vector2D side2 = new Vector2D(c.getX() - b.getX(),c.getY() - b.getY());
        Vector2D side3 = new Vector2D(a.getX() - c.getX(),a.getY() - c.getY());
        double s1 = side1.length();
        double s2 = side2.length();
        double s3 = side3.length();
        double s = (s1 + s2 + s3)/2;
        double area = Math.sqrt(s * (s - s1) * (s - s2) * (s - s3));

        return area;
    }

    @Override
    public String toString() {
        return "Triangle{" +
                "vertices=" + Arrays.toString(vertices) +
                '}';
    }

    public static void main(String[] args) {
        Vector2D a = new Vector2D(0, 0);
        Vector2D b = new Vector2D(10, 0);
        Vector2D c =  new Vector2D(5, 5);
        Triangle triangle = new Triangle(a, b, c);
        double area = triangle.area();
        System.out.printf("Die Fläche des Dreiecks 'triangle' {%s, %s, %s} beträgt %.1f LE^2.\n", a, b, c, area);

        Triangle triangle2 = new Triangle(triangle);
        System.out.println("triangle2 ist eine Kopie per Copy-Konstruktor von 'triangle': " + triangle2);
        a.setX(-5);
        System.out.println("Eckpunkt 'a', der zur Definition von 'triangle' verwendet wurde, wird geändert.");
        System.out.println("Nun ist der Wert von 'triangle2': " + triangle2);
        /*
        Die erwartete Ausgabe ist:
Die Fläche des Dreiecks 'triangle' {(0.0, 0.0), (10.0, 0.0), (5.0, 5.0)} beträgt 25,0 LE^2.
triangle2 ist eine Kopie per Copy-Konstruktor von 'triangle': Triangle{[(0.0, 0.0), (10.0, 0.0), (5.0, 5.0)]}
Eckpunkt 'a', der zur Definition von 'triangle' verwendet wurde, wird geändert.
Nun ist der Wert von 'triangle2': Triangle{[(-5.0, 0.0), (10.0, 0.0), (5.0, 5.0)]}
         */
    }
}

