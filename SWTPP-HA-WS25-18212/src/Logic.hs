module Logic where  -- do NOT CHANGE export of module

-- #############################################################################
-- HINWEIS ZUR KI-NUTZUNG:
-- Teile dieses Moduls wurden unter Zuhilfenahme eines LLM (Gemini) entwickelt.
-- Der vollständige Chatverlauf befindet sich in der Datei "Ki-Nutzung um Code zu verbessern.pdf".
-- #############################################################################

-- IMPORTS HERE
-- Note: Imports allowed that DO NOT REQUIRE TO CHANGE package.yaml, e.g.:
--       import Data.Char

import Board -- 导入Board模块，Board模块定义了游戏的基本数据类型和初始棋盘布局
import Data.Char(ord, chr) -- ord, chr是用来处理字符和其对应的整数ASCII码转换的函数，它们来自Data.Char模块
import Data.Maybe(mapMaybe) -- 用于处理Maybe类型的函数


data Move = Move {start :: Pos, target :: Pos} -- Move表示游戏中的一次移动，由起始位置（start）和目标位置（target）组成。start和target都是Pos类型，表示棋盘上的位置。

instance Show Move where -- 定义Move类型的字符串表示,Show类型类用于将值转换为字符串表示,这里是为Move类型实现Show类型类的功能。instance关键字用于为特定类型实现类型类的功能, 和if语句类似，用于定义字符串表示的具体实现
  show (Move (Pos startC startR) (Pos targetC targetR)) = [startC] ++ show startR ++ "-" ++ [targetC] ++ show targetR -- 将Move对象转换为字符串表示，格式为"cR-cR"，其中c表示列字符，R表示行数字。++是字符串连接操作符，用于将多个字符串连接在一起。

instance Eq Move where -- 定义Move类型的相等性比较,Eq类型类用于定义相等性的具体实现,这里是为Move类型实现Eq类型类的功能。instance关键字用于为特定类型实现类型类的功能, 和if语句类似，用于定义相等性的具体实现
  (==) (Move (Pos sc1 sr1) (Pos tc1 tr1)) (Move (Pos sc2 sr2) (Pos tc2 tr2)) = -- 比较两个Move对象的起始位置和目标位置是否相等，如果起始位置和目标位置都相等，则认为两个Move对象相等。
    sc1 == sc2 && sr1 == sr2 && tc1 == tc2 && tr1 == tr2 -- 比较起始位置的列和行以及目标位置的列和行是否相等。(==)是Eq类型类中定义的相等性比较操作符，用于比较两个值是否相等。  

buildMove :: String -> Maybe Move  -- 将字符串转换为Maybe Move对象，buildMove是一个函数，接受一个字符串参数，返回一个Maybe Move类型的对象。该函数用于将表示移动的字符串转换为Move对象，如果字符串格式无效，则返回Nothing。
buildMove "" = Nothing -- 如果字符串为空，返回Nothing，表示无效的移动
buildMove s = case break (=='-') s of -- 将字符串按照'-'分割为起始位置和目标位置
  (a, '-':b) -> Just (Move (buildPos a) (buildPos b)) -- 构造Move对象，并使用Just包装，表示有效的移动
  _ -> error "Invalid move format" -- 如果字符串格式无效，抛出错误，error函数用于抛出运行时错误，并提供错误信息。

-- =============================================================================
-- 辅助函数区
-- KI-Referenz: Anfrage 3 (Hilfsfunktionen für Koordinaten und Pfadlogik)
-- =============================================================================

poSToIndx :: Pos -> (Int, Int) -- 将Pos对象转换为索引元组，poSToIndx是一个函数，接受一个Pos类型的对象作为参数，返回一个包含两个整数的元组。该函数用于将Pos对象转换为棋盘的索引表示。
poSToIndx (Pos c r) = (ord c - ord 'a', r) -- 将列字符转换为整数索引（0到3），行保持不变。ord函数用于将字符转换为其对应的整数ASCII码。

idXToPosi :: (Int, Int) -> Pos -- 将索引元组转换为Pos对象，idXToPosi是一个函数，接受一个包含两个整数的元组作为参数，返回一个Pos类型的对象。该函数用于将棋盘的索引表示转换为Pos对象。
idXToPosi (c, r) = Pos (chr (ord 'a' + c)) r -- 将整数索引转换为列字符，行保持不变。chr函数用于将整数ASCII码转换为对应的字符。

