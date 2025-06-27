import random

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def findBestMove(gs, validMoves, depth):
    return 