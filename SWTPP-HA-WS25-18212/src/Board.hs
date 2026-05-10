module Board where  -- do NOT CHANGE export of module

-- #############################################################################
-- HINWEIS ZUR KI-NUTZUNG:
-- Teile dieses Moduls wurden unter Zuhilfenahme eines LLM (Gemini) entwickelt.
-- Der vollständige Chatverlauf befindet sich in der Datei "Ki-Nutzung um Code zu verbessern.pdf".
-- #############################################################################

-- IMPORTS HERE
-- Note: Imports allowed that DO NOT REQUIRE TO ANY CHANGES TO package.yaml, e.g.:
--       import Data.Chars
import Data.Char(isDigit, digitToInt) --isDigit, digitToInt是用来处理字符和数字转换的函数，他们们来自Data.Char模块, Data.Char模块提供了处理字符的函数,包括字符与其对应的整数ASCII码之间的转换，以及判断字符类型的函数。
import Text.Read()--用于读取和解析字符串,但在此代码中未直接使用,可能是为了未来的扩展或保持一致性而导入的。

-- #############################################################################
-- ############# GIVEN IMPLEMENTATION                           ################
-- ############# Given data types may NOT be changed            ################
-- #############################################################################

data Player = Top | Bottom deriving (Show, Read) -- Player表示游戏中的两个玩家：Top和Bottom，它们可以通过Show和Read类型类进行字符串表示和解析。 deriving表示Player类型自动实现Show和Read类型类的功能。是Haskell中的一种简洁方式，用于定义数据类型及其行为。
data Cell = Empty | Queen | Drone | Pawn deriving Show -- Cell表示棋盘上的单元格状态，可以是Empty（空），Queen（皇后），Drone（无人机），Pawn（兵）。 deriving Show表示Cell类型自动实现Show类型类的功能，用于将Cell值转换为字符串表示。
data Pos = Pos { col :: Char, row :: Int } deriving Show -- Pos表示棋盘上的位置，由列（col）和行（row）组成。 col是一个字符，表示列（如'a'到'd'），row是一个整数，表示行（1到8）。 deriving Show表示Pos类型自动实现Show类型类的功能，用于将Pos值转换为字符串表示。
type Board = [[Cell]] -- Board表示棋盘，是一个二维列表，每个元素是一个Cell，表示棋盘上的单元格状态。[[Cell]]表示一个包含多个行的列表，每行又是一个包含多个Cell的列表。[[]]是Haskell中表示二维数组或矩阵的常用方式。

instance Eq Pos where -- 定义Pos类型的相等性比较，haskell中的instance关键字用于为特定类型实现类型类的功能，这里是为Pos类型实现Eq类型类的功能。和if语句类似，用于定义相等性的具体实现
  (==) (Pos c1 r1) (Pos c2 r2) = (c1 == c2) && (r1 == r2) -- 比较两个Pos对象的列和行是否相等，如果列和行都相等，则认为两个Pos对象相等。(==)是Eq类型类中定义的相等性比较操作符，用于比较两个值是否相等。

instance Eq Player where -- 定义Player类型的相等性比较
  (==) Top Top = True -- 如果两个Player对象都是Top，则认为它们相等，返回True。
  (==) Bottom Bottom = True -- 如果两个Player对象都是Bottom，则认为它们相等，返回True。
  (==) _ _ = False -- 如果一个是Top另一个是Bottom，则认为它们不相等，返回False。

instance Eq Cell where -- 定义Cell类型的相等性比较，Eq类型类用于定义相等性的具体实现
  (==) Empty Empty = True -- 如果两个Cell对象都是Empty，则认为它们相等，返回True。
  (==) Pawn Pawn = True -- 如果两个Cell对象都是Pawn，则认为它们相等，返回True。
  (==) Drone Drone = True -- 如果两个Cell对象都是Drone，则认为它们相等，返回True。
  (==) Queen Queen = True -- 如果两个Cell对象都是Queen，则认为它们相等，返回True。
  (==) _ _ = False -- 如果两个Cell对象类型不同，则认为它们不相等，返回False。
  