iSValidIndx :: (Int, Int) -> Bool -- 检查索引元组是否在有效范围内，iSValidIndx是一个函数，接受一个包含两个整数的元组作为参数，返回一个布尔值。该函数用于检查给定的索引是否在棋盘的有效范围内。
iSValidIndx (c, r) = c >= 0 && c <= 3 && r >= 0 && r <= 7 -- 检查列索引是否在0到3之间，行索引是否在0到7之间。

geTCell :: Board -> Pos -> Cell -- 获取指定位置的单元格状态，geTCell是一个函数，接受一个Board类型的对象和一个Pos类型的对象作为参数，返回一个Cell类型的对象。该函数用于获取棋盘上指定位置的单元格状态。
geTCell board (Pos c r) = (board !! (7 - r)) !! (ord c - ord 'a') -- 根据Pos对象的列和行计算索引，并从棋盘中获取对应的单元格状态。!!是列表索引操作符，用于获取列表中指定位置的元素。

geTCellIdx :: Board -> (Int, Int) -> Cell -- 获取指定索引位置的单元格状态，geTCellIdx是一个函数，接受一个Board类型的对象和一个包含两个整数的元组作为参数，返回一个Cell类型的对象。该函数用于获取棋盘上指定索引位置的单元格状态。
geTCellIdx board (c, r) = (board !! (7 - r)) !! c -- 根据索引元组的列和行计算索引，并从棋盘中获取对应的单元格状态。

owneROf :: Int -> Player -- 根据行号确定该行所属的玩家，owneROf是一个函数，接受一个整数参数，返回一个Player类型的对象。该函数用于根据行号确定该行所属的玩家。
owneROf r = if r >= 4 then Top else Bottom -- 如果行号大于等于4，则该行属于Top玩家，否则属于Bottom玩家。

iSMyTurnAndPiece :: Board -> Player -> Pos -> Bool -- 检查指定位置的棋子是否属于当前玩家，iSMyTurnAndPiece是一个函数，接受一个Board类型的对象、一个Player类型的对象和一个Pos类型的对象作为参数，返回一个布尔值。该函数用于检查指定位置的棋子是否属于当前玩家。
iSMyTurnAndPiece board player pos@(Pos _ r) =  -- 检查指定位置的棋子是否属于当前玩家
    case geTCell board pos of -- 获取指定位置的单元格状态
        Empty -> False -- 如果单元格为空，返回False
        _     -> owneROf r == player -- 否则，检查该行所属的玩家是否与当前玩家相同

caNLand :: Board -> Player -> (Int, Int) -> Bool -- 检查指定索引位置是否可以落子，caNLand是一个函数，接受一个Board类型的对象、一个Player类型的对象和一个包含两个整数的元组作为参数，返回一个布尔值。该函数用于检查指定索引位置是否可以落子。
caNLand board myPlayer (tc, tr) = -- 检查指定索引位置是否可以落子
    let targetCell = geTCellIdx board (tc, tr) -- 获取目标位置的单元格状态
        targetZoneOwner = owneROf tr -- 获取目标位置所属的玩家
    in case targetCell of -- 根据目标位置的单元格状态判断是否可以落子
        Empty -> True -- 如果目标位置为空，返回True
        _     -> targetZoneOwner /= myPlayer -- 如果目标位置不为空，检查该位置所属的玩家是否与当前玩家不同

counTLin :: Board -> (Int, Int) -> (Int, Int) -> Int -- 计算指定方向上非空单元格的数量，counTLin是一个函数，接受一个Board类型的对象、一个包含两个整数的元组表示起始位置和一个包含两个整数的元组表示方向作为参数，返回一个整数。该函数用于计算指定方向上非空单元格的数量。
counTLin board (c, r) (dc, dr) -- 计算指定方向上非空单元格的数量
    | dc /= 0 = length [ x | x <- [0..3], geTCellIdx board (x, r) /= Empty ] -- 如果水平方向上移动，计算该行上非空单元格的数量
    | otherwise = length [ y | y <- [0..7], geTCellIdx board (c, y) /= Empty ] -- 否则，计算该列上非空单元格的数量

