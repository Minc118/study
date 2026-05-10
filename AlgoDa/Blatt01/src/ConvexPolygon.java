import java.util.Arrays;

/*
3.1 Konvexe Polygone (Klasse ConvexPolygon) (25 Punkte)
Die Klasse ConvexPolygon implementiert die von der Schnittstelle Shape geforderten Metho-
den. Das geometrische Objekt wird gemäß der Vorgabe aus der abstrakten Klasse Polygon durch
die Eckpunkte in einem Vector2D-Array dargestellt und in der entsprechenden Objektvaria-
ble vertices gespeichert. Es braucht nicht überprüft zu werden, ob die übergebenen Punkte
tatsächlich ein konvexes Polygon darstellen. Die Funktionen müssen außerdem nur unter der
Annahme funktionieren, dass die in vertices[] gegebenen Punkte umlaufend sind, also im
oder gegen den Uhrzeigersinn geordnet.
Die Methode totalArea() soll den aufsummierten Flächeninhalt aller übergebenen Polygone
zurückgeben. Zur Berechnung des Flächeninhalts empfiehlt sich eine Triangulierung, so dass
die Flächeninhalte der Dreiecke per Triangle.area() berechnet und addiert werden können.
Eine Art der Unterteilung in Dreiecke wird in Abbildung 2 gezeigt. Für Dreiecke wird area() in
der nächsten Teilaufgabe implementiert. Diese einfache Art der Triangulierung funktioniert nur
für konvexe Polygone. Wie oben beschrieben, brauchen Sie nicht zu überprüfen, ob das Polygon
wirklich konvex ist. */


public class ConvexPolygon extends Polygon {

    // convert vertices[] to a list of triangles
    // 设计理由 - 初始化多边形的顶点数据，构建几何图形
    // 通过三角形的顶点来表示三角形
    // 让ConvexPolygon继承vertices类
    // vertices用于储存所有顶点

    public ConvexPolygon(Vector2D[] vertices){
        this.vertices = vertices;  // Attribut 初始化
    }

    // 计算多边形的面积
    // 重写area()方法来计算多边形的面积
    // 多个多边形都能分解为 n-2个三角形
    // 计算每个三角形的面积并相加
    // 最后一个点为固定点

    @Override
    public double area(){
        double area = 0;
        Vector2D gesamtPunkt = vertices[vertices.length - 1];
        //设置一个固定点作为起始点，选择数组最后一个点 vertices.length ->在java中和c一样从0开始算位数吗？

        for(int i = 0; i < vertices.length - 2; i++){  //构造三角形通过不同的顶点 因为最后一个点是length -1 所有在i+1的情况下需要i-2
            Triangle triangleBuilding = new Triangle(gesamtPunkt, vertices[i], vertices[(i+1)]);
            area += triangleBuilding.area(); //把每个三角形的面积加到总面积中
        }
        return area;
    }

    //计算周长 - perimeter 的组成是由不同坐标两点之间的距离限制
    //所以要得出两点之间的距离，然后相加
    //但是我们又得注意到得从最后一条边回到第一条边
    //所以在代码中我们得加入判定条件

    @Override
    public double perimeter() {
        double perimeter = 0;
        for(int i = 0; i < vertices.length; i++){
            Vector2D first = vertices[i];
            Vector2D last;

            //判定是否超出长度
            if ( i +1 < vertices.length){
                last = vertices[i+1];
            } else {
                last = vertices[0];
            }

            //
            Vector2D vectorLength = new Vector2D(last.getX() - first.getX(), last.getY() - first.getY());
            double Length = vectorLength.length();  //计算公式来自Vector2D
            perimeter += Length;
        }
        return perimeter;
    }

    public static Polygon[] somePolygons() {
        Vector2D a = new Vector2D(0, 0);
        Vector2D b = new Vector2D(10, 0);
        Vector2D c = new Vector2D(5, 5);
        Vector2D e = new Vector2D(10, -5);
        Vector2D f = new Vector2D(12, 2);
        Vector2D g = new Vector2D(3, 17);

        Polygon Triangle = new ConvexPolygon(new Vector2D[]{a, b, c});
        Polygon Tetragon = new ConvexPolygon(new Vector2D[]{a, e, f, g});

        // 1. 生成单位五边形（radius=1）
        RegularPolygon Fuenfeck = new RegularPolygon(5, 1.0);

        // 生成单位六边形
        RegularPolygon Sechseck = new RegularPolygon(6, 1.0);

        return new Polygon[]{Triangle, Tetragon, Fuenfeck, Sechseck};
    }

    public static double totalArea(Polygon[] polygons){
        double totalArea = 0;
        for (Polygon polygon: polygons){
            totalArea += polygon.area();
        }
        return totalArea;
    }

    @Override
    public String toString() {
        return "ConvexPolygon(" + Arrays.toString(vertices) +
                ')';
    }
}


