"""
This is our main driver file. It will be responsible for handling user input and displaying the current GameState object.   
"""
import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512 #400 is another good option
DIMENSION = 8 
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

'''
Initialize a global dictionaty of images. This will be called exactly once in the main.
'''
def loadImages():
    pieces = ['wP','wK','wN', 'wB','wQ','wR','bP','bK','bB','bR', 'bN', 'bQ']
    for piece in pieces:    
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #we can now access an image by saying 'IMAGES['wP']'

'''
The main driver for our code. This will handle user input and updating the graphics
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
    
    loadImages()
    running = True
    sqSelected = () #keeps track of the last click of the user (tupel: row, col)
    playerClicks = [] #two tuples
    
    while(running):
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                
            #mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
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
                    
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False      
                         
        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()
  
'''
Responsible for all the graphics within a current game state.
'''  
def drawGameState(screen, gs):
    drawBoard(screen) #draw the squares on the board
    #add in piece highlighting or move suggestions (later)
    drawPieces(screen, gs.board) #draw pieces on top of those squares
  
'''
Draw the squares on the board.
'''
def drawBoard(screen):
    white = (255,255,255)  # RGB for white
    black = (186,186,180)   # RGB for black
    colors = [white, black]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
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

  
        
if __name__ == "__main__":
    main()
