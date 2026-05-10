import java.sql.ClientInfoStatus;
import java.util.InputMismatchException;
import java.util.Stack;

import static java.lang.Math.abs;
/**
 * This class represents a generic TicTacToe game board.
 */
public class Board {
    private int n;
    private int[][] playground;  //储存棋牌状态的二维数组， -1 玩家1,0 空格,1 玩家2
    private int freeBoard; // 记录空格的数量
    public int lastPlayer; // 记录最后一个落子的玩家
    public Position lastMove; // 记录最后一个落子的位置

    /**
     *  Creates Board object, am game board of size n * n with 1<=n<=10.
     */
    public Board(int n)
    {
        if (n < 1 || n > 10) {
            throw new InputMismatchException("ein Spielbrett der Größe muss n * n für 1 ≤ n ≤10 sein");
        }
        this.n = n; // 设置棋盘的大小
        this.playground = new int[n][n]; // 初始化棋盘为n*n的二维数组 - 所有位置初始为0
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                playground[i][j] = 0; // 初始化棋盘所有位置为0 - 空格
            }
        }
        this.freeBoard = n * n; // 初始化空格数量为n*n - 所有位置初始为空格

    }
    
    /**
     *  @return     length/width of the Board object
     */
    // 获取棋盘的大小
    public int getN() { return n; }
    // 获取棋盘的大小
    /**
     *  @return     number of currently free fields
     */
    // 获取当前空格的数量
    public int nFreeFields() {
        return freeBoard; // 返回空格的数量

    }
    
    /**
     *  @return     token at position pos
     *  *  @throws     InputMismatchException 如果 pos 不在棋盘范围内
     */
    public int getField(Position pos) throws InputMismatchException
    {
        int row = pos.x; // 获取位置的行坐标
        int col = pos.y; // 获取位置的列坐标
        // 检查位置是否在棋盘范围内
        if (row < 0 || row >= n || col < 0 || col >= n) {
            throw new InputMismatchException("Position " + pos + " is out of bounds.");
        }
        return playground[row][col]; // 返回该位置的棋子状态
    }

    /**
     *  Sets the specified token at Position pos.
     *  value 只能是 -1， 0 ，1。 同时会自动维护freeBoard的值。
     */    
    public void setField(Position pos, int token) throws InputMismatchException
    {
        int row = pos.x; // 获取位置的行坐标
        int col = pos.y; // 获取位置的列坐标
        // 检查位置是否在棋盘范围内
        if (row < 0 || row >= n || col < 0 || col >= n) {
            throw new InputMismatchException("Position " + pos + " is out of bounds.");
        }
        // 检查token的值是否有效
        if (token != -1 && token != 0 && token != 1) {
            throw new InputMismatchException("Token must be -1, 0, or 1.");
        }
        // 检查该位置是否已经有棋子
        // 如果原来是空格，则freeBoard减1
        // 如果原来是玩家1或玩家2的棋子，则freeBoard++
        if (playground[row][col] == 0 && token != 0) {
            freeBoard--; // 如果原来是空格，则空格数量减1
        }
        // 如果原来不是空，而且放进去的 token 与原来的值不同，说明格子是从一个玩家的棋子被“改写”/撤销，
        // 那 freeBoard++。
        // **但注意**：在你的业务逻辑里，doMove() 里会先检查该格是空的再落子，undoMove() 会用 setField(pos,0) 清空，
        // 所以这一段“else if”只在“undoMove”时才会触发（原来非 0，现在写 0）。

        else if (playground[row][col] != 0 && token == 0) {
            freeBoard++; // 如果原来是玩家1或玩家2的棋子，则空格数量加1
        }
        // 设置该位置的棋子
        playground[row][col] = token; // 设置该位置的棋子状态
    }
    
    /**
     *  Places the token of a player at Position pos.
     *  doMove 表示“真正意义上的落子”， 只有当该格子是空格时才允许落子；否则抛异常。
     *  player 的值只能是 -1 或 1，分别表示玩家1和玩家2。
     *  如果落子成功，则更新 lastMove 和 lastPlayer 的值。
     *  调用 setField 方法来设置棋盘状态。
     *  如果 pos 不在棋盘范围内，或者 player 的值不合法，则抛出 InputMismatchException 异常。
     */
    public void doMove(Position pos, int player)
    {
        int row = pos.x; // 获取位置的行坐标
        int col = pos.y; // 获取位置的列坐标
        //检查player的合法性
        if (player != -1 && player != 1) {
            throw new InputMismatchException("Player must be -1 or 1.");
        }
        // 检查位置是否在棋盘范围内
        if (row < 0 || row >= n || col < 0 || col >= n) {
            throw new InputMismatchException("Position " + pos + " is out of bounds.");
        }
        // 检查该位置是否已经有棋子 - board[row][col] == 0
        if (playground[row][col] != 0) {
            throw new InputMismatchException("Position " + pos + " is already occupied.");
        }
        // 设置该位置的棋子- 调用 setField 方法
        setField(pos, player); // 设置该位置的棋子状态
        // 更新 lastMove 和 lastPlayer 的值
        lastPlayer = player; // 更新最后一个落子的玩家
        lastMove = pos; // 更新最后一个落子的位置
    }

    /**
     *  Clears board at Position pos.
     *  undoMove 表示“撤销落子”， 只有当该格子是玩家1或玩家2的棋子时才允许撤销；否则抛异常。
     *  如果 pos 不在棋盘范围内，或者该位置没有玩家的棋子，则抛出 InputMismatchException 异常。
     *  如果撤销成功，则更新 lastMove 和 lastPlayer 的值。
     *  如果该位置原来是空格，则 freeBoard 的值不变；如果该位置原来是玩家1或玩家2的棋子，则 freeBoard 的值加1。
     */
    public void undoMove(Position pos)
    {
        int row = pos.x; // 获取位置的行坐标
        int col = pos.y; // 获取位置的列坐标
        // 检查位置是否在棋盘范围内
        if (row < 0 || row >= n || col < 0 || col >= n) {
            throw new InputMismatchException("Position " + pos + " is out of bounds.");
        }
        // 检查该位置是否有玩家的棋子
        if (playground[row][col] == 0) {
            throw new InputMismatchException("Position " + pos + " is already empty.");
        }
        // 直接调用 setField 方法来清除该位置的棋子
        setField( pos, 0);
    }
    
    /**
     *  @return     true if game is won, false if not
     *  判断当前棋盘是否有人获胜，即是否有玩家在一行、一列或对角线上连续放置了 n 个相同的棋子。
     *  若最后一次doMove的玩家获胜，则返回true；否则返回false。
     *  也可以按题意，只要有任意一条连线满足条件就认为游戏获胜。，直接返回true。
     */
    public boolean isGameWon(){
        //如果没落子，直接就返回false
        if (lastMove == null) {
            return false; // 如果没有落子，游戏未获胜
        }
        int player = lastPlayer; // 获取最后一个落子的玩家
        int row = lastMove.x; // 获取最后一个落子的位置的行坐标
        int col = lastMove.y; // 获取最后一个落子的位置的列坐标

        // 检查行
        for (int j = 0; j < n; j++) {
            if (playground[row][j] != player) {
                break; // 如果当前行有不等于玩家的棋子，跳出循环
            }
            if (j == n - 1) {
                return true; // 如果遍历到最后一个位置，表示该行获胜
            }
        }

        // 检查列
        for (int i = 0; i < n; i++) {
            if (playground[i][col] != player) {
                break; // 如果当前列有不等于玩家的棋子，跳出循环
            }
            if (i == n - 1) {
                return true; // 如果遍历到最后一个位置，表示该列获胜
            }
        }

        // 检查主对角线
        if (row == col) { // 如果最后一个落子在主对角线上
            for (int i = 0; i < n; i++) {
                if (playground[i][i] != player) {
                    break; // 如果主对角线上有不等于玩家的棋子，跳出循环
                }
                if (i == n - 1) {
                    return true; // 如果遍历到最后一个位置，表示主对角线获胜
                }
            }
        }

        // 检查副对角线
        if (row + col == n - 1) { // 如果最后一个落子在副对角线上
            for (int i = 0; i < n; i++) {
                if (playground[i][n - 1 - i] != player) {
                    break; // 如果副对角线上有不等于玩家的棋子，跳出循环
                }
                if (i == n - 1) {
                    return true; // 如果遍历到最后一个位置，表示副对角线获胜
                }
            }
        }
        return false; // 如果没有任何一行、列或对角线满足条件，则游戏未获胜
    }
