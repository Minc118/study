/**
 * This class implements and evaluates game situations of a TicTacToe game.
 */


public class TicTacToe {

    /**
     * Returns an evaluation for player at the current board state.
     * Arbeitet nach dem Prinzip der Alphabeta-Suche. Works with the principle of Alpha-Beta-Pruning.
     *
     * @param board  current Board object for game situation - 当前游戏局面
     * @param player player who has a turn - 当前玩家
     * @return rating of game situation from player's point of view - 从玩家的角度对游戏局面进行评分
     **/

    public static int alphaBeta(Board board, int player) {
        // 初始 a = Integer.MIN_VALUE, b = Integer.MAX_VALUE, depth = 0
        return alphaBeta(board, player, Integer.MIN_VALUE/2, Integer.MAX_VALUE/2,0);
        // 这里调用了重载的 alphaBeta 方法，传入初始的 a, b, 和 depth = 0
    }

    public static int alphaBeta(Board board, int player, int alpha, int beta, int depth) {

        //检查是否终局，如果上一步落子让对手获胜，则返回负分
        if (board.isGameWon()) {
            //计算当前玩家的分数
            int p = board.nFreeFields(); // 计算当前局面剩余的空格数量作为评分
            // 如果当前玩家获胜，返回正分，否则返回负分
            if (board.lastPlayer == player) {
                // 如果上一步落子是当前玩家 player，则返回正分
                return p + 1; // 返回当前局面的评分 + 1
            } else {
                // 如果上一步落子是对手 -player，则返回负分
                return -(p + 1); // 返回当前局面的评分 - 1
            }
        }
        // 如果棋盘已满或有玩家获胜，返回评分
        if (board.nFreeFields() == 0) { // 棋盘已满，返回评分
            return 0; // 返回当前局面的评分
        }

        int bestValue = Integer.MIN_VALUE/2; // 初始化最佳评分为最小值

        // 遍历所有可能的落子位置
        for (Position pos : board.validMoves()) {
            // 尝试在当前位置落子
            board.doMove(pos, player); //真正落子
            // 递归调用 alphaBeta 方法，切换玩家
            int value = -alphaBeta(board, -player, -beta, -alpha, depth + 1); // 递归调用，切换玩家并取反评分 - 最大化自己，最小化对手
            // 撤销落子
            board.undoMove(pos);

            // 更新最佳评分
            if (value > bestValue) {
                bestValue = value;
            }
            // 更新 alpha 值
            alpha = Math.max(alpha, value);
            // 剪枝
            if (beta <= alpha) {
                break; // 如果 beta 小于等于 alpha，剪枝
            }
        }
        return bestValue; // 返回最佳评分
    }

    /**
     * Vividly prints a rating for each currently possible move out at System.out.
     * (from player's point of view)
     * Uses Alpha-Beta-Pruning to rate the possible moves.
     * formatting: See "Beispiel 1: Bewertung aller Zugmöglichkeiten" (Aufgabenblatt 4).
     *
     * @param board  current Board object for game situation
     * @param player player who has a turn
     **/
    public static void evaluatePossibleMoves(Board board, int player) {
        int n = board.getN(); // 获取棋盘的大小

        // 遍历棋盘的每个位置
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                Position pos = new Position(i, j); // 创建一个位置对象
                if (board.getField(pos) == 1) { // 如果该位置是当前玩家的棋子
                    System.out.print("x "); // 打印"x"表示当前玩家的棋子
                } else if (board.getField(pos) == -1) { // 如果该位置是对手的棋子
                    System.out.print("o "); // 打印"o"表示对手的棋子
                } else { // 如果该位置是空的
                    //当前位置是空的，计算该位置的评分
                    board.doMove(pos, player); // 在当前位置落子
                    int punkt = alphaBeta(board, -player, Integer.MIN_VALUE, Integer.MAX_VALUE, 1); // 计算评分
                    board.undoMove(pos); // 撤销落子
                    System.out.print(punkt + " "); // 打印"."表示空格
                }
                if (j < n - 1) {
                    System.out.print(" "); // 打印空格分隔
                }
            }
            System.out.println(); // 换行
        }
    }


    /**
     * Main method to test the TicTacToe class.
     * Creates a 3x3 board and evaluates possible moves for player 1.
     * 创建一个board对象，大小为3x3
     * 手动设置一些棋子状态
     * 调用evaluatePossibleMoves方法，评估当前棋盘状态下的所有可能落子
     * <p>
     * 也可以在这里添加更多的测试代码来验证功能
     */

    public static void main(String[] args) {
        Board board = new Board(3); // 创建一个3x3的棋盘

        board.doMove(new Position(0, 1), 1); //
        board.doMove(new Position(2, 1), -1); //
        //现在轮到玩家1落子，用evaluatePossibleMoves方法评估当前棋盘状态下的所有可能落子
        int nullpunkt = alphaBeta(board, 1); // 调用alphaBeta方法，获取当前局面的评分
        System.out.println("Max punkt in 3x3: " + nullpunkt); // 打印评分
        evaluatePossibleMoves(board, 1); // 评估当前棋盘状态下的所有可能落子
        // 期待输出一个3x3的棋盘，每个位置上显示当前局面的评分




        Board newBoard = new Board(3); // 创建一个新的3x3棋盘
        newBoard.doMove(new Position(0, 0), 1); //
        newBoard.doMove(new Position(1, 0), -1); //
        newBoard.doMove(new Position(0, 1), 1); //
        newBoard.doMove(new Position(1, 1), -1); //
        // 这时轮到x下， 可以在(2,0)位置落子，获得最大分1
        int maxPunkt = alphaBeta(newBoard, 1); // 计算最大分数
        System.out.println("Null Punkt in 3x3: " + maxPunkt); // 打印最大分数
        evaluatePossibleMoves(newBoard,1);


        //测试2x2棋盘
        Board board2x2 = new Board(2); // 创建一个2x2的棋盘
        // 在2x2棋盘上调用alphaBeta方法，获取当前局面的评分
        //任何一方落子后，对手立刻就能连2个
        //所有先手必胜
        // p = 1, p+1 = 2
        int nullpunkt2x2 = alphaBeta(board2x2, 1);
        System.out.println("Nullpunkt in 2x2: " + nullpunkt2x2); // 打印评分
        // 期待输出2，因为在2x2棋盘上，先手必胜
    }
}

