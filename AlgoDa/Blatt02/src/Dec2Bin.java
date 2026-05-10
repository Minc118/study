import java.util.Stack;
/*任务3：十进制转换为二进制（家庭作业）

设N为一个自然数，以十进制表示。该数的二进制表示可以通过从最低位到最高位迭代地确定：

• 二进制表示中的最低位是N % 2（N除以2的余数）。
• 然后N除以2（整数除法，无余数），并对结果重复此过程，直到N=0。

为了以正确的顺序输出数字，您可以将它们存储在栈中。请按照此方法实现以下两种方法。

3.1 实现convert()方法（15分）

在Dec2Bin类中实现public void convert(int N)方法。它应该将传入的数N存储在对象变量N中，并将其转换为二进制表示。二进制表示应存储在对象变量binStack中，以便最高有效位可以通过栈的第一个pop()获得。请注意，在正确存储二进制表示之前，栈必须处于什么状态！

3.2 实现toString()方法（15分）

在Dec2Bin类中实现方法public String toString()。它应该以通常的方式返回存储的二进制表示形式的字符串，例如，对于输入数字50，返回110010。调用toString()不应该删除栈中的内容。

提示：

• 可以假设输入≥0。
• convert()方法可以用少于10行代码实现，无需递归。
• toString()方法必须将对象变量binStack转换为字符串，并且不得使用对象变量N。在测试中，binStack会被修改（不调用convert()），然后测试toString()。*/
/** * A class for constructing a Decimal-to-Binary Number- Converter; * contains a main method for demonstration. */
public class Dec2Bin {
    //binStack用于保存二进制表示 <Integer>格式
    public Stack<Integer> binStack;  // We make it public to modify it in our tests.
    private int N;  //储存十进制输入数字

    /**
     * Constructor of an empty object. Use method {@code convert()} to convert a number.
     */
    public Dec2Bin() {
        binStack = new Stack<>();
    }

    /**
     * Returns the number that is converted as {@code int}.
     *
     * @return the converted number
     */
    public int getN() {
        return N;
    }

    /**
     * Converts the given number into binary format, with each digit being represented in a
     * stack of {@code int}.
     *
     * @param N the number that is to be converted.
     */
    public void convert(int N) {
        // TODO implement this method
        this.N = N;
        binStack.clear(); // free the old information
        binStack.size();
        System.out.println("Nsize = " + binStack.size() );
        //遍历N

        if (N == 0) {
            binStack.push(0);  // 存入0: 特殊情况：0的二进制就是0
            System.out.println("N = 0");
            return;
        }

        while (N > 0) {
            binStack.push(N % 2); // 存入当前位
            N = N / 2; //减少原始数据
            System.out.println("N = " + N);
        }
    }


    /**
     * Returns the digits that are stored in {@code binStack} as a string. To is the binary format of the
     * converted number.
     * For testing purpose, we require that the function works also, if the variable {@code binStack} is
     * modified externally.
     *
     * @return a string representation of the number in binary format.
     */

    // 因为Stack的数据结构为LIFO，所以需要将二进制的数字提取出来然后再发送出来
    @Override
    public String toString() {
        // 警告：Stack.toString() 不会保留堆栈顺序。请勿使用它。
        // TODO implement this method
        Stack<Integer> Stack2 = new Stack<>(); // 创建一个备用stack,用于保存弹出的数据，以便后面恢复 binStack
        StringBuilder builder = new StringBuilder();

        while (!binStack.isEmpty()) {
            Stack2.push(binStack.pop());  //将binStack的值加入零时数组Stack2
        }

        while (!Stack2.isEmpty()){
            binStack.push(Stack2.peek()); //将Stack2的值送回binStack
            System.out.println("binStack size = " + binStack.size());
            builder.append(Stack2.pop());   //将Stack2的值组成string
        }
        System.out.println("binStack size = " + binStack.size());
        System.out.println("binStack = " + binStack);
        return builder.reverse().toString(); //因为LIFO所以在我再次将Stack2的值送回binStack时，数据的储存顺序是对的，但是提取时因为Stack的LIFO所以出来的数字顺序回事反着的
    }

    public static void main(String[] args) {
        Dec2Bin dec2bin = new Dec2Bin();
        dec2bin.convert(50);
        System.out.println("Die Zahl " + dec2bin.getN() + " in Binärdarstellung: " + dec2bin);
        // Do it another time to demonstrate that toString does not erase the binStack.
        System.out.println("Die Zahl " + dec2bin.getN() + " in Binärdarstellung: " + dec2bin);
    }
}

