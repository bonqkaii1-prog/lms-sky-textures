import chess, random, sys, json
FEN = "r2q1rk1/pp1nbppp/2p1p3/3pP3/3P4/2PB1N2/PP3PPP/R2QR1K1 w - - 0 13"
start = chess.Board(FEN)
VAL = {chess.PAWN:1, chess.KNIGHT:3, chess.BISHOP:3, chess.ROOK:5, chess.QUEEN:9, chess.KING:100}

def ok_rank(color, sq):
    r = chess.square_rank(sq)
    return r <= 4 if color == chess.WHITE else r >= 3

def safe(b, mv):
    """sensible-looking: no capture, no pawn move, no check, own half, not hanging to a cheaper attacker"""
    p = b.piece_at(mv.from_square)
    if p.piece_type == chess.PAWN or b.is_capture(mv) or b.gives_check(mv) or b.is_castling(mv): return False
    if not ok_rank(p.color, mv.to_square): return False
    b.push(mv)
    att = b.attackers(not p.color, mv.to_square)
    dfd = b.attackers(p.color, mv.to_square)
    bad = any(VAL[b.piece_at(s).piece_type] < VAL[p.piece_type] for s in att) or (att and not dfd)
    # don't leave anything else hanging either
    if not bad:
        for sq, q in b.piece_map().items():
            if q.color == p.color and q.piece_type != chess.KING:
                a = b.attackers(not p.color, sq)
                if a and (not b.attackers(p.color, sq) or any(VAL[b.piece_at(s).piece_type] < VAL[q.piece_type] for s in a)):
                    bad = True; break
    b.pop()
    return not bad

LAST = {}
def trip(b, color, rng):
    """a closed loop for one piece of `color`: 2-4 moves that bring it back home (each checked in isolation)"""
    pieces = [sq for sq, p in b.piece_map().items() if p.color == color and p.piece_type not in (chess.PAWN,)]
    W = {chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 2.5, chess.QUEEN: 1.2, chess.KING: 0.5}
    pieces = sorted(pieces, key=lambda q: -rng.random() ** (1.0 / W[b.piece_at(q).piece_type]))
    last = LAST.get(color)
    if last in pieces: pieces.remove(last); pieces.append(last)
    for sq in pieces:
        bb = b.copy(); bb.turn = color
        path = [sq]
        L = rng.choice([2, 2, 3, 3, 4])
        okp = True
        for i in range(L - 1):
            moves = [m for m in bb.legal_moves if m.from_square == path[-1] and safe(bb, m) and m.to_square not in path]
            if not moves: okp = False; break
            m = rng.choice(moves); bb.push(m); bb.turn = color; path.append(m.to_square)
        if not okp: continue
        back = chess.Move(path[-1], sq)
        if back in bb.legal_moves and safe(bb, back):
            LAST[color] = sq
            return [chess.Move(path[i], path[i+1]) for i in range(len(path) - 1)] + [back]
    return None

def attempt(seed, n_trips=7):
    rng = random.Random(seed); LAST.clear()
    b = start.copy()
    seq = []
    wq, bq = [], []
    for _ in range(400):
        if b.turn == chess.WHITE:
            if not wq:
                if len([m for m in seq if True]) >= 2 * 40: break
                t = trip(b, chess.WHITE, rng)
                if not t: return None
                wq = t
            mv = wq.pop(0)
        else:
            if not bq:
                t = trip(b, chess.BLACK, rng)
                if not t: return None
                bq = t
            mv = bq.pop(0)
        if mv not in b.legal_moves or not safe(b, mv): return None
        b.push(mv); seq.append(mv)
        if len(seq) >= 60 and not wq and not bq and b.board_fen() == start.board_fen() and b.turn == chess.WHITE:
            return seq
    return None

for seed in range(20000):
    s = attempt(seed)
    if s:
        b = start.copy(); san = []
        for m in s: san.append(b.san(m)); b.push(m)
        print("seed", seed, "plies", len(s))
        print(" ".join(san))
        json.dump({"fen": FEN, "moves": [m.uci() for m in s], "san": san}, open("loop.json", "w"))
        break