startingFEN :: String -- 标准起始位置的FEN字符串表示,startingFEN是一个字符串类型的常量，表示游戏的起始位置，采用FEN（Forsyth-Edwards Notation）格式。FEN是一种用于表示棋盘布局的标准符号系统，广泛应用于国际象棋和其他棋类游戏中。
startingFEN = "qqd1/qdp1/dpp1///1ppd/1pdq/1dqq" -- FEN字符串表示棋盘布局的起始位置，使用斜杠（/）分隔每一行，字符表示不同类型的棋子和空格。q表示Queen，d表示Drone，p表示Pawn，数字表示连续的空格数量，斜杠用于分隔行。qqd1表示第一行有两个Queen，一个Drone和一个空格，依此类推。

startingBoard :: [[Cell]] -- 标准起始位置的棋盘布局，startingBoard是一个二维列表，表示游戏的起始位置的棋盘布局。每个元素是一个Cell类型，表示棋盘上的单元格状态。
startingBoard = [ -- 标准起始位置的棋盘布局
  [Queen, Queen, Drone, Empty], -- 第一行
  [Queen, Drone, Pawn,  Empty], -- 第二行
  [Drone, Pawn,  Pawn,  Empty], -- 第三行
  [Empty, Empty, Empty, Empty], -- 第四行
  [Empty, Empty, Empty, Empty], -- 第五行
  [Empty, Pawn,  Pawn,  Drone], -- 第六行
  [Empty, Pawn,  Drone, Queen], -- 第七行
  [Empty, Drone, Queen, Queen]  -- 第八行
  ]

buildPos :: String -> Pos -- 将字符串转换为Pos对象，buildPos是一个函数，接受一个字符串参数，返回一个Pos类型的对象。该函数用于将表示位置的字符串转换为Pos对象。是haskell中的函数定义语法，表示定义一个名为buildPos的函数，接受一个字符串参数，返回一个Pos类型的对象。
buildPos (c:rStr) = Pos c (read rStr) -- 将字符串的第一个字符作为列（col），剩余部分转换为整数作为行（row），并构造一个Pos对象。read函数用于将字符串转换为整数类型。 (c:rStr)是Haskell中的模式匹配语法，表示将字符串分解为第一个字符c和剩余字符串rStr。Pos c (read rStr)表示创建一个Pos对象，其中c是列，read rStr将剩余字符串转换为整数作为行。
buildPos _ = error "Invalid position format" -- 如果字符串格式无效，抛出错误，error函数用于抛出运行时错误，并提供错误信息。

-- ##############################################################################
-- 辅助函数：分割字符串
spliTOn :: Char -> String -> [String] -- splitOn是一个函数，接受一个字符和一个字符串作为参数，返回一个字符串列表。该函数用于将字符串按照指定的分隔符字符进行分割，返回分割后的子字符串列表。
spliTOn _ [] = [""] -- 如果字符串为空，返回包含一个空字符串的列表。
spliTOn delim str = -- 否则，按照分隔符进行分割
    case break (== delim) str of -- 使用break函数找到第一个分隔符的位置，并将字符串分为两部分。
        (a, []) -> [a] -- 如果没有找到分隔符，返回整个字符串作为唯一的子字符串。
        (a, _:b) -> a : spliTOn delim b -- 如果找到了分隔符，将前半部分作为一个子字符串，递归处理后半部分。

