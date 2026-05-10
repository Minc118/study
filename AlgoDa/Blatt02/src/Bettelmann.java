import java.util.*;

/**
 * The class {@code Bettelmann} simulated the card game 'Bettelmann'. You can construct objects
 * either by providing the piles of cards of the two players, or by requesting a shuffled
 * distribution of cards.
 */
public class Bettelmann {
    private Deque<Card> closedPile1; //玩家1的牌堆（关闭状态）
    private Deque<Card> closedPile2; //玩家2的牌堆（关闭状态）
    private int winner = -1; // -1 表示游戏尚未结束； 0 = 平局， 1 = 玩家1赢， 2 = 玩家2赢

    /**
     * Constructor which initializes both players with empty piles.
     */
    public Bettelmann() {
        closedPile1 = new LinkedList<>();
        closedPile2 = new LinkedList<>();
    }

    /**
     * Constructor which initializes both players with the provided piles of cards.
     *
     * @param pile1 pile of cards of player 1.
     * @param pile2 pile of cards of player 2.
     */
    public Bettelmann(Deque<Card> pile1, Deque<Card> pile2) {
        closedPile1 = pile1;
        closedPile2 = pile2;
    }

    /**
     * Returns the closed pile of player 1 (required for the tests).
     *
     * @return The closed pile of player 1.
     */
    public Deque<Card> getClosedPile1() {
        return closedPile1;
    }

    /**
     * Returns the closed pile of player 2 (required for the tests).
     *
     * @return The closed pile of player 2.
     */
    public Deque<Card> getClosedPile2() {
        return closedPile2;
    }

    /**
     * Play one round of the game. This includes drawing more cards, when both players
     * have drawn cards of the same rank. At the end of the round, the player with the
     * higher ranked card wins the trick, so all drawn cards from that round are added
     * to the bottom of her/his closed pile of cards.
     */
    public void playRound() {
        // TODO implement this method
        if (closedPile1.isEmpty()){ //如果玩家1的牌堆空了，玩家2赢
            winner = 2;
            return;
        } else if (closedPile2.isEmpty()){
            winner = 1;
            return;
        }

        //简历数据结构 使用queue 先进先出FIFO
        Queue<Card> open1 = new LinkedList<>(); //玩家1翻开的牌 -空的数据结构来储存
        Queue<Card> open2 = new LinkedList<>(); //玩家2翻开的牌 -空的数据结构来储存

        Card C1 = closedPile1.poll(); //抽牌
        Card C2 = closedPile2.poll(); //抽牌
        open1.add(C1); //将抽到的牌存进去
        open2.add(C2);

        //相等就抽牌
        while (C1.compareTo(C2) == 0) {
            // 如果两位玩家同时没有牌，则为平局
            if (closedPile1.isEmpty() && closedPile2.isEmpty()) {
                winner = 0;
                return;
            }
            //用还有没有牌来定输赢
            if (closedPile1.isEmpty()) {
                winner = 2;
                return;
            }
            if (closedPile2.isEmpty()) {
                winner = 1;
                return;
            }

            C1 = closedPile1.poll();
            C2 = closedPile2.poll();
            open1.add(C1); //将抽到的牌存进去
            open2.add(C2);
            }

        //判断大小
        if (C1.compareTo(C2) > 0 ){
            closedPile1.addAll(open1);
            closedPile1.addAll(open2);
            if (closedPile2.isEmpty() && closedPile1.size() > 0) {
                winner = 1;
                return;
            }
        } else {
            closedPile2.addAll(open2);
            closedPile2.addAll(open1);
            if (closedPile1.isEmpty() && closedPile2.size() > 0) {
                winner = 2;
                return;
            }
        }

        // 回合结束后再次检查牌堆，决定游戏是否结束
        if (closedPile1.isEmpty() && closedPile2.isEmpty()) {
            winner = 0; // 平局
        } else if (closedPile1.isEmpty()) {
            winner = 2; // 玩家2胜
        } else if (closedPile2.isEmpty()) {
            winner = 1; // 玩家1胜
        }
    }

    /**
     * Returns the winner of the game after the end, or -1 during the game.
     *
     * @return the winner of game (1 or 2), or -1 while the game is ongoing.
     */
    public int getWinner() {
        return winner;
    }

    /**
     * Deal the given deck of cards alternately to the two players.
     * Side effect: The deck is empty after calling this method.
     *
     * @param deck The deck of cards that is distributed to the players.
     */
    public void distributeCards(Stack<Card> deck) {
        closedPile1.clear();
        closedPile2.clear();
        // use addFirst() because the last distributed card should be drawn first
        while (!deck.isEmpty()) {
            Card card = deck.pop();
            closedPile1.addFirst(card);
            if (!deck.isEmpty()) {
                card = deck.pop();
                closedPile2.addFirst(card);
            }
        }
    }

    /**
     * Shuffle a deck of cards and distribute it evenly to the two players.
     */
    public void distributeCards() {
        Stack<Card> deck = new Stack<>();
        for (int i = 0; i < Card.nCards; i++){
            deck.add(new Card(i));
        }
        Collections.shuffle(deck);
        distributeCards(deck);
    }

    /**
     * Returns a String representation of closed piles of cards of the two players.
     *
     * @return String representation of the state of the game.
     */
    @Override
    public String toString() {
        return "Player 1: " + closedPile1 + "\nPlayer 2: " + closedPile2;
    }

    public static void main(String[] args) {
/*
        // Game with a complete, shuffled deck
        Bettelmann game = new Bettelmann();
        game.distributeCards();
*/

        // For testing, you may also use specific distribtions and a small number of cards like this:
        int[] deckArray = {28, 30, 6, 23, 17, 14};
        Stack<Card> deck = new Stack<>();
        for (int id : deckArray) {
            deck.push(new Card(id));
        }
        Bettelmann game = new Bettelmann();
        game.distributeCards(deck);

        // This part is the same for both of the above variants
        System.out.println("Initial situation (top card first):\n" + game);
        int round = 0;
        while (round < 1000000 && game.getWinner()<0) {
            round++;
            game.playRound();
            System.out.println("State after round " + round + ":\n" + game);
        }
    }
}
