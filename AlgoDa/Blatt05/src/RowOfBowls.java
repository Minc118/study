import java.util.ArrayList;
import java.util.List;

/**
 * This class implements a game of Row of Bowls.
 * For the games rules see Blatt05. The goal is to find an optimal strategy.
 */
public class RowOfBowls {

    public int[] v; // 弹珠数组 - 每个碗中的弹珠数量
    public int[][] bv; // 动态规划表 - bv[i][j]表示从i到j碗时先手玩家的最大得分
    public int n; // 碗的数量 - 长度
    public int[][] choosen; // 记录选择的碗 - chosen[i][j]表示从i到j碗时选择的碗的方向， 0表示左边碗，1表示右边碗
    //计算先手玩家在双方最优策略下的最大得分
    public RowOfBowls() {
    }
    
    /**
     * Implements an optimal game using dynamic programming
     * @param values array of the number of marbles in each bowl
     * @return number of game points that the first player gets, provided both parties play optimally
     */
    public int maxGain(int[] values) {
        this.n = values.length; // 碗的数量
        this.v = values; // 弹珠数组
        this.bv = new int[n][n]; // 动态规划表 - bv[i][j]表示从i到j碗时先手玩家的最大得分
        this.choosen = new int[n][n]; // 记录选择的碗 - chosen[i][j]表示从i到j碗时选择的碗的方向， 0表示左边碗，1表示右边碗

        // 区间bv，按照区间长度递增填表
        for (int len = 1; len <= n; len++) { // len是区间长度
            for (int i = 0; i <= n - len; i++) { // i是区间起点 - 左边界
                int j = i + len - 1; // j是区间终点 - 右边界
                if (i == j) { // 如果只有一个碗
                    bv[i][j] = v[i]; // 先手玩家只能取这个碗的弹珠数量
                    choosen[i][j] = 0; // 选择左边碗 - 只有一个碗时，左边碗就是这个碗
                } else {
                    // 取左或取右后的净得分
                    int leftGain = v[i] - bv[i + 1][j]; // 取左边碗的得分
                    int rightGain = v[j] - bv[i][j - 1]; // 取右边碗的得分
                    if (leftGain > rightGain) { // 如果取左边碗的得分更高
                        bv[i][j] = leftGain; // 更新最大得分
                        choosen[i][j] = 0; // 选择左边碗 - 0表示左边碗
                    } else {
                        bv[i][j] = rightGain; // 更新最大得分
                        choosen[i][j] = 1; // 选择右边碗 - 1表示右边碗
                    }
                }
            }
        }
        return bv[0][n - 1]; // 返回从0到n-1碗的最大得分
    }
    /**
     * Implements an optimal game recursively.
     *
     * @param values array of the number of marbles in each bowl
     * @return number of game points that the first player gets, provided both parties play optimally
     */
    public int maxGainRecursive(int[] values) {
        // TODO
        this.n = values.length; // 碗的数量
        this.v = values; // 弹珠数组
        return loesen(0, n-1); // 调用loesen方法计算最大得分
    }

    public int loesen(int li, int re){
        if ( li == re) { // 如果只有一个碗
            return v[li];
        } // 返回该碗的弹珠数量
        //取左或取右后的净得分
        int leftGain = v[li] - loesen(li + 1, re); // 取左边碗的得分
        int rightGain = v[re] - loesen(li, re - 1); // 取右边碗的得分
        return Math.max(leftGain, rightGain); // 返回两者中的最大值
    }

    
    /**
     * Calculates an optimal sequence of bowls using the partial solutions found in maxGain(int values)
     * @return optimal sequence of chosen bowls (represented by the index in the values array)
     */
    public Iterable<Integer> optimalSequence()
    {
        // TODO
        if (bv == null || choosen == null) {
            throw new IllegalStateException("maxGain must be called before optimalSequence");
        }

        List<Integer> sequence = new ArrayList<>(); // 创建一个列表来存储选择的碗的索引
        int i = 0; // 左边界
        int j = n - 1; // 右边界
        while (i <= j) {
            if (i == j) { // 如果只有一个碗
                sequence.add(i); // 添加这个碗的索引
                break; // 结束循环
            }
            if (choosen[i][j] == 0) {
                sequence.add(i); // 选择左边碗
                i++; // 更新左边界
            } else {
                sequence.add(j); // 选择右边碗
                j--; // 更新右边界
            }
        }
        return sequence;
    }


    public static void main(String[] args)
    {
        // For Testing
        RowOfBowls testgame = new RowOfBowls();
        int[] testValues = {4,7,3,2};
        System.out.println("Max Gain: " + testgame.maxGain(testValues));
        System.out.println("Optimal Sequence: " + testgame.optimalSequence());
        }
}