-- ##############################################################################
-- ################## IMPLEMENT validateFEN :: String -> Bool ###################
-- ################## - 1 Functional Point                   ####################
-- ##############################################################################
-- KI-Referenz: Anfrage 1 (Implementierung von validateFEN)
validateFEN :: String -> Bool -- validateFEN是一个函数，接受一个字符串参数，返回一个布尔值。该函数用于验证给定的FEN字符串是否符合规范。
validateFEN fen =  -- 验证FEN字符串的有效性
    let rows = spliTOn '/' fen -- 将FEN字符串按照斜杠分割成行
        iSValidChar c = c `elem` "pdq1234" -- 检查字符是否是有效的棋子表示或数字
        
        roWLen :: String -> Int -- 计算行的长度，考虑数字表示的空格，rowLen是一个辅助函数，接受一个字符串参数，返回一个整数。该函数用于计算行的实际长度，考虑数字表示的空格数量。
        roWLen [] = 0 -- 如果字符串为空，长度为0
        roWLen (c:cs) -- 如果第一个字符是数字，则将其转换为整数并加上剩余字符串的长度,|是Haskell中的守卫语法，用于根据条件选择不同的表达式。和if语句类似，用于定义多分支条件。可以多个使用。像if-then-else语句一样。c:cs表示将字符串分解为第一个字符c和剩余字符串cs。
            | isDigit c = digitToInt c + roWLen cs -- 如果第一个字符是数字，则将其转换为整数并加上剩余字符串的长度
            | otherwise = 1 + roWLen cs -- 如果第一个字符是棋子表示，则长度加1并继续计算剩余字符串的长度
            
        iSRowValid r = (r == "") || (roWLen r == 4 && all iSValidChar r) -- 检查行是否有效，允许空行或长度为4且所有字符有效的行
        
    in length rows == 8 && all iSRowValid rows -- 检查总行数是否为8且所有行均有效

-- ##############################################################################
-- ################## IMPLEMENT buildBoard :: String -> Board ###################
-- ################## - 1 Functional Point                   ####################
-- ##############################################################################
-- KI-Referenz: Anfrage 2 (Implementierung von buildBoard mit expandRow)
buildBoard :: String -> Board -- buildBoard是一个函数，接受一个字符串参数，返回一个Board类型的对象。该函数用于将FEN字符串转换为棋盘布局。
buildBoard fen = map parsERow (spliTOn '/' fen) -- 将FEN字符串按照斜杠分割成行，并解析每一行为Cell列表
  where --where子句用于定义辅助函数parsERow,该函数用于解析单行FEN字符串并将其转换为Cell列表。
    -- 修正逻辑：先判断是否为空行，空行直接返回4个Empty
    parsERow :: String -> [Cell] -- parseRow是一个辅助函数，接受一个字符串参数，返回一个Cell类型的列表。该函数用于解析单行FEN字符串并将其转换为Cell列表。
    parsERow "" = [Empty, Empty, Empty, Empty] -- 如果行为空，返回4个Empty
    parsERow s  = expanDRow s -- 否则，调用expandRow函数解析行内容,s是单行FEN字符串

    -- 递归解析非空行
    expanDRow :: String -> [Cell] -- expandRow是一个辅助函数，接受一个字符串参数，返回一个Cell类型的列表。该函数用于递归解析单行FEN字符串，将字符转换为对应的Cell类型。
    expanDRow [] = [] -- 递归结束返回空列表，而不是4个Empty
    expanDRow (c:cs) -- 解析字符并递归处理剩余字符串,根据字符类型转换为对应的Cell类型,|是Haskell中的守卫语法，用于根据条件选择不同的表达式。和if语句类似，用于定义多分支条件。可以多个使用。像if-then-else语句一样。c:cs表示将字符串分解为第一个字符c和剩余字符串cs。cs是剩余字符串。
        | isDigit c = replicate (digitToInt c) Empty ++ expanDRow cs -- 如果字符是数字，则生成对应数量的Empty单元格，并递归处理剩余字符串
        | c == 'p'  = Pawn : expanDRow cs -- 如果字符是'p'，则表示Pawn单元格，并递归处理剩余字符串
        | c == 'd'  = Drone : expanDRow cs -- 如果字符是'd'，则表示Drone单元格，并递归处理剩余字符串
        | c == 'q'  = Queen : expanDRow cs -- 如果字符是'q'，则表示Queen单元格，并递归处理剩余字符串
        | otherwise = expanDRow cs -- 忽略无效字符，继续递归处理剩余字符串.otherwise表示所有其他情况，相当于else分支。

