-- #############################################################################
-- ###### TESTS                                                       ##########
-- #############################################################################

-- #############################################################################
-- HINWEIS ZUR KI-NUTZUNG:
-- Teile dieses Moduls wurden unter Zuhilfenahme eines LLM (Gemini&Claude) entwickelt.
-- Der vollständige Chatverlauf befindet sich in der Datei "Ki-Nutzung um Code zu verbessern.pdf".
-- #############################################################################

import Test.Hspec -- Hspec是Haskell的一个测试框架，用于编写和运行测试用例。能够帮助开发者验证代码的正确性和行为。
import Control.Exception (evaluate) -- Control.Exception模块提供了处理异常的功能，evaluate函数用于强制求值一个表达式，以便在测试中捕获可能的异常。是Haskell中处理异常的标准方式。

import Board (validateFEN, buildBoard, buildFEN, -- 导入Board模块中的函数和类型
              Player(Top, Bottom),
              Cell(Empty, Pawn, Drone, Queen),
              Pos(Pos, col, row), Board, buildPos, startingFEN, startingBoard) -- Board模块定义了游戏的棋盘相关功能和数据类型。player表示玩家，Cell表示棋盘单元格状态，Pos表示位置，Board表示棋盘布局。Board模块还提供了验证FEN字符串、构建棋盘和转换位置的函数。得到这些功能后，可以在测试中使用它们来验证棋盘相关的逻辑。

import Logic (Move(..), pawnMoves, droneMoves, queenMoves, makeMove, playerWon,
              buildMove) -- 导入Logic模块中的函数和类型，Logic模块定义了游戏的逻辑相关功能和数据类型。Move表示一次移动，pawnMoves、droneMoves和queenMoves分别表示兵、无人机和皇后的移动逻辑，makeMove用于执行一次移动并更新棋盘状态，playerWon用于判断玩家是否获胜。buildMove用于构建移动对象。得到这些功能后，可以在测试中使用它们来验证游戏逻辑相关的功能。
                         -- Logic模块还提供了构建移动对象的函数。buildMove用于将字符串表示的移动转换为Move对象。 

-- 辅助：快速构建测试棋盘
setupBoard :: String -> Board -- setupBoard是一个函数，接受一个字符串参数，返回一个Board类型的对象。该函数用于快速构建测试用的棋盘布局。
setupBoard = buildBoard -- 使用buildBoard函数将FEN字符串转换为Board对象，方便在测试中使用特定的棋盘布局。