iSPathClean :: Board -> (Int, Int) -> (Int, Int) -> Int -> Bool -- 检查指定路径是否清空，iSPathClean是一个函数，接受一个Board类型的对象、一个包含两个整数的元组表示起始位置、一个包含两个整数的元组表示方向和一个整数表示步数作为参数，返回一个布尔值。该函数用于检查指定路径上是否所有单元格均为空。
iSPathClean board (c, r) (dc, dr) steps = -- 检查指定路径是否清空
    let path = [ (c + i*dc, r + i*dr) | i <- [1 .. steps - 1] ] -- 生成路径上的所有位置
    in all (\p -> geTCellIdx board p == Empty) path -- 检查路径上的所有位置是否均为空

iSIllegalUndo :: Player -> Pos -> Pos -> Maybe Move -> Bool -- 检查是否为非法的撤销移动，iSIllegalUndo是一个函数，接受一个Player类型的对象、两个Pos类型的对象表示当前移动的起始位置和目标位置以及一个Maybe Move类型的对象表示上一次移动作为参数，返回一个布尔值。该函数用于检查当前移动是否为非法的撤销移动。
iSIllegalUndo player currentStart currentEnd lastMove = -- 检查是否为非法的撤销移动
    case lastMove of -- 根据上一次移动进行判断
        Nothing -> False -- 如果没有上一次移动，返回False
        Just (Move lmStart lmEnd) -> -- 如果有上一次移动，检查当前移动是否与上一次移动相反
            if currentStart == lmEnd && currentEnd == lmStart -- 如果当前移动的起始位置等于上一次移动的目标位置且当前移动的目标位置等于上一次移动的起始位置
            then -- 检查起始位置和目标位置是否属于不同的玩家区域
                let startZone = owneROf (row lmStart) -- 获取上一次移动起始位置所属的玩家区域
                    endZone = owneROf (row lmEnd) -- 获取上一次移动目标位置所属的玩家区域
                in startZone /= endZone -- 如果起始位置和目标位置属于不同的玩家区域，返回True，否则返回False
            else False -- 如果当前移动与上一次移动不相反，返回False

-- ########################################################################################################
-- ################## pawnMoves :: Board -> Player -> Pos -> Maybe Move -> [Move]        ##################
-- ################## - 5 Functional Points                                              ##################
-- ########################################################################################################
-- KI-Referenz: Anfrage 3 (Implementierung von pawnMoves)
pawnMoves :: Board -> Player -> Pos -> Maybe Move -> [Move] -- 获取指定位置的兵棋子所有合法移动，pawnMoves是一个函数，接受一个Board类型的对象、一个Player类型的对象、一个Pos类型的对象表示兵棋子的位置以及一个Maybe Move类型的对象表示上一次移动作为参数，返回一个包含Move类型对象的列表。该函数用于获取指定位置的兵棋子所有合法移动。
pawnMoves board player p@(Pos c r) lastMove = -- 获取指定位置的兵棋子所有合法移动
    if not (iSMyTurnAndPiece board player p) || geTCell board p /= Pawn then [] else -- 如果指定位置的棋子不属于当前玩家或不是兵棋子，返回空列表
    let --let用于定义局部变量和函数,和where类似，用于定义局部函数或变量
        (ic, ir) = poSToIndx p -- 将Pos对象转换为索引元组
        dirs = [(1,1), (1,-1), (-1,1),(-1,-1)] -- 定义兵棋子的移动方向
        candidates = [ (ic+dc,ir+dr) | (dc,dr) <- dirs ] -- 计算所有可能的目标位置
        validTargets = filter (\t -> iSValidIndx t && caNLand board player t) candidates -- 过滤出有效的目标位置，即在有效范围内且可以落子的目标位置，
        moves = [ Move p (idXToPosi t) | t <-validTargets ] -- 构造所有合法的Move对象
    in filter (\m -> not (iSIllegalUndo player (start m) (target m) lastMove)) moves -- 过滤掉非法的撤销移动，返回最终的合法移动列表

-- #######################################################################################################
-- ################## droneMoves :: Board -> Player -> Pos -> Maybe Move -> [Move]      ##################
-- ################## - 5 Functional Points                                             ##################
-- #######################################################################################################
-- KI-Referenz: Anfrage 3 (Implementierung von droneMoves mit calCTarget)
droneMoves :: Board -> Player -> Pos -> Maybe Move -> [Move] -- 获取指定位置的无人机棋子所有合法移动，droneMoves是一个函数，接受一个Board类型的对象、一个Player类型的对象、一个Pos类型的对象表示无人机棋子的位置以及一个Maybe Move类型的对象表示上一次移动作为参数，返回一个包含Move类型对象的列表。该函数用于获取指定位置的无人机棋子所有合法移动。
droneMoves board player p@(Pos c r) lastMove = -- 获取指定位置的无人机棋子所有合法移动
    if not (iSMyTurnAndPiece board player p) || geTCell board p /= Drone then [] else -- 如果指定位置的棋子不属于当前玩家或不是无人机棋子，返回空列表
    let 
        (ic, ir) = poSToIndx p -- 将Pos对象转换为索引元组
        dirs = [(0,1), (0,-1), (1,0), (-1,0)] -- 定义无人机的移动方向
        
        calCTarget :: (Int, Int) -> Maybe Pos -- 计算指定方向上的合法目标位置，calCTarget是一个函数，接受一个包含两个整数的元组表示方向作为参数，返回一个Maybe Pos类型的对象。该函数用于计算指定方向上的合法目标位置。
        calCTarget (dc, dr) = -- 计算指定方向上的合法目标位置
            let steps = counTLin board (ic, ir) (dc, dr) -- 计算指定方向上非空单元格的数量
                targetIdx = (ic + steps*dc, ir + steps*dr) -- 计算目标位置的索引
            in if iSValidIndx targetIdx -- 目标位置在有效范围内
                  && iSPathClean board (ic, ir) (dc, dr) steps -- 路径是否干净
                  && caNLand board player targetIdx -- 是否可以落子
               then Just (idXToPosi targetIdx) -- 构造目标位置的Pos对象，并使用Just包装，表示有效的目标位置
               else Nothing -- 否则，返回Nothing，表示无效的目标位置
               
        validMoves = mapMaybe (\d -> fmap (Move p) (calCTarget d)) dirs -- 计算所有合法的Move对象，mapMaybe用于将函数应用于列表中的每个元素，并过滤掉返回Nothing的结果
    in filter (\m -> not (iSIllegalUndo player (start m) (target m) lastMove)) validMoves -- 过滤掉非法的撤销移动，返回最终的合法移动列表

-- #######################################################################################################
-- ################## queenMoves :: Board -> Player -> Pos -> Maybe Move -> [Move]      ##################
-- ################## - 3 Functional Points                                             ##################
-- #######################################################################################################
-- KI-Referenz: Anfrage 3 (Implementierung von queenMoves mit scanDir)
queenMoves :: Board -> Player -> Pos -> Maybe Move -> [Move] -- 获取指定位置的女王棋子所有合法移动，queenMoves是一个函数，接受一个Board类型的对象、一个Player类型的对象、一个Pos类型的对象表示女王棋子的位置以及一个Maybe Move类型的对象表示上一次移动作为参数，返回一个包含Move类型对象的列表。该函数用于获取指定位置的女王棋子所有合法移动。
queenMoves board player p@(Pos c r) lastMove = -- 获取指定位置的女王棋子所有合法移动
    if not (iSMyTurnAndPiece board player p) || geTCell board p /= Queen then [] else -- 如果指定位置的棋子不属于当前玩家或不是女王棋子，返回空列表
    let
        (ic, ir) = poSToIndx p -- 将Pos对象转换为索引元组
        dirs = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)] -- 定义女王的移动方向
        
        scaNDirec :: (Int, Int) -> [Pos] -- 扫描指定方向上的所有合法目标位置，scanDir是一个函数，接受一个包含两个整数的元组表示方向作为参数，返回一个包含Pos类型对象的列表。该函数用于扫描指定方向上的所有合法目标位置。
        scaNDirec (dc, dr) = go (ic+dc, ir+dr) -- 从当前位置开始，沿指定方向扫描
          where -- 定义辅助函数go，用于递归扫描目标位置
            go t@(tc, tr) -- 递归扫描目标位置
                | not (iSValidIndx t) = [] -- 如果目标位置不在有效范围内，返回空列表
                | caNLand board player t = -- 如果目标位置可以落子
                    if geTCellIdx board t == Empty -- 如果目标位置为空
                    then (idXToPosi t) : go (tc+dc, tr+dr) -- 将目标位置加入结果列表，并继续扫描下一个位置
                    else [(idXToPosi t)] -- 如果目标位置不为空，将目标位置加入结果列表，停止扫描
                | otherwise = [] -- 如果目标位置不能落子，返回空列表
                
        allTargets = concatMap scaNDirec dirs -- 扫描所有方向上的合法目标位置，并将结果合并为一个列表
        moves = map (Move p) allTargets -- 构造所有合法的Move对象
    in filter (\m -> not (iSIllegalUndo player (start m) (target m) lastMove)) moves -- 过滤掉非法的撤销移动，返回最终的合法移动列表

