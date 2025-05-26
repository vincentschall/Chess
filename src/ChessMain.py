"""
This is the main driver file. It is be responsible for handling user input and displaying the current GameState object.   
"""
import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512 #400 is another good option
DIMENSION = 8 
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
COLORS = [(255, 255, 255), (186, 186, 180)] # colors for white and black

'''
Initialize a global dictionaty of images. Called exactly once in main.
'''
def loadImages():
    pieces = ['wP','wK','wN', 'wB','wQ','wR','bP','bK','bB','bR', 'bN', 'bQ']
    for piece in pieces:    
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #we can now access an image by saying 'IMAGES['wP']'

'''
The main driver of the code. It handles user input and updating the graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    
    p.display.set_caption("Chess Engine")
    p.display.set_icon(p.image.load("images/bP.png"))
    
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made  
    animate = False #flag variable for when we should animate

    loadImages()
    running = True
    sqSelected = () #keeps track of the last click of the user (tupel: row, col)
    playerClicks = [] #two tuples
    
    gameOver = False

    while(running):
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                
            #mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() #x, y location of the mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE   
                    if sqSelected == (row, col):
                        sqSelected = () #deselect
                        playerClicks = []    
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) #append for both 1st and 2nd clicks
                    if len(playerClicks) == 2: #after 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                print(move.getChessNotation())
                                sqSelected = () #reset user clicks
                                playerClicks = []     
                        if not moveMade:
                            playerClicks = [sqSelected]
            #keyboard handlers          
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undoMove()    
                    moveMade = True
                    animate = False
                if e.key == p.K_r: # reset when 'r' is pressed 
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
                  
        drawGameState(screen, gs, validMoves, sqSelected, gs.moveLog[-1] if gs.moveLog else '')

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.stalemate:
            gameOver = True
            drawText(screen, 'Draw by stalemate')
        elif gs.repetition:
            gameOver = True
            drawText(screen, 'Draw by repetition')

        clock.tick(MAX_FPS)
        p.display.flip()

'''
Highlighting square selected and moves for piece selected 
'''
def highlightSquares(screen, gs, validMoves, squareSelected, lastMove):
    # Highlight last move 
    if lastMove != '':
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green'))
        screen.blit(s, (lastMove.startCol * SQ_SIZE, lastMove.startRow * SQ_SIZE))
        screen.blit(s, (lastMove.endCol * SQ_SIZE, lastMove.endRow * SQ_SIZE))
    
    # Highlight selected square and valid moves
    if squareSelected != ():
        r, c = squareSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('yellow'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            
            # highlight valid moves
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

'''
Responsible for all the graphics within a current game state.
'''  
def drawGameState(screen, gs, validMoves, squareSelected, lastMove):
    drawBoard(screen) #draw the squares on the board
    highlightSquares(screen, gs, validMoves, squareSelected, lastMove)
    drawPieces(screen, gs.board) #draw pieces on top of those squares
  
'''
Draw the squares on the board.
'''
def drawBoard(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = COLORS[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
    
'''
Draw the pieces pn the board using the current GameState.board
'''  
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # Check if there's a piece at this position
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))  

'''
animations and stuff
'''
def animateMove(move, screen, board, clock):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5 # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        color = COLORS[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2-textObject.get_width()/2, HEIGHT/2-textObject.get_height()/2)
    screen.blit(textObject)
    textObject = font.render(text, 0, p.Color("Gray"))
    screen,blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()