//    public boolean isGameWon() {
//        // 检查行
//        for (int i = 0; i < n; i++){
//            int allRow = 0; // 初始化行的计数器
//            for (int j = 0; j < n; j++) {
//                allRow += playground[i][j]; // 累加行的所有元素
//            } //playground[i][j] == 1表示玩家1的棋子，playground[i][j] == -1表示玩家2的棋子
//            if (abs(allRow) == n) { // 如果行的计数器的绝对值等于n，表示有玩家获胜
//                return true; // 游戏获胜
//            }
//        }
//
//        // 检查列
//        for (int j = 0; j < n; j++) {
//            int allCol = 0; // 初始化列的计数器
//            for (int i = 0; i < n; i++) {
//                allCol += playground[i][j]; // 累加列的所有元素
//            }
//            if (abs(allCol) == n) { // 如果列的计数器的绝对值等于n，表示有玩家获胜
//                return true; // 游戏获胜
//            }
//        }
//
//        // 检查主对角线
//        int allMainDiagonal = 0; // 初始化主对角线的计数器
//        for (int i = 0; i < n; i++) {
//            allMainDiagonal += playground[i][i]; // 累加主对角线的所有元素
//        }
//        if (abs(allMainDiagonal) == n) { // 如果主对角线的计数器的绝对值等于n，表示有玩家获胜
//            return true; // 游戏获胜
//        }
//
//        // 检查副对角线
//        int allAntiDiagonal = 0; // 初始化副对角线的计数器
//        for (int i = 0; i < n; i++) {
//            allAntiDiagonal += playground[i][n - 1 - i]; // 累加副对角线的所有元素
//        }
//        if (abs(allAntiDiagonal) == n) { // 如果副对角线的计数器的绝对值等于n，表示有玩家获胜
//            return true; // 游戏获胜
//        }
//
//        // 如果没有任何一行、列或对角线满足条件，则游戏未获胜
//        return false; // 游戏未获胜
//    }

    /**
     *  @return     set of all free fields as some Iterable object
     *  *  返回当前棋盘上所有空格的位置集合。
     *  *  该方法遍历棋盘的每个位置，如果该位置是空格（即值为0），则将其添加到一个集合中。
     *  *  最后返回这个集合。
     *  *  注意：返回的集合是一个可迭代的对象，可以用于遍历所有空格的位置。
     *
     */
    public Iterable<Position> validMoves()
    {
        Stack<Position> freePositions = new Stack<>(); // 使用栈来存储空格位置

        // 遍历棋盘的每个位置
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (playground[i][j] == 0) { // 如果该位置是空格
                    freePositions.push(new Position(i, j)); // 将位置添加到栈中
                }
            }
        }
        return freePositions; // 返回包含所有空格位置的栈
    }

    /**
     *  Outputs current state representation of the Board object.
     *  Practical for debugging.
     *  *  输出当前棋盘的状态表示，适用于调试。
     *  *  *  该方法遍历棋盘的每个位置，并根据位置的值（-1、0或1）输出相应的字符表示。
     */
    public void print() {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                // 根据位置的值输出相应的字符表示
                if (playground[i][j] == -1) {
                    System.out.print("X "); // 玩家1的棋子用X表示
                } else if (playground[i][j] == 1) {
                    System.out.print("O "); // 玩家2的棋子用O表示
                } else {
                    System.out.print(". "); // 空格用.表示
                }
            }
            System.out.println(); // 换行
        }
    }

}