-- #######################################################################################################
-- ################## makeMove :: Board -> Move -> (Board -> Int)                       ##################
-- ################## - 3 Functional Points                                             ##################
-- #######################################################################################################
-- KI-Referenz: Anfrage 4 (makeMove Implementierung mit splitAt)
makeMove :: Board -> Move -> (Board, Int) -- 执行一次移动并返回更新后的棋盘和得分，makeMove是一个函数，接受一个Board类型的对象和一个Move类型的对象作为参数，返回一个包含更新后的Board类型对象和整数得分的元组。该函数用于执行一次移动，并计算得分。
makeMove board (Move startP targetP) = -- 执行一次移动并返回更新后的棋盘和得分
    let 
        sourceCell = geTCell board startP -- 获取起始位置的单元格状态
        targetCell = geTCell board targetP -- 获取目标位置的单元格状态
        
        score = case targetCell of -- 计算得分
            Pawn  -> 1
            Drone -> 2
            Queen -> 3
            Empty -> 0
            
        -- 更新棋盘：移除了死代码分支，直接匹配成功模式
        -- 因为前提是 startP 和 targetP 在 getCell 时已验证合法
        seTCell :: Board -> Pos -> Cell -> Board -- 设置指定位置的单元格状态，seTCell是一个函数，接受一个Board类型的对象、一个Pos类型的对象和一个Cell类型的对象作为参数，返回一个更新后的Board类型的对象。该函数用于设置棋盘上指定位置的单元格状态。
        seTCell b (Pos c r) val = -- 设置指定位置的单元格状态
            let rIdx = 7 - r -- 计算行索引
                cIdx = ord c - ord 'a' -- 计算列索引
                (top, targetRow:bot) = splitAt rIdx b -- 使用splitAt分割棋盘为上半部分、目标行和下半部分
                (left, _:right) = splitAt cIdx targetRow -- 使用splitAt分割目标行为左半部分、目标单元格和右半部分
            in top ++ [left ++ [val] ++ right] ++ bot -- 重新组合棋盘，更新目标单元格的状态
            
        boardStep1 = seTCell board startP Empty -- 将起始位置的单元格设置为空
        boardStep2 = seTCell boardStep1 targetP sourceCell -- 将目标位置的单元格设置为起始位置的单元格状态
        
    in (boardStep2, score) -- 返回更新后的棋盘和得分

-- #######################################################################################################
-- ################## playerWon :: Board -> Player -> Int -> Int -> Maybe Player        ##################
-- ################## - 3 Functional Points                                             ##################
-- #######################################################################################################
-- KI-Referenz: Anfrage 4 (playerWon)
playerWon :: Board -> Player -> Int -> Int -> Maybe Player -- 检查游戏是否结束并确定获胜玩家，playerWon是一个函数，接受一个Board类型的对象、一个Player类型的对象表示最后移动的玩家以及两个整数表示双方的得分作为参数，返回一个Maybe Player类型的对象。该函数用于检查游戏是否结束，并确定获胜玩家。
playerWon board lastMover scoreTop scoreBottom = -- 检查游戏是否结束并确定获胜玩家
    let -- 分割棋盘为上半部分和下半部分
        toPRows = take 4 board -- 获取棋盘的前4行（Top玩家区域）
        boTRows = drop 4 board -- 获取棋盘的后4行（Bottom玩家区域）
        iSZoneEmpty rows = all (all (== Empty)) rows -- 检查指定区域是否为空
        toPEmpty = iSZoneEmpty toPRows -- 检查Top玩家区域是否为空
        boTEmpty = iSZoneEmpty boTRows -- 检查Bottom玩家区域是否为空
        gameOver = toPEmpty || boTEmpty -- 游戏是否结束
    in 
        if not gameOver then Nothing -- 如果游戏未结束，返回Nothing
        else if scoreTop > scoreBottom then Just Top -- 如果Top玩家得分更高，返回Just Top
        else if scoreBottom > scoreTop then Just Bottom -- 如果Bottom玩家得分更高，返回Just Bottom
        else Just lastMover -- 如果得分相同，返回最后移动的玩家作为获胜者