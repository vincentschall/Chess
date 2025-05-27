"""
This class is responsible for storing all the information about the current state of a chess game. It is responsible 
for determining the valid moves at the current state. It will also keep a move log.
"""
class GameState():
    
    def __init__(self):
        #board is an 8x8 2d list, each element has 2 characters.
        #The first character represents the color of the piece, 'b'or 'w'
        #The second character represents the type of piece, 'K', 'Q', 'R', 'B', 'N', 'P'
        #"--" represents an empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.whiteToMove = True
        self.moveLog = []
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'K': self.getKingMoves, 'Q': self.getQueenMoves, 'B': self.getBishopMoves}
        
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        
        self.inCheck = False
        self.pins = []
        self.checks = []
        
        self.checkmate = False
        self.stalemate = False
        self.repetition = False
        
        self.enPassantPossible = () #coordinates where an en passant capture is possible

        self.whiteCastleKingside = True
        self.whiteCastleQueenside = True
        self.blackCastleKingside = True
        self.blackCastleQueenside = True
          
    '''
    takes a move as a parameter and executes it (excludes castling, en passant, promotion)    
    '''
    def makeMove(self, move):
        # store castling rights
        move.castleRightsBefore = {
            'whiteKingside': self.whiteCastleKingside,
            'whiteQueenside': self.whiteCastleQueenside,
            'blackKingside': self.blackCastleKingside,
            'blackQueenside': self.blackCastleQueenside
        }

        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.whiteToMove = not self.whiteToMove
        self.moveLog.append(move)
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
            
        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
            
        #en passant
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = '--' #capturing the pawn
            
        #update enPassantPossible
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.endRow + move.startRow) // 2, move.startCol) # // for integer division
            
        else:
            self.enPassantPossible = ()

        # update castling rights 
        if move.pieceMoved == 'wK':
            self.whiteCastleKingside = False
            self.whiteCastleQueenside = False
        elif move.pieceMoved == 'bK':
            self.blackCastleKingside = False
            self.blackCastleQueenside = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7 and move.startCol == 0:
                self.whiteCastleQueenside = False
            elif move.startRow == 7 and move.startCol == 7:
                self.whiteCastleKingside = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0 and move.startCol == 0:
                self.blackCastleQueenside = False
            elif move.startRow == 0 and move.startCol == 7:
                self.blackCastleKingside = False
        if move.pieceCaptured == 'wR':
            if move.endRow == 7 and move.endCol == 0:
                self.whiteCastleQueenside = False
            elif move.endRow == 7 and move.endCol == 7:
                self.whiteCastleKingside = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0 and move.endCol == 0:
                self.blackCastleQueenside = False
            elif move.endRow == 0 and move.endCol == 7:
                self.blackCastleKingside = False

        # castling 
        if move.isCastleMove:
            # kingside 
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'
                move.originalRookPos = (move.endRow, move.endCol + 1)
            else: # queenside 
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'
                move.originalRookPos = (move.endRow, move.endCol - 2)
        
    '''
    undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # Switch turn back
            
            # Restore king position if necessary
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # **Undo en passant move**
            if move.isEnPassantMove:
                # Reset the pawn that was captured (appears back on the correct row)
                capturedPawnRow = move.endRow + (1 if move.pieceMoved[0] == 'w' else -1)
                self.board[capturedPawnRow][move.endCol] = move.pieceCaptured
                self.board[move.endRow][move.endCol] = "--"  # Clear the en passant capture square
                self.enPassantPossible = (move.endRow, move.endCol)  # Restore en passant target square

            # **Undo a two-square pawn advance**
            elif move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = (move.endRow, move.endCol)  # Restore en passant square properly
            else:
                self.enPassantPossible = None  # Otherwise, clear en passant

            # restore castling rights 

            self.whiteCastleKingside = move.castleRightsBefore['whiteKingside']
            self.whiteCastleQueenside = move.castleRightsBefore['whiteQueenside']
            self.blackCastleKingside = move.castleRightsBefore['blackKingside']
            self.blackCastleQueenside = move.castleRightsBefore['blackQueenside']
            # Undo castling move
            if move.isCastleMove:
                # Move king back
                self.board[move.startRow][move.startCol] = move.pieceMoved
                # Move rook back to original position
                rookRow, rookCol = move.originalRookPos
                if move.endCol - move.startCol == 2:  # Kingside
                    self.board[rookRow][rookCol] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:  # Queenside
                    self.board[rookRow][rookCol] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"
                # Clear king's new position
                self.board[move.endRow][move.endCol] = "--"        
    '''
    All moves considering checks
    '''   
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]  
        if self.inCheck:
            moves = self.getAllPossibleMoves()
            # For each move, check if it leaves the king in check
            for i in range(len(moves)-1, -1, -1):
                self.makeMove(moves[i])
                self.whiteToMove = not self.whiteToMove # Switch turn to check for opponent's check 
                inCheck, _, _ = self.checkForPinsAndChecks()
                self.whiteToMove = not self.whiteToMove # Switch back 
                self.undoMove()
                if inCheck:
                    moves.remove(moves[i])
        else:
            moves = self.getAllPossibleMoves()

        return moves
        
    '''
    returns if the player is in check, a list of pins, and a list of checks
    '''  
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow, startCol = self.whiteKingLocation
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow, startCol = self.blackKingLocation

        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for j, d in enumerate(directions):
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        pieceType = endPiece[1]
                        #1) orthogonal rook
                        #2) diagonal bishop
                        #3) pawn
                        #4) every direction queen
                        #5) king
                        if (0 <= j <= 3 and pieceType == "R") or \
                           (4 <= j <= 7 and pieceType == "B") or \
                           (pieceType == "Q") or \
                           (i == 1 and pieceType == "P" and ((enemyColor == "w" and 6 <= j <= 7) or
                                                            (enemyColor == "b" and 4 <= j <= 5))) or \
                           (i == 1 and pieceType == "K"):
                            if possiblePin == ():  # No blocking piece
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # Piece is pinned
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break
        return inCheck, pins, checks
        
        
    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = [] 
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves
                        
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if(self.whiteToMove):
            if self.board[r-1][c] == "--":
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--":
                        moves.append(Move((r, c), (r-2, c), self.board))
            # Capture moves
            for dc in [-1, 1]:  # Left (-1) and right (+1) capture
                if 0 <= c + dc <= 7:  # Ensure within board
                    if self.board[r-1][c+dc][0] == 'b':  # Capturing an opponent's piece
                        if not piecePinned or pinDirection == (-1, dc):
                            moves.append(Move((r, c), (r-1, c+dc), self.board))
                
                # **En Passant**
                    if (r-1, c + dc) == self.enPassantPossible:  # Check if the square is en passant target
                        if not piecePinned or pinDirection == (-1, dc):
                            moves.append(Move((r, c), (r-1, c+dc), self.board, isEnPassantMove=True))
        else:
            if self.board[r+1][c] == "--":
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":
                        moves.append(Move((r, c), (r+2, c), self.board))
            # Capture moves
            for dc in [-1, 1]:  # Left (-1) and right (+1) capture
                if 0 <= c + dc <= 7:  # Ensure within board
                    if self.board[r+1][c+dc][0] == 'w':  # Capturing an opponent's piece
                        if not piecePinned or pinDirection == (1, dc):
                            moves.append(Move((r, c), (r+1, c+dc), self.board))
                
                    # **En Passant**
                    if (r+1, c + dc) == self.enPassantPossible:  # Check if the square is en passant target
                        if not piecePinned or pinDirection == (1, dc):
                            moves.append(Move((r, c), (r+1, c+dc), self.board, isEnPassantMove=True))

    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1) 
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, _, _ = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)   

         # Castling moves (only if not in check)
        if not self.inCheck:
            if self.whiteToMove:
                # White kingside (O-O)
                if self.whiteCastleKingside and \
                    self.board[7][5] == "--" and self.board[7][6] == "--":
                    # Check if squares f1/g1 are safe
                    if not self.squareUnderAttack(7, 5) and not self.squareUnderAttack(7, 6):
                        moves.append(Move((7, 4), (7, 6), self.board, isCastleMove=True))
            
                # White queenside (O-O-O)
                if (self.whiteCastleQueenside and 
                    self.board[7][1] == "--" and  # b1 must be empty (but can be under attack)
                    self.board[7][2] == "--" and  # c1 must be empty AND safe
                    self.board[7][3] == "--" and  # d1 must be empty AND safe
                    not self.squareUnderAttack(7, 2) and  # c1 not attacked
                    not self.squareUnderAttack(7, 3)):    # d1 not attacked
                    moves.append(Move((7, 4), (7, 2), self.board, isCastleMove=True))   
            else:
                # Black kingside (O-O)
                if self.blackCastleKingside and \
                    self.board[0][5] == "--" and self.board[0][6] == "--":
                    if not self.squareUnderAttack(0, 5) and not self.squareUnderAttack(0, 6):
                        moves.append(Move((0, 4), (0, 6), self.board, isCastleMove=True))
            
                # Black queenside (O-O-O)
                if (self.blackCastleQueenside and 
                    self.board[0][1] == "--" and  # b8 must be empty (but can be under attack)
                    self.board[0][2] == "--" and  # c8 must be empty AND safe
                    self.board[0][3] == "--" and  # d8 must be empty AND safe
                    not self.squareUnderAttack(0, 2) and  # c8 not attacked
                    not self.squareUnderAttack(0, 3)):    # d8 not attacked
                    moves.append(Move((0, 4), (0, 2), self.board, isCastleMove=True))  

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': #can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break
               
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        enemyColor = "b" if self.whiteToMove else "w" 
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break          
                   
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = [(-1, -1), (-1, 1), (1, 1), (1, -1)]  # Corrected directions
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # Inside board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # Capture enemy piece
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # Blocked by ally piece
                            break
                else:  # Out of bounds
                    break
  
    
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)
    
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
          
        directions = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)] #array of tupels (row, column)
        allyColor = "w" if self.whiteToMove else "b"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    '''
    Checks if a square is currently under attack
    '''
    def squareUnderAttack(self, r, c):
        enemyColor = 'b' if self.whiteToMove else 'w'
    
        # Check knight attacks
        knight_moves = [(-2,-1), (-2,1), (-1,-2), (-1,2),
                        (1,-2), (1,2), (2,-1), (2,1)]
        for m in knight_moves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if self.board[endRow][endCol] == enemyColor + 'N':
                    return True
    
        # Check straight lines (queen/rook)
        directions = [(-1,0), (0,-1), (1,0), (0,1)]
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    piece = self.board[endRow][endCol]
                    if piece[0] == enemyColor:
                        if piece[1] in ['Q', 'R'] or (i == 1 and piece[1] == 'K'):
                            return True
                        break  # Blocked by any piece
                    elif piece != "--":
                        break
    
        # Check diagonals (queen/bishop)
        directions = [(-1,-1), (-1,1), (1,-1), (1,1)]
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    piece = self.board[endRow][endCol]
                    if piece[0] == enemyColor:
                        if piece[1] in ['Q', 'B'] or (i == 1 and piece[1] == 'K'):
                            return True
                        break
                    elif piece != "--":
                        break
    
        # Check pawn attacks
        pawn_dir = -1 if self.whiteToMove else 1
        for dc in [-1, 1]:
            endRow = r + pawn_dir
            endCol = c + dc
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if self.board[endRow][endCol] == enemyColor + 'P':
                    return True
    
        return False            
 
class Move():
    
    #maps keys to values (key : value)
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0,}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7,}
    colsToFiles = {v: k for k, v in filesToCols.items()}
        
    def __init__(self, startSq, endSq, board, isEnPassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        
        # pawn promotoion
        self.isPawnPromotion = (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7)
        
        # en passant
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = 'bP' if self.pieceMoved == 'wP' else 'wP'
        
        self.isCastleMove = isCastleMove
        self.castleRightsBefore = None

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
                
    '''
    Overriding the equals method
    '''    
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
             
    def getChessNotation(self):
        text = ''
        if self.pieceMoved[1] == 'K' and abs(self.startCol - self.endCol) ==  2:
            text += '0-0-0' if self.endCol == 2 else '0-0'
            return text
        if self.pieceMoved[1] == 'P' and not self.isEnPassantMove:
            if self.pieceCaptured != '--':
                text += self.colsToFiles[self.startCol]
        else:
            text += self.pieceMoved[1]
        if self.pieceCaptured != '--':
            text += 'x'
        text += self.getRankFile(self.endRow, self.endCol)
        return text;

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