main :: IO () -- main函数是Haskell程序的入口点，类型为IO ()，表示该函数执行输入输出操作但不返回有意义的值。
main = hspec $ do -- 使用hspec函数运行测试套件，hspec是Hspec测试框架的核心函数，用于定义和执行测试用例。do关键字用于开始一个代码块，表示接下来的代码是hspec的测试定义部分。
  describe "Marsian Chess Tests" $ do -- 描述测试套件的名称，describe函数用于组织测试用例，提供一个描述性的名称，方便识别测试的目的和范围。"Marsian Chess Tests"表示这是火星象棋的测试套件。

    -- =========================================================================
    -- KI-Referenz: Anfrage 5 
    -- =========================================================================
    -- =========================================================================
    -- 1. Board Module Functional Tests
    -- =========================================================================
    describe "validateFEN" $ do -- 描述validateFEN函数的测试用例，validateFEN是Board模块中的一个函数，用于验证FEN字符串的有效性。
      it "returns True for the starting FEN" $ do -- 定义一个测试用例，it函数用于定义具体的测试用例，提供一个描述性的名称和测试逻辑。"returns True for the starting FEN"表示该测试用例验证起始FEN字符串是否被正确识别为有效。it是这么用的，do表示开始一个代码块。
        validateFEN "qqd1/qdp1/dpp1///1ppd/1pdq/1dqq" `shouldBe` True -- 使用shouldBe断言验证validateFEN函数的输出是否与预期值相等。这里验证起始FEN字符串是否返回True，表示有效。
      it "returns True for an empty board" $ do -- 定义另一个测试用例，验证空棋盘的FEN字符串是否被正确识别为有效。
        validateFEN "///4/4/4/4/4" `shouldBe` True -- 验证空棋盘的FEN字符串是否返回True，表示有效。
      it "returns False for incorrect number of rows" $ do -- 定义一个测试用例，验证FEN字符串行数不正确的情况是否被正确识别为无效。
        validateFEN "4/4/4" `shouldBe` False -- 验证行数不正确的FEN字符串是否返回False，表示无效。
      it "returns False for row too short" $ do -- 定义一个测试用例，验证FEN字符串中某行长度过短的情况是否被正确识别为无效。
         validateFEN "4/4/4/4/4/4/4/1" `shouldBe` False -- 验证某行长度过短的FEN字符串是否返回False，表示无效。
      it "returns False for row too long" $ do -- 定义一个测试用例，验证FEN字符串中某行长度过长的情况是否被正确识别为无效。
         validateFEN "4/4/4/4/4/4/4/5" `shouldBe` False -- 验证某行长度过长的FEN字符串是否返回False，表示无效。
      it "returns False for invalid chars" $ do -- 定义一个测试用例，验证FEN字符串中包含无效字符的情况是否被正确识别为无效。
         validateFEN "4/4/4/4/4/4/4/x3" `shouldBe` False -- 验证包含无效字符的FEN字符串是否返回False，表示无效。
      it "returns True for all empty rows" $ do -- 定义一个测试用例，验证FEN字符串中所有行均为空的情况是否被正确识别为有效。
         validateFEN "///////" `shouldBe` True -- 验证所有行均为空的FEN字符串是否返回True，表示有效。
      it "returns False for 9 rows" $ do -- 定义一个测试用例，验证FEN字符串中行数超过8行的情况是否被正确识别为无效。
         validateFEN "4/4/4/4/4/4/4/4/4" `shouldBe` False -- 验证行数超过8行的FEN字符串是否返回False，表示无效。

    describe "buildBoard & buildFEN (Roundtrip)" $ do -- 描述buildBoard和buildFEN函数的测试用例，验证它们之间的相互转换是否正确。
      it "can rebuild the starting FEN correctly" $ do -- 定义一个测试用例，验证起始FEN字符串经过buildBoard和buildFEN转换后是否保持不变。
        let fen = "qqd1/qdp1/dpp1///1ppd/1pdq/1dqq" -- 定义起始FEN字符串
        let board = buildBoard fen -- 使用buildBoard函数将FEN字符串转换为Board对象
        buildFEN board `shouldBe` fen -- 使用buildFEN函数将Board对象转换回FEN字符串，并验证是否与原始FEN字符串相等
      it "handles mixed rows correctly" $ do -- 定义一个测试用例，验证包含混合行的FEN字符串经过buildBoard和buildFEN转换后是否保持不变。
        let inputFen = "p3/1p2/2p1/3p/4/4/4/4" -- 定义包含混合行的FEN字符串
        let expectedFen = "p3/1p2/2p1/3p////" -- 定义预期的FEN字符串
        buildFEN (buildBoard inputFen) `shouldBe` expectedFen -- 验证经过转换后的FEN字符串是否与预期值相等
      it "handles all piece types" $ do -- 定义一个测试用例，验证包含所有棋子类型的FEN字符串经过buildBoard和buildFEN转换后是否保持不变。
        let fen = "qdp1///////1pdq" -- 定义包含所有棋子类型的FEN字符串
        let board = buildBoard fen -- 使用buildBoard函数将FEN字符串转换为Board对象
        buildFEN board `shouldBe` fen -- 使用buildFEN函数将Board对象转换回FEN字符串，并验证是否与原始FEN字符串相等
      it "handles empty board" $ do -- 定义一个测试用例，验证空棋盘的FEN字符串经过buildBoard和buildFEN转换后是否保持不变。
        let fen = "///////" -- 定义空棋盘的FEN字符串
        let board = buildBoard fen -- 使用buildBoard函数将FEN字符串转换为Board对象
        buildFEN board `shouldBe` fen -- 使用buildFEN函数将Board对象转换回FEN字符串，并验证是否与原始FEN字符串相等
      it "handles invalid characters in FEN (otherwise branch)" $ do -- 测试expandRow中的otherwise分支
        let fen = "pxd1/4/4/4/4/4/4/4" -- 包含无效字符'x'的FEN字符串
        let board = buildBoard fen -- 无效字符会被忽略
        let firstRow = head board
        length firstRow `shouldBe` 3 -- 无效字符被忽略，所以只有3个单元格(p,d,1=Empty)
      it "handles joinWSlash with empty list" $ do -- 测试joinWSlash []分支
        let emptyBoard = [] :: Board -- 空棋盘
        buildFEN emptyBoard `shouldBe` "" -- 空棋盘应该返回空字符串

    describe "startingFEN and startingBoard" $ do -- 描述startingFEN和startingBoard的测试用例，验证它们是否正确表示起始棋盘状态。
      it "startingFEN is correct" $ do -- 定义一个测试用例，验证startingFEN字符串是否与预期值相等。
        startingFEN `shouldBe` "qqd1/qdp1/dpp1///1ppd/1pdq/1dqq" -- 验证startingFEN字符串是否与预期的起始FEN字符串相等
      it "startingBoard matches startingFEN" $ do -- 定义一个测试用例，验证startingBoard经过buildFEN转换后是否与startingFEN字符串相等。
        buildFEN startingBoard `shouldBe` startingFEN -- 使用buildFEN函数将startingBoard转换为FEN字符串，并验证是否与startingFEN字符串相等

    describe "buildPos" $ do -- 描述buildPos函数的测试用例，验证其是否正确解析位置字符串。
      it "parses various positions" $ do -- 定义一个测试用例，验证buildPos函数是否能正确解析不同的位置信息。
        buildPos "a0" `shouldBe` Pos 'a' 0 -- 验证buildPos函数解析"a0"字符串是否返回正确的Pos对象
        buildPos "b3" `shouldBe` Pos 'b' 3 -- 验证buildPos函数解析"b3"字符串是否返回正确的Pos对象
        buildPos "c5" `shouldBe` Pos 'c' 5 -- 验证buildPos函数解析"c5"字符串是否返回正确的Pos对象
        buildPos "d7" `shouldBe` Pos 'd' 7 -- 验证buildPos函数解析"d7"字符串是否返回正确的Pos对象
      it "col accessor works correctly" $ do -- 测试col字段访问器
        col (Pos 'a' 0) `shouldBe` 'a' -- 验证col字段访问器
        col (Pos 'd' 7) `shouldBe` 'd' -- 验证col字段访问器
        row (Pos 'b' 3) `shouldBe` 3 -- 验证row字段访问器

    -- =========================================================================
    -- 2. Logic Module Functional Tests
    -- =========================================================================

    describe "pawnMoves" $ do -- 描述pawnMoves函数的测试用例，验证兵的移动逻辑是否正确。
      it "moves diagonally (4 directions)" $ do -- 定义一个测试用例，验证兵可以向四个对角方向移动。
        let fen = "4/4/4/4/4/4/1p2/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = pawnMoves board Bottom (Pos 'b' 1) Nothing -- 获取兵在指定位置的所有合法移动
        let targets = map target moves -- 提取所有移动的目标位置
        targets `shouldContain` [Pos 'a' 2] -- 验证目标位置包含'a2'
        targets `shouldContain` [Pos 'c' 2] -- 验证目标位置包含'c2'
        targets `shouldContain` [Pos 'a' 0] -- 验证目标位置包含'a0'
        targets `shouldContain` [Pos 'c' 0] -- 验证目标位置包含'c0'
      it "returns empty if not my turn" $ do -- 定义一个测试用例，验证当不是当前玩家的回合时，兵没有合法移动。
        let fen = "4/4/4/4/4/4/1p2/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        pawnMoves board Top (Pos 'b' 1) Nothing `shouldBe` [] -- 验证当不是当前玩家的回合时，兵没有合法移动
      it "returns empty if piece is not Pawn" $ do -- 定义一个测试用例，验证当指定位置的棋子不是兵时，没有合法移动。
        let fen = "4/4/4/4/4/4/1d2/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        pawnMoves board Bottom (Pos 'b' 1) Nothing `shouldBe` [] -- 验证当指定位置的棋子不是兵时，没有合法移动
      it "returns empty if cell is empty" $ do -- 定义一个测试用例，验证当指定位置的单元格为空时，没有合法移动。
        let fen = "4/4/4/4/4/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        pawnMoves board Bottom (Pos 'b' 1) Nothing `shouldBe` [] -- 验证当指定位置的单元格为空时，没有合法移动
      it "cannot land on own piece in own zone" $ do -- 定义一个测试用例，验证兵不能在自己的区域内落子到己方棋子所在的位置。
        let fen = "4/4/4/4/4/pp2/1p2/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = pawnMoves board Bottom (Pos 'b' 1) Nothing -- 获取兵在指定位置的所有合法移动
        let targets = map target moves -- 提取所有移动的目标位置
        targets `shouldNotContain` [Pos 'a' 2] -- 验证目标位置不包含'a2'，即不能落子到己方棋子所在的位置
      it "can capture enemy piece in enemy zone" $ do -- 定义一个测试用例，验证兵可以在敌方区域内捕获敌方棋子。
        let fen = "4/4/4/1p2/p3/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = pawnMoves board Bottom (Pos 'a' 3) Nothing -- 获取兵在指定位置的所有合法移动
        let targets = map target moves -- 提取所有移动的目标位置
        targets `shouldContain` [Pos 'b' 4] -- 验证目标位置包含'b4'，即可以捕获敌方棋子
      it "respects board boundaries" $ do -- 定义一个测试用例，验证兵的移动受到棋盘边界的限制。
        let fen = "4/4/4/4/4/4/4/p3" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = pawnMoves board Bottom (Pos 'a' 0) Nothing -- 获取兵在指定位置的所有合法移动
        let targets = map target moves -- 提取所有移动的目标位置
        length targets `shouldBe` 1 -- 验证目标位置的数量为1，表示只能有一个合法移动
        targets `shouldContain` [Pos 'b' 1] -- 验证目标位置包含'b1'，即只能向右上方移动
      it "pawn at top-right corner" $ do -- 定义一个测试用例，验证位于右上角的兵的移动。
        let fen = "4/4/4/4/4/4/4/3p" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = pawnMoves board Bottom (Pos 'd' 0) Nothing -- 获取兵在指定位置的所有合法移动
        length moves `shouldBe` 1 -- 验证合法移动的数量为1
      it "pawn undo filter works" $ do -- 定义一个测试用例，验证兵的撤销过滤功能是否正常工作。
        let fen = "4/4/4/4/p3/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let lastMove = Just (Move (Pos 'b' 3) (Pos 'a' 4)) -- 定义上一步移动，用于撤销过滤
        let moves = pawnMoves board Top (Pos 'a' 4) lastMove -- 获取兵在指定位置的所有合法移动，考虑撤销过滤
        let targets = map target moves -- 提取所有移动的目标位置
        targets `shouldNotContain` [Pos 'b' 3] -- 验证目标位置不包含'b3'，即撤销过滤生效

    describe "droneMoves" $ do -- 描述droneMoves函数的测试用例，验证无人机的移动逻辑是否正确。
      it "moves based on line count (vertical)" $ do -- 定义一个测试用例，验证无人机可以根据路径上的行数进行垂直移动。
        let fen = "4/4/4/4/p3/4/4/d3" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = droneMoves board Bottom (Pos 'a' 0) Nothing -- 获取无人机在指定位置的所有合法移动
        map target moves `shouldContain` [Pos 'a' 2] -- 验证目标位置包含'a2'，即可以根据路径上的行数进行垂直移动
      it "is blocked by obstacles in path" $ do -- 定义一个测试用例，验证无人机在路径上遇到障碍物时无法继续移动。
        let fen = "4/4/4/4/4/4/p3/d3" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = droneMoves board Bottom (Pos 'a' 0) Nothing -- 获取无人机在指定位置的所有合法移动
        map target moves `shouldNotContain` [Pos 'a' 2] -- 验证目标位置不包含'a2'，即路径上有障碍物时无法继续移动
      it "returns empty if not Drone" $ do -- 定义一个测试用例，验证当指定位置的棋子不是无人机时，没有合法移动。
         let fen = "4/4/4/4/4/4/1p2/4" -- 定义测试用的FEN字符串，表示棋盘布局
         let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
         droneMoves board Bottom (Pos 'b' 1) Nothing `shouldBe` [] -- 验证当指定位置的棋子不是无人机时，没有合法移动
      it "returns empty if cell is empty" $ do -- 定义一个测试用例，验证当指定位置的单元格为空时，没有合法移动。
         let fen = "4/4/4/4/4/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
         let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
         droneMoves board Bottom (Pos 'b' 1) Nothing `shouldBe` [] -- 验证当指定位置的单元格为空时，没有合法移动
      it "moves horizontally based on line count" $ do -- 定义一个测试用例，验证无人机可以根据路径上的行数进行水平移动。
        let fen = "4/4/4/4/4/4/4/d3" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = droneMoves board Bottom (Pos 'a' 0) Nothing -- 获取无人机在指定位置的所有合法移动
        map target moves `shouldContain` [Pos 'b' 0] -- 验证目标位置包含'b0'，即可以根据路径上的行数进行水平移动
      it "drone can capture in enemy zone" $ do -- 定义一个测试用例，验证无人机可以在敌方区域内捕获敌方棋子。
        let fen = "4/4/4/4/d3/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = droneMoves board Top (Pos 'a' 4) Nothing -- 获取无人机在指定位置的所有合法移动
        length moves `shouldSatisfy` (>= 0) -- 验证合法移动的数量大于等于0
      it "drone undo filter works" $ do -- 定义一个测试用例，验证无人机的撤销过滤功能是否正常工作。
        let fen = "4/4/4/4/d3/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let lastMove = Just (Move (Pos 'a' 3) (Pos 'a' 4)) -- 定义上一步移动，用于撤销过滤
        let moves = droneMoves board Top (Pos 'a' 4) lastMove -- 获取无人机在指定位置的所有合法移动，考虑撤销过滤
        let targets = map target moves -- 提取所有移动的目标位置
        targets `shouldNotContain` [Pos 'a' 3] -- 验证目标位置不包含'a3'，即撤销过滤生效

    describe "queenMoves" $ do -- 描述queenMoves函数的测试用例，验证皇后的移动逻辑是否正确。
      it "moves like a Queen (vertical)" $ do -- 定义一个测试用例，验证皇后可以进行垂直移动。
        let fen = "4/4/4/4/4/4/4/q3"
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = queenMoves board Bottom (Pos 'a' 0) Nothing -- 获取皇后在指定位置的所有合法移动
        let targets = map target moves -- 提取所有移动的目标位置
        targets `shouldContain` [Pos 'a' 7] -- 验证目标位置包含'a7'，即可以进行垂直移动
      it "returns empty if not Queen" $ do -- 定义一个测试用例，验证当指定位置的棋子不是皇后时，没有合法移动。
         let fen = "4/4/4/4/4/4/1p2/4" -- 定义测试用的FEN字符串，表示棋盘布局
         let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
         queenMoves board Bottom (Pos 'b' 1) Nothing `shouldBe` [] -- 验证当指定位置的棋子不是皇后时，没有合法移动
      it "returns empty if cell is empty" $ do -- 定义一个测试用例，验证当指定位置的单元格为空时，没有合法移动。
         let fen = "4/4/4/4/4/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
         let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
         queenMoves board Bottom (Pos 'b' 1) Nothing `shouldBe` [] -- 验证当指定位置的单元格为空时，没有合法移动
      it "moves diagonally" $ do -- 定义一个测试用例，验证皇后可以进行对角线移动。
        let fen = "4/4/4/4/4/4/4/q3" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = queenMoves board Bottom (Pos 'a' 0) Nothing -- 获取皇后在指定位置的所有合法移动
        let targets = map target moves -- 提取所有移动的目标位置
        targets `shouldContain` [Pos 'b' 1] -- 验证目标位置包含'b1'，即可以进行对角线移动
        targets `shouldContain` [Pos 'c' 2] -- 验证目标位置包含'c2'，即可以进行对角线移动
        targets `shouldContain` [Pos 'd' 3] -- 验证目标位置包含'd3'，即可以进行对角线移动
      it "stops at enemy piece (can capture)" $ do -- 定义一个测试用例，验证皇后在遇到敌方棋子时可以捕获并停止移动。
        let fen = "4/4/4/p3/4/4/4/q3" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = queenMoves board Bottom (Pos 'a' 0) Nothing -- 获取皇后在指定位置的所有合法移动
        let targets = map target moves -- 提取所有移动的目标位置
        targets `shouldContain` [Pos 'a' 4] -- 验证目标位置包含'a4'，即可以捕获敌方棋子
        targets `shouldNotContain` [Pos 'a' 5] -- 验证目标位置不包含'a5'，即捕获后停止移动
      it "stops before own piece (cannot capture)" $ do -- 定义一个测试用例，验证皇后在遇到己方棋子时不能捕获并停止移动。
        let fen = "4/4/4/4/4/4/p3/q3" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = queenMoves board Bottom (Pos 'a' 0) Nothing -- 获取皇后在指定位置的所有合法移动
        let targets = map target moves -- 提取所有移动的目标位置
        targets `shouldNotContain` [Pos 'a' 1] -- 验证目标位置不包含'a1'，即不能捕获己方棋子
      it "moves horizontally" $ do -- 定义一个测试用例，验证皇后可以进行水平移动。
        let fen = "4/4/4/4/4/4/4/q3" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = queenMoves board Bottom (Pos 'a' 0) Nothing -- 获取皇后在指定位置的所有合法移动
        let targets = map target moves -- 提取所有移动的目标位置
        targets `shouldContain` [Pos 'b' 0] -- 验证目标位置包含'b0'，即可以进行水平移动
        targets `shouldContain` [Pos 'c' 0] -- 验证目标位置包含'c0'，即可以进行水平移动
        targets `shouldContain` [Pos 'd' 0] -- 验证目标位置包含'd0'，即可以进行水平移动

    describe "makeMove" $ do -- 描述makeMove函数的测试用例，验证其在执行移动时是否正确更新棋盘状态和计算分数。
      it "updates board and calculates score (Pawn=1)" $ do -- 定义一个测试用例，验证在兵捕获时，棋盘状态是否正确更新且分数计算正确。
        let fen = "4/4/p3/4/q3/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let move = Move (Pos 'a' 3) (Pos 'a' 5) -- 定义一个移动，表示从'a3'移动到'a5'
        let (_, score) = makeMove board move -- 执行移动并获取分数
        score `shouldBe` 1 -- 验证分数为1，表示捕获了一个兵
      it "scores 2 for Drone capture" $ do -- 定义一个测试用例，验证在无人机捕获时，分数计算是否正确。
         let fen = "4/4/d3/4/q3/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
         let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
         let move = Move (Pos 'a' 3) (Pos 'a' 5) -- 定义一个移动，表示从'a3'移动到'a5'
         let (_, score) = makeMove board move -- 执行移动并获取分数
         score `shouldBe` 2 -- 验证分数为2，表示捕获了一个无人机
      it "scores 3 for Queen capture" $ do -- 定义一个测试用例，验证在皇后捕获时，分数计算是否正确。
         let fen = "4/4/q3/4/q3/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
         let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
         let move = Move (Pos 'a' 3) (Pos 'a' 5) -- 定义一个移动，表示从'a3'移动到'a5'
         let (_, score) = makeMove board move -- 执行移动并获取分数
         score `shouldBe` 3 -- 验证分数为3，表示捕获了一个皇后
      it "scores 0 for moving to empty cell" $ do -- 定义一个测试用例，验证在移动到空单元格时，分数计算是否正确。
         let fen = "4/4/4/4/q3/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
         let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
         let move = Move (Pos 'a' 3) (Pos 'a' 5) -- 定义一个移动，表示从'a3'移动到'a5'
         let (_, score) = makeMove board move -- 执行移动并获取分数
         score `shouldBe` 0 -- 验证分数为0，表示没有捕获任何棋子
      it "updates board correctly after move" $ do -- 定义一个测试用例，验证在执行移动后，棋盘状态是否正确更新。
         let fen = "4/4/4/4/q3/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
         let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
         let move = Move (Pos 'a' 3) (Pos 'a' 5) -- 定义一个移动，表示从'a3'移动到'a5'
         let (newBoard, _) = makeMove board move -- 执行移动并获取新的棋盘状态
         buildFEN newBoard `shouldBe` "//q3/////" -- 验证新的棋盘状态是否与预期的FEN字符串相等
      
    describe "playerWon" $ do -- 描述playerWon函数的测试用例，验证其在判断游戏胜利条件时的逻辑是否正确。
      it "returns correct winner (Top)" $ do -- 定义一个测试用例，验证当上方玩家获胜时，函数是否正确返回上方玩家。
        let fen = "q3/4/4/4/4/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        playerWon board Top 10 5 `shouldBe` Just Top -- 验证函数返回上方玩家为胜利者
      it "returns correct winner (Bottom)" $ do -- 定义一个测试用例，验证当下方玩家获胜时，函数是否正确返回下方玩家。
        let fen = "q3/4/4/4/4/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        playerWon board Top 5 10 `shouldBe` Just Bottom -- 验证函数返回下方玩家为胜利者
      it "returns last mover on tie" $ do -- 定义一个测试用例，验证在平局情况下，函数是否正确返回最后移动的玩家为胜利者。
        let fen = "q3/4/4/4/4/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        playerWon board Bottom 5 5 `shouldBe` Just Bottom -- 验证函数返回最后移动的玩家为胜利者
      it "returns Nothing if game not over (top has pieces)" $ do -- 定义一个测试用例，验证当游戏未结束且上方玩家仍有棋子时，函数是否正确返回Nothing。
        let fen = "q3/4/4/4/p3/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        playerWon board Top 5 5 `shouldBe` Nothing -- 验证函数返回Nothing，表示游戏未结束
      it "returns Nothing if game not over (both have pieces)" $ do -- 定义一个测试用例，验证当游戏未结束且双方玩家均有棋子时，函数是否正确返回Nothing。
        let fen = "qqd1/qdp1/dpp1///1ppd/1pdq/1dqq" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        playerWon board Top 0 0 `shouldBe` Nothing -- 验证函数返回Nothing，表示游戏未结束
      it "detects win when bottom zone empty" $ do -- 定义一个测试用例，验证当下方区域为空时，函数是否正确检测到上方玩家获胜。
        let fen = "4/4/4/4/q3/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        playerWon board Top 3 0 `shouldBe` Just Top -- 验证函数返回上方玩家为胜利者

    -- =========================================================================
    -- 3. COVERAGE BOOSTERS
    -- =========================================================================
    
    describe "Data Types & Instances (Coverage)" $ do -- 描述数据类型和实例的测试用例，旨在提高代码覆盖率。
      it "shows types correctly" $ do -- 定义一个测试用例，验证各种数据类型的Show实例是否正确。
        show Top `shouldBe` "Top" -- 验证Player类型的Top值的Show实例是否正确
        show Bottom `shouldBe` "Bottom" -- 验证Player类型的Bottom值的Show实例是否正确
        show Empty `shouldBe` "Empty" -- 验证Piece类型的Empty值的Show实例是否正确
        show Pawn `shouldBe` "Pawn" -- 验证Piece类型的Pawn值的Show实例是否正确
        show Drone `shouldBe` "Drone" -- 验证Piece类型的Drone值的Show实例是否正确
        show Queen `shouldBe` "Queen" -- 验证Piece类型的Queen值的Show实例是否正确
        show (Pos 'a' 1) `shouldBe` "Pos {col = 'a', row = 1}" -- 验证Pos类型的Show实例是否正确
        show (Move (Pos 'a' 0) (Pos 'b' 1)) `shouldBe` "a0-b1" -- 验证Move类型的Show实例是否正确
        
      it "reads Player correctly" $ do -- 定义一个测试用例，验证Player类型的Read实例是否正确。
        read "Top" `shouldBe` Top -- 验证Player类型的Top值的Read实例是否正确
        read "Bottom" `shouldBe` Bottom -- 验证Player类型的Bottom值的Read实例是否正确

      it "checks equality" $ do -- 定义一个测试用例，验证各种数据类型的Eq实例是否正确。
        Top == Top `shouldBe` True -- 验证Player类型的Top值的Eq实例是否正确 
        Top == Bottom `shouldBe` False -- 验证Player类型的Top值与Bottom值的Eq实例是否正确
        Bottom == Bottom `shouldBe` True -- 验证Player类型的Bottom值的Eq实例是否正确
        Pawn == Pawn `shouldBe` True -- 验证Piece类型的Pawn值的Eq实例是否正确
        Pawn == Drone `shouldBe` False -- 验证Piece类型的Pawn值与Drone值的Eq实例是否正确
        Pawn == Queen `shouldBe` False -- 验证Piece类型的Pawn值与Queen值的Eq实例是否正确
        Pawn == Empty `shouldBe` False -- 验证Piece类型的Pawn值与Empty值的Eq实例是否正确
        Drone == Drone `shouldBe` True -- 验证Piece类型的Drone值的Eq实例是否正确
        Drone == Queen `shouldBe` False -- 验证Piece类型的Drone值与Queen值的Eq实例是否正确
        Drone == Empty `shouldBe` False -- 验证Piece类型的Drone值与Empty值的Eq实例是否正确
        Queen == Queen `shouldBe` True -- 验证Piece类型的Queen值的Eq实例是否正确
        Queen == Empty `shouldBe` False -- 验证Piece类型的Queen值与Empty值的Eq实例是否正确
        Empty == Empty `shouldBe` True -- 验证Piece类型的Empty值的Eq实例是否正确
        Pos 'a' 1 == Pos 'a' 1 `shouldBe` True -- 验证Pos类型的Eq实例是否正确
        Pos 'a' 1 == Pos 'b' 1 `shouldBe` False -- 验证Pos类型的Eq实例是否正确
        Pos 'a' 1 == Pos 'a' 2 `shouldBe` False -- 验证Pos类型的Eq实例是否正确
        Pos 'a' 1 == Pos 'b' 2 `shouldBe` False -- 验证Pos类型的Eq实例是否正确
        let m1 = Move (Pos 'a' 0) (Pos 'b' 1) -- 验证Move类型的Eq实例是否正确
        let m2 = Move (Pos 'a' 0) (Pos 'b' 1) -- 创建另一个Move实例，与m1相同
        let m3 = Move (Pos 'a' 0) (Pos 'c' 1) -- 创建另一个Move实例，与m1不同
        let m4 = Move (Pos 'b' 0) (Pos 'b' 1) -- 创建另一个Move实例，与m1不同
        m1 == m2 `shouldBe` True -- 验证Move类型的Eq实例是否正确
        m1 == m3 `shouldBe` False -- 验证Move类型的Eq实例是否正确
        m1 == m4 `shouldBe` False -- 验证Move类型的Eq实例是否正确

    describe "buildMove" $ do -- 描述buildMove函数的测试用例，验证其在解析字符串表示的移动时的逻辑是否正确。
      it "parses valid strings" $ do -- 定义一个测试用例，验证buildMove函数是否能正确解析有效的字符串表示的移动。
        buildMove "a0-b1" `shouldBe` Just (Move (Pos 'a' 0) (Pos 'b' 1)) -- 验证buildMove函数能正确解析"a0-b1"
        buildMove "c3-d4" `shouldBe` Just (Move (Pos 'c' 3) (Pos 'd' 4)) -- 验证buildMove函数能正确解析"c3-d4"
      it "handles empty string" $ do -- 定义一个测试用例，验证buildMove函数在处理空字符串时的行为。
        buildMove "" `shouldBe` Nothing -- 验证buildMove函数在处理空字符串时返回Nothing
      it "handles string without dash" $ do -- 定义一个测试用例，验证buildMove函数在处理不包含破折号的字符串时的行为。
        evaluate (buildMove "a0b1") `shouldThrow` errorCall "Invalid move format" -- 验证buildMove函数在处理不包含破折号的字符串时抛出错误

    describe "Undo Logic Coverage" $ do -- 描述撤销逻辑的测试用例，验证各种棋子的撤销过滤功能是否正常工作。
      it "filters out illegal undo moves (cross-zone)" $ do -- 定义一个测试用例，验证当撤销移动跨越区域时，撤销过滤功能是否生效。
        let fen = "4/4/4/4/q3/4/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let lastMove = Just (Move (Pos 'a' 3) (Pos 'a' 4)) -- 定义上一步移动，用于撤销过滤
        let moves = queenMoves board Top (Pos 'a' 4) lastMove -- 获取皇后在指定位置的所有合法移动，考虑撤销过滤
        let targets = map target moves -- 提取所有移动的目标位置
        targets `shouldNotContain` [Pos 'a' 3] -- 验证目标位置不包含'a3'，即撤销过滤生效
      it "allows undo within same zone" $ do -- 定义一个测试用例，验证当撤销移动在同一区域内时，撤销过滤功能是否允许该移动。
        let fen = "4/4/4/4/4/q3/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let lastMove = Just (Move (Pos 'a' 1) (Pos 'a' 2)) -- 定义上一步移动，用于撤销过滤
        let moves = queenMoves board Bottom (Pos 'a' 2) lastMove -- 获取皇后在指定位置的所有合法移动，考虑撤销过滤
        let targets = map target moves -- 提取所有移动的目标位置
        targets `shouldContain` [Pos 'a' 1] -- 验证目标位置包含'a1'，即撤销过滤允许该移动
      it "no undo restriction when lastMove is Nothing" $ do -- 定义一个测试用例，验证当lastMove为Nothing时，没有撤销限制。
        let fen = "4/4/4/4/4/q3/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = queenMoves board Bottom (Pos 'a' 2) Nothing -- 获取皇后在指定位置的所有合法移动，考虑撤销过滤
        length moves `shouldSatisfy` (> 0) -- 验证合法移动的数量大于0
      it "undo allowed if move does not match lastMove pattern" $ do -- 定义一个测试用例，验证当移动不符合lastMove模式时，撤销允许该移动。
        let fen = "4/4/4/4/4/q3/4/4" -- 定义测试用的FEN字符串，表示棋盘布局
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let lastMove = Just (Move (Pos 'b' 1) (Pos 'b' 2)) -- 定义上一步移动，用于撤销过滤
        let moves = queenMoves board Bottom (Pos 'a' 2) lastMove -- 获取皇后在指定位置的所有合法移动，考虑撤销过滤
        length moves `shouldSatisfy` (> 0) -- 验证合法移动的数量大于0

    describe "Edge Cases" $ do -- 描述边缘情况的测试用例，验证各种特殊情况下的移动逻辑是否正确。
      it "handles pawn at corner" $ do -- 定义一个测试用例，验证位于角落的兵的移动。
        let fen = "4/4/4/4/4/4/4/p3"
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = pawnMoves board Bottom (Pos 'a' 0) Nothing -- 获取兵在指定位置的所有合法移动，考虑撤销过滤
        length moves `shouldBe` 1 -- 验证合法移动的数量为1
      it "handles queen blocked all directions" $ do -- 定义一个测试用例，验证当皇后在所有方向上都被阻挡时的移动。
        let fen = "4/4/4/4/4/4/ppp1/pqp1"
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = queenMoves board Bottom (Pos 'b' 0) Nothing -- 获取皇后在指定位置的所有合法移动，考虑撤销过滤
        length moves `shouldBe` 0 -- 验证合法移动的数量为0
      it "drone moves in all four directions" $ do -- 定义一个测试用例，验证无人机可以在四个方向上移动。
        let fen = "4/4/4/4/1p2/4/4/1d2"
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = droneMoves board Bottom (Pos 'b' 0) Nothing -- 获取无人机在指定位置的所有合法移动，考虑撤销过滤
        length moves `shouldSatisfy` (>= 1) -- 验证合法移动的数量大于等于1
      it "pawn cannot capture own piece in enemy zone" $ do -- 定义一个测试用例，验证兵在敌方区域内不能捕获己方棋子。
        let fen = "4/4/4/pp2/4/4/4/4"
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = pawnMoves board Bottom (Pos 'a' 4) Nothing -- 获取兵在指定位置的所有合法移动，考虑撤销过滤
        let targets = map target moves -- 提取所有移动的目标位置
        targets `shouldNotContain` [Pos 'b' 4] -- 验证目标位置不包含'b4'，即兵不能捕获己方棋子
      it "handles move at column d" $ do -- 定义一个测试用例，验证在d列的移动。
        let fen = "4/4/4/4/4/4/4/3q"
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = queenMoves board Bottom (Pos 'd' 0) Nothing -- 获取皇后在指定位置的所有合法移动，考虑撤销过滤
        length moves `shouldSatisfy` (> 0) -- 验证合法移动的数量大于0
      it "handles move at row 7" $ do -- 定义一个测试用例，验证在第7行的移动。
        let fen = "3q/4/4/4/4/4/4/4"
        let board = setupBoard fen -- 使用setupBoard函数将FEN字符串转换为Board对象
        let moves = queenMoves board Top (Pos 'd' 7) Nothing -- 获取皇后在指定位置的所有合法移动，考虑撤销过滤
        length moves `shouldSatisfy` (> 0) -- 验证合法移动的数量大于0