-- ##############################################################################
-- ################## IMPLEMENT buildFEN :: Board -> String   ###################
-- ################## - 1 Functional Point                   ####################
-- ##############################################################################
-- KI-Referenz: Anfrage 2 (Implementierung von buildFEN mit compressCells)
buildFEN :: Board -> String -- buildFEN是一个函数，接受一个Board类型的对象作为参数，返回一个字符串。该函数用于将棋盘布局转换为FEN字符串表示。
buildFEN board = joinWSlash (map compresSRow board) -- 将每一行压缩为FEN字符串，并使用斜杠连接行, joinWSlash用于将行列表连接为单个FEN字符串，compresRow用于压缩单行为FEN字符串。这些函数在where子句中定义。是haskell中的函数调用语法，表示调用函数并传递参数。是自己写的辅助函数，可以改变名字
  where --where子句用于定义辅助函数joinWSlash和compresRow，where和let类似，用于定义局部函数或变量
    joinWSlash :: [String] -> String -- joinWithSlash是一个辅助函数，接受一个字符串列表作为参数，返回一个字符串。该函数用于将字符串列表连接为单个字符串，使用斜杠作为分隔符。
    joinWSlash [] = "" -- 如果列表为空，返回空字符串
    joinWSlash [x] = x -- 如果列表只有一个元素，返回该元素
    joinWSlash (x:xs) = x ++ "/" ++ joinWSlash xs -- 递归连接字符串列表，使用斜杠作为分隔符

    compresSRow :: [Cell] -> String --compresRow是一个辅助函数，接受一个Cell类型的列表作为参数，返回一个字符串。该函数用于将单行的Cell列表压缩为FEN字符串表示。
    compresSRow cells -- 压缩单行的Cell列表为FEN字符串表示
        | all (== Empty) cells = "" -- 如果整行都是Empty，返回空字符串
        | otherwise = compresSCells cells -- 否则，调用compresCells函数进行压缩,compresCells用于实际的压缩逻辑

    compresSCells :: [Cell] -> String -- compresCells是一个辅助函数，接受一个Cell类型的列表作为参数，返回一个字符串。该函数用于将Cell列表压缩为FEN字符串表示。
    compresSCells [] = "" -- 递归结束返回空字符串
    compresSCells (Empty:xs) = counTEmpties 1 xs -- 如果第一个单元格是Empty，则计数连续的Empty单元格，并递归处理剩余列表
    compresSCells (Pawn:xs)  = 'p' : compresSCells xs -- 如果第一个单元格是Pawn，则添加'p'并递归处理剩余列表
    compresSCells (Drone:xs) = 'd' : compresSCells xs -- 如果第一个单元格是Drone，则添加'd'并递归处理剩余列表
    compresSCells (Queen:xs) = 'q' : compresSCells xs -- 如果第一个单元格是Queen，则添加'q'并递归处理剩余列表

    counTEmpties :: Int -> [Cell] -> String -- countEmpties是一个辅助函数，接受一个整数和一个Cell类型的列表作为参数，返回一个字符串。该函数用于计数连续的Empty单元格，并将计数转换为字符串表示。
    counTEmpties n [] = show n -- 如果列表为空，返回计数的字符串表示
    counTEmpties n (Empty:xs) = counTEmpties (n+1) xs -- 如果下一个单元格也是Empty，则计数加1并递归处理剩余列表
    counTEmpties n other = show n ++ compresSCells other -- 如果下一个单元格不是Empty，则返回计数的字符串表示，并继续压缩剩余列表