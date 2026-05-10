import java.util.Objects;

/*Implementieren Sie eine Klasse Pair, die zwei Elemente eines beliebigen (generischen) Typs spei-
chern kann. Die beiden Elemente müssen denselben Typ besitzen, also Elemente derselben Klasse
sein. Sie sollen als private Variablen der Klasse Pair gespeichert werden. Der Zugriff geschieht über
sogenannte getter und setter Methoden, siehe API.
*/
// Die Klasse Pair ist eine 泛型 Klasse, die zwei Elemente eines beliebigen generischen Typs speichert
public class Pair<E> {
// TODO

    // 定义两个元素 first 和 second - E 是一个泛型
    // 这意味着它可以是任何类型
    // 例如 Integer, String, Double 等等
    // 这两个元素可以是相同的类型，也可以是不同的类型
    // 这取决于你在创建 Pair 对象时传入的类型
    // 也就是告诉Java将这个类的类型参数 E 替换为你想要的类型，但是我现在不先定义
    // private E first;表示这个类有一个私有变量 first，它的类型是 E
    // second 也是一样
    // 这两个变量是私有的，意味着它们只能在这个类的内部访问
    // 这是generics（泛型）的一个特性，能让一个类通用于任意类型
    // 属性（attribute）是类的一个重要组成部分
    // 它们是类的状态或数据
    // 在这个类中，我们有两个属性 first 和 second
    // 它们的类型是 E
    // E 是一个泛型类型参数
    // 泛型（generics）是 Java 中的一种特性
    // 允许我们在类、接口和方法中使用类型参数
    // 这使得我们可以编写更通用的代码

    private E first;
    private E second;

    // erzeugt ein paar mid den beiden Elementen first und second - 生成一对元素 first 和 second
    // 这个构造函数接受两个参数 first 和 second
    // 构造函数（constructor）是一个特殊的方法，用于创建类的对象
    // 在这个构造函数中，我们将传入的参数赋值给类的私有变量 first 和 second
    // 这意味着当我们创建一个 Pair 对象时，我们可以传入两个值
    // 这两个值将被存储在 Pair 对象的 first 和 second 变量中
    // 当我用new创建对象时，他会被自动调用，用来给对象的属性赋值  

    public Pair(E first, E second){
        this.first = first;
        this.second = second;
    }

    // copy constructor - 复制构造函数
    // 创建一个新对象，并复制一有对象的属性值
    // java 中没有内置的复制构造函数
    // 但是我们可以自己实现一个
    // 这个构造函数接受一个 Pair 对象作为参数
    // 然后将这个对象的 first 和 second 属性值复制到新创建的对象中
    // 这意味着我们可以创建一个新的 Pair 对象
    // 这个对象的属性值与另一个 Pair 对象的属性值相同
    // 这就是复制构造函数的作用

    public Pair(Pair<E> other){
        this.first = other.first;
        this.second = other.second;
        
    }

    // 这个方法的名称是 swap
    // swap 方法用于交换 first 和 second 的值

    public void swap(){
        E tempPair = first;
        first = second;
        second = tempPair;
    }

    // getter und setter Methoden - 获取和设置方法
    // getter 方法用于获取私有变量的值
    // setter 方法用于设置私有变量的值
    // 这两个方法是公共的
    // 这意味着它们可以在类的外部访问
    // 这两个方法的返回值类型是 E
    // 这意味着它们返回的值的类型是 E

    // 这两个方法的名称是 getFirst 和 setFirst
    // getFirst 方法用于获取 first 的值

    public E getFirst(){
        return first;
    }

    // setFirst 方法用于设置 first 的值

    public void setFirst(E first){
        this.first = first;
    }

    // 这两个方法的名称是 getSecond 和 setSecond
    // getSecond 方法用于获取 second 的值

    public E getSecond(){
        return second;
    }

    // setSecond 方法用于设置 second 的值

    public void setSecond(E second){
        this.second = second;
    }
    
    // 这两个方法的名称是 equals
    // equals 方法用于比较两个 Pair 对象是否相等
    // 这两个方法的名称是 hashCode
    // hashCode 方法用于计算 Pair 对象的哈希值


    @Override
    public boolean equals(Object o) {
        if (o == null || getClass() != o.getClass()) return false;
        Pair<?> pair = (Pair<?>) o;
        return Objects.equals(first, pair.first) && Objects.equals(second, pair.second);
    }

    @Override
    public int hashCode() {
        return Objects.hash(first, second);
    }

    // 这两个方法的名称是 toString
    // toString 方法用于将 Pair 对象转换为字符串


    @Override
    public String toString() {
        return "Pair<" + first +
                "," + second +
                '>';
    }

    // 这两个方法的名称是 main
    // main 方法是 Java 程序的入口点
    // 这两个方法的名称是 args
    // 这两个方法的名称是 System.out.println
    public static void main(String[] args) {
        Pair<Integer> pair1 = new Pair<>(1, 2);
        Pair<Integer> pair2 = new Pair<>(1, 2);
        System.out.println("Variable pair1 hat den Wert: " + pair1);
        System.out.println("Variable pair2 hat den Wert: " + pair2);
        System.out.println("Syntaktische Gleichheit von pair1 und pair2 ist: " + (pair1==pair2));
        System.out.println("Semantische Gleichheit von pair1 und pair2 ist: " + pair1.equals(pair2));
        Pair<Integer> pair1b = pair1;
        Pair<Integer> pair2b = new Pair<>(pair2);
        pair1.swap();
        pair2.setFirst(10);
        System.out.println("Nach swap() hat Variable pair1 den Wert: " + pair1);
        System.out.println("Nach setFirst(10) hat Variable pair2 den Wert: " + pair2);
        System.out.println("Die zuvor erstellte Kopie pair1b hat den Wert: " + pair1b);
        System.out.println("Die zuvor erstellte Kopie pair2b hat den Wert: " + pair2b);
        /*
        Die erwartete Ausgabe ist:
Variable pair1 hat den Wert: Pair<1, 2>
Variable pair2 hat den Wert: Pair<1, 2>
Syntaktische Gleichheit von pair1 und pair2 ist: false
Semantische Gleichheit von pair1 und pair2 ist: true
Nach swap() hat Variable pair1 den Wert: Pair<2, 1>
Nach setFirst(10) hat Variable pair2 den Wert: Pair<10, 2>
Die zuvor erstellte Kopie pair1b hat den Wert: Pair<2, 1>
Die zuvor erstellte Kopie pair2b hat den Wert: Pair<1, 2>
         */
    }
}

