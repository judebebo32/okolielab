"""Puzzle Corner (Rubik's cube hobby section): a landing page, seven tutorials and a request form.

Every algorithm printed on these pages is checked against the puzzle simulators in
puzzles.py when the site is built (see verify()), and the diagrams are drawn from the
same simulators, so a typo in a move sequence stops the build instead of reaching
the site.

The request form is a Netlify form (data-netlify="true"); submissions appear under
Forms in the Netlify dashboard for the okolielab project.
"""
import html, math
from puzzles import Cube, Pyraminx, cube_svg, pyra_svg, invert, _fit_svg, FACES as FACES_CUBE

E = html.escape

# ---------------- algorithms used on the pages ----------------
A = {
    "corner": "R U R' U'",
    "mid_right": "U R U' R' U' F' U F",
    "mid_left": "U' L' U L U F U' F'",
    "cross": "F R U R' U' F'",
    "edges": "R U R' U R U2 R' U",
    "corners_place": "U R U' L' U R' U' L",
    "corners_twist": "R' D' R D",
    "aperm": "R' F R' B2 R F' R' B2 R2",
    "pair": "Uw' R U R' F R' F' R Uw",
    "flip": "R U R' F R' F' R",
    "oll_parity": "r2 B2 U2 l U2 r' U2 r U2 F2 r F2 l' B2 r2",
    "pll_parity": "r2 U2 r2 Uw2 r2 u2",
    "pyr_cycle": "R U R' U R U R'",
    "pyr_flip": "R' L R L' U L' U' L",
}
PYR_INSERT = [  # (edge position, where the bottom colour faces, algorithm)
    ("front-right top edge", "right face", "L' U L U'"),
    ("front-right top edge", "front face", "U R U' R'"),
    ("front-left top edge", "left face", "R U' R' U"),
    ("front-left top edge", "front face", "L R' L' R"),
    ("back top edge", "right face", "R U R' U'"),
    ("back top edge", "left face", "L' U' L U"),
]

# ---------------- verification ----------------
def _ids(n):
    c = Cube(n); c.st = {k: k for k in c.st}; return c

def _touched(alg, n=3):
    c = _ids(n).apply(alg); return {k for k, v in c.st.items() if k != v}

def _home_of(alg, sticker, n=3):
    c = _ids(n).apply(alg); return [k for k, v in c.st.items() if v == sticker][0]

def verify():
    m = 2
    # 3x3 first layer / middle layer / last layer algorithms leave the right layers alone
    t = _touched(A["corner"]); assert {p for p, _ in t if p[1] == -m} == {(m, -m, m)}
    for k in ("mid_right", "mid_left"):
        assert not any(p[1] == -m for p, _ in _touched(A[k]))
    assert _home_of(A["mid_right"], ((0, m, m), (0, 0, 1))) == ((m, 0, m), (0, 0, 1))
    assert _home_of(A["mid_left"], ((0, m, m), (0, 0, 1))) == ((-m, 0, m), (0, 0, 1))
    for k in ("cross", "edges", "corners_place"):
        assert all(p[1] == m for p, _ in _touched(A[k])), k
    # yellow edges: fixes back and right edges, swaps front and left
    for src, dst in (((0, m, m), (-m, m, 0)), ((-m, m, 0), (0, m, m)), ((m, m, 0), (m, m, 0)), ((0, m, -m), (0, m, -m))):
        assert _home_of(A["edges"], (src, (0, 1, 0)))[0] == dst
    # corner 3-cycle keeps front-right-top corner in place
    assert _home_of(A["corners_place"], ((m, m, m), (0, 1, 0))) == ((m, m, m), (0, 1, 0))
    # R' D' R D has order 6 (twice or four times twists a corner and restores the rest)
    c = Cube(3)
    for _ in range(6): c.apply(A["corners_twist"])
    assert c.solved()
    # 2x2 A-perm keeps the bottom layer
    a, b = Cube(2), Cube(2).apply(A["aperm"])
    assert all(a.st[k] == b.st[k] for k in a.st if k[0][1] == -1)
    # 4x4: parity algorithms only affect the stated edges; pairing keeps centres
    def wrong(alg, n=4):
        s, x = Cube(n), Cube(n).apply(alg)
        return {p for (p, nv) in s.st if s.st[(p, nv)] != x.st[(p, nv)]}
    assert wrong(A["oll_parity"]) == {(-1, 3, 3), (1, 3, 3)}
    assert wrong(A["pll_parity"]) == {(-1, 3, 3), (1, 3, 3), (-1, 3, -3), (1, 3, -3)}
    assert _centres_ok(Cube(4).apply(A["pair"]))
    setup = _ids(4).apply(invert(A["pair"]))   # partners in the upper middle row at front-left and front-right, same colour on the front
    assert setup.st[((-3, 1, 3), (0, 0, 1))] == ((3, -1, 3), (0, 0, 1)) and setup.st[((3, 1, 3), (0, 0, 1))] == ((3, 1, 3), (0, 0, 1))
    assert setup.st[((3, -1, 3), (0, 0, 1))][0] == (-3, 1, 3)
    fl = _ids(4).apply(A["flip"])              # flips the front-right edge in place
    assert fl.st[((3, 1, 3), (0, 0, 1))] == ((3, -1, 3), (1, 0, 0))
    # Pyraminx: last-layer algorithms leave everything but the three top edges solved
    for k in ("pyr_cycle", "pyr_flip"):
        p0, p1 = Pyraminx(), Pyraminx().apply(A[k])
        for key in p0.st:
            if p0.st[key][1] != p1.st[key][1]:
                pos = p0.st[key][0]
                assert p0.piece_kind(pos) == "edge" and _pyr_edge(p0, pos) in ("LU", "RU", "BU"), k
    # Pyraminx edge inserts: each brings the front-bottom edge home without touching the other bottom edges
    names = {"front-right top edge": "RU", "front-left top edge": "LU", "back top edge": "BU"}
    faces = {"right face": "Rf", "left face": "Lf", "front face": "F"}
    P = Pyraminx()
    d_sticker = [k for k, (p, col) in P.st.items() if col == "D" and P.piece_kind(p) == "edge" and _pyr_edge(P, p) == "LR"][0]
    for where, face, alg in PYR_INSERT:
        q = Pyraminx(); q.st = {k: (v[0], k) for k, v in q.st.items()}; q.apply(invert(alg))
        pos = [p for k, (p, home) in q.st.items() if home == d_sticker][0]
        assert _pyr_edge(P, pos) == names[where] and P.face_of(pos) == faces[face], (alg, _pyr_edge(P, pos), P.face_of(pos))
        p0, p1 = Pyraminx(), Pyraminx().apply(alg)
        for key in p0.st:
            if p0.st[key][1] != p1.st[key][1]:
                pos = p0.st[key][0]
                assert p0.piece_kind(pos) == "edge" and _pyr_edge(p0, pos) not in ("BL", "BR"), alg
    return True

def _is_center(p, n):
    m = n - 1; return sum(1 for v in p if abs(v) == m) == 1

def _centres_ok(c):
    faces = {}
    for (p, nv), col in c.st.items():
        if _is_center(p, c.n): faces.setdefault(nv, set()).add(col)
    return all(len(v) == 1 for v in faces.values())

def _pyr_edge(P, p):
    ds = sorted((sum(p[i] * P.V[v][i] for i in range(3)), v) for v in "ULRB")
    return "".join(sorted(ds[-1][1] + ds[-2][1]))

# ---------------- diagrams ----------------
def _masked(c, keep):
    d = c.copy()
    for k in d.st:
        if not keep(*k): d.st[k] = "X"
    return d

def _kind(p, n):
    m = n - 1; k = sum(1 for v in p if abs(v) == m)
    return {1: "center", 2: "edge", 3: "corner"}[k]

def svg_3x3(stage, size=170):
    n, m = 3, 2
    if stage == "scrambled":
        return cube_svg(Cube(3).apply("R U F' L2 D B' R2 U' F D2 L U2 B R'"), size=size, label="A scrambled 3x3 cube")
    if stage == "cross":
        c = Cube(3)
        return cube_svg(_masked(c, lambda p, nv: _kind(p, n) == "center" or (p[1] == m and _kind(p, n) == "edge")), size=size, label="White cross with matching side colours")
    c = Cube(3).apply("z2")             # white on the bottom, yellow on top
    keep = {
        "layer1": lambda p, nv: p[1] == -m or _kind(p, n) == "center",
        "layer2": lambda p, nv: p[1] <= 0 or _kind(p, n) == "center",
        "ycross": lambda p, nv: p[1] <= 0 or _kind(p, n) == "center" or (p[1] == m and _kind(p, n) == "edge" and nv == (0, 1, 0)),
        "yedges": lambda p, nv: p[1] <= 0 or _kind(p, n) != "corner",
    }
    if stage in keep:
        return cube_svg(_masked(c, keep[stage]), size=size, label=stage)
    if stage == "ycorners":           # corners in place, two still twisted
        c.apply(invert("R' D' R D R' D' R D U R' D' R D R' D' R D R' D' R D R' D' R D U'"))
        return cube_svg(c, size=size, label="Yellow corners in place but two are twisted")
    return cube_svg(c, size=size, label="Solved 3x3 cube")

def svg_2x2(stage, size=150):
    n, m = 2, 1
    if stage == "scrambled": return cube_svg(Cube(2).apply("R U2 F' R' U F2 R2 U'"), size=size, label="A scrambled 2x2 cube")
    c = Cube(2).apply("z2")
    if stage == "layer1": return cube_svg(_masked(c, lambda p, nv: p[1] == -m), size=size, label="First layer solved")
    if stage == "top":
        c.apply("R' F R' B2 R F' R' B2 R2")
        return cube_svg(c, size=size, label="Top face yellow; corners not yet in place")
    if stage == "top_grey": return cube_svg(_masked(c, lambda p, nv: p[1] == -m or nv == (0, 1, 0)), size=size, label="Yellow top face")
    return cube_svg(c, size=size, label="Solved 2x2 cube")

def svg_4x4(stage, size=170):
    n = 4
    if stage == "scrambled": return cube_svg(Cube(4).apply("Rw U2 F' r L2 D Uw' B R2 u F' D2 L Fw U2 B"), size=size, label="A scrambled 4x4 cube")
    c = Cube(4).apply("z2")
    if stage == "centers": return cube_svg(_masked(c, lambda p, nv: _kind(p, n) == "center"), size=size, label="All six centres solved")
    if stage == "edges": return cube_svg(_masked(c, lambda p, nv: _kind(p, n) != "corner"), size=size, label="Centres and paired edges")
    if stage == "oll": return cube_svg(c.apply(invert(A["oll_parity"])), size=size, label="OLL parity: one flipped edge pair")
    if stage == "pll": return cube_svg(c.apply(A["pll_parity"]), size=size, label="PLL parity: two edges swapped")
    return cube_svg(c, size=size, label="Solved 4x4 cube")

def svg_pyra(stage, size=170):
    P = Pyraminx()
    if stage == "scrambled": return pyra_svg(Pyraminx().apply("R B' U L R' B U' L' B R U' B' L u r' b"), size=size, label="A scrambled Pyraminx")
    keep = {
        "tips": lambda q, p, col: q.piece_kind(p) == "tip",
        "centers": lambda q, p, col: q.piece_kind(p) != "edge",
        "bottom": lambda q, p, col: q.piece_kind(p) != "edge" or _pyr_edge(q, p) in ("LR", "BL", "BR"),
    }
    if stage in keep:
        return pyra_svg(P, mask=lambda q, p, col: col if keep[stage](q, p, col) else "X", size=size, label=stage)
    if stage == "flip": return pyra_svg(P.apply(A["pyr_flip"]), size=size, label="Two flipped top edges")
    return pyra_svg(P, size=size, label="Solved Pyraminx")

def svg_mirror(size=170, scrambled=False):
    """Isometric mirror cube: one colour, uneven cuts. Scrambled view staggers the pieces."""
    cuts = {"x": [0, .30, .72, 1], "y": [0, .22, .58, 1], "z": [0, .40, .78, 1]}
    s = size * .36; cx, cy = size / 2, size * .53
    ex = (math.cos(math.radians(30)) * s, math.sin(math.radians(30)) * s)
    ez = (-math.cos(math.radians(30)) * s, math.sin(math.radians(30)) * s)
    def pt(x, y, z):  # unit cube coordinates centred at .5
        x -= .5; y -= .5; z -= .5
        return (cx + x * ex[0] * 1.6 + z * ez[0] * 1.6, cy + x * ex[1] * 1.6 + z * ez[1] * 1.6 - y * s * 1.6)
    shade = {"U": "url(#mU)", "F": "url(#mF)", "R": "url(#mR)"}
    polys = []
    def poly(pts, f, dy=0):
        polys.append(f'<polygon points="{" ".join(f"{a:.1f},{b - dy:.1f}" for a, b in pts)}" fill="{shade[f]}" stroke="#5b6470" stroke-width="1.6" stroke-linejoin="round"/>')
    X, Y, Z = cuts["x"], cuts["y"], cuts["z"]
    lift = [0, 0, 0]
    if scrambled: lift = [0, size * .035, -size * .03]
    for i in range(3):
        for j in range(3):   # U face: x by z
            poly([pt(X[i], 1, Z[j]), pt(X[i + 1], 1, Z[j]), pt(X[i + 1], 1, Z[j + 1]), pt(X[i], 1, Z[j + 1])], "U", lift[j] if scrambled else 0)
            poly([pt(X[i], Y[j + 1], 1), pt(X[i + 1], Y[j + 1], 1), pt(X[i + 1], Y[j], 1), pt(X[i], Y[j], 1)], "F")
            poly([pt(1, Y[j + 1], Z[i]), pt(1, Y[j + 1], Z[i + 1]), pt(1, Y[j], Z[i + 1]), pt(1, Y[j], Z[i])], "R")
    defs = ('<defs><linearGradient id="mU" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4f6f8"/><stop offset="1" stop-color="#c3c9d1"/></linearGradient>'
            '<linearGradient id="mF" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d9dee4"/><stop offset="1" stop-color="#9aa3ae"/></linearGradient>'
            '<linearGradient id="mR" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#b8c0ca"/><stop offset="1" stop-color="#7d8794"/></linearGradient></defs>')
    return _fit_svg(polys, size, "Mirror cube", defs)

# ---------------- Megaminx and Helicopter cube ----------------
from puzzles import make_megaminx, make_helicopter, mega_svg, heli_svg

MEGA = {
    "s2": "DR F DR' F'",            # white corner from the spot above its slot (F, DL, DR) into (D, DL, DR)
    "s3_right": "F DR F' DR' F' DL' F DL",
    "s3_left": "F' DL' F DL F DR F' DR'",
    "s4_corner": "L F L' F'",       # corner from (F, L, DL) into (F, DL, DR)
    "s4_dl_a": "F L' F' U F L F' U'",      # edge at top-front, F colour on top
    "s4_dl_b": "F2 U' F2' U' F2 U F2' U",  # edge at top-front, F colour on the front
    "s4_dr_a": "F' R F U' F' R' F U",
    "s4_dr_b": "F2' U F2 U F2' U' F2 U'",
    "lift": "F U F'",
    "s5_corner": "R U R' U'",
    "s5_right": "U R U' R' U' F' U F",
    "s5_left": "U' L' U L U F U' F'",
    "eo": "F R U R' U' F'",
    "ep": "R U R' U R U2' R'",
    "cp": "U R U' BL' U R' U' BL",
    "co": "R' DR' R DR",
}
HELI = {
    "twist_a": "UR UL UB UL UR UF",   # front-right and front-left corners: top stickers move down to the front
    "twist_b": "UF UR UL UB UL UR",   # the reverse: top stickers move to the sides
    "cycle": "FR UF FR UR FR UF FR UR",
}
_LOW = {"DR", "DBR", "DB", "DBL", "DL"}; _UPP = {"F", "R", "BR", "BL", "L"}

def _mega():
    if not hasattr(_mega, "g"): _mega.g = make_megaminx()
    return _mega.g.copy()

def _mstage(fs):
    fs = set(fs)
    if "D" in fs: return 1 if len(fs) <= 2 else 2
    if "U" in fs: return 9
    if len(fs) == 1: return 0
    l = len(fs & _LOW)
    if len(fs) == 2: return 3 if l == 2 else (4 if l == 1 else 5)
    return 4 if l == 2 else 5

def _mfoot(alg):
    g = _mega(); g.state = list(range(len(g.pts))); g.apply(alg)
    return {g.piece_faces[i] for i in range(len(g.pts)) if g.state[i] != i}

def _minv(alg):
    """Inverse of a Megaminx algorithm (on a Megaminx, X2 and X2' are different turns)."""
    return " ".join(m[:-1] if m.endswith("'") else m + "'" for m in reversed(alg.split()))

def _mloc(alg, target):
    """Where the piece with faces `target` sits after applying the inverse of alg to a solved puzzle: {colour: face it shows on}."""
    g = _mega(); g.state = list(range(len(g.pts))); g.apply(_minv(alg))
    t = [i for i in range(len(g.pts)) if g.piece_faces[i] == target]
    return {g.home[g.state[p]]: g.home[p] for p in range(len(g.pts)) if g.state[p] in t}

def verify_mega_heli():
    g = _mega(); f = frozenset
    st = {p: _mstage(p) for p in set(g.piece_faces)}
    def only(alg, allowed, upto):
        bad = [p for p in _mfoot(alg) if st[p] <= upto and p not in allowed]
        assert not bad, (alg, bad)
    only(MEGA["s2"], {f({"D", "DL", "DR"})}, 2)
    assert _mloc(MEGA["s2"], f({"D", "DL", "DR"})) == {"DR": "F", "D": "DR", "DL": "DL"}
    only(MEGA["s3_right"], {f({"DL", "DR"})}, 3); only(MEGA["s3_left"], {f({"DL", "DR"})}, 3)
    assert _mloc(MEGA["s3_right"], f({"DL", "DR"})) == {"DR": "F", "DL": "DL"}
    assert _mloc(MEGA["s3_left"], f({"DL", "DR"})) == {"DL": "F", "DR": "DR"}
    slot = {f({"F", "DL", "DR"}), f({"F", "DL"}), f({"F", "DR"})}
    only(MEGA["s4_corner"], slot, 4)
    assert set(_mloc(MEGA["s4_corner"], f({"F", "DL", "DR"})).values()) == {"F", "L", "DL"}
    for k, tgt, want in (("s4_dl_a", {"F", "DL"}, {"DL": "F", "F": "U"}), ("s4_dl_b", {"F", "DL"}, {"F": "F", "DL": "U"}),
                         ("s4_dr_a", {"F", "DR"}, {"DR": "F", "F": "U"}), ("s4_dr_b", {"F", "DR"}, {"F": "F", "DR": "U"})):
        only(MEGA[k], {f(tgt)}, 4); assert _mloc(MEGA[k], f(tgt)) == want, k
    only(MEGA["lift"], set(), 4)
    only(MEGA["s5_corner"], {f({"F", "R", "DR"}), f({"F", "R"})}, 5)
    assert set(_mloc(MEGA["s5_corner"], f({"F", "R", "DR"})).values()) == {"U", "F", "R"}
    only(MEGA["s5_right"], {f({"F", "R"})}, 5); only(MEGA["s5_left"], {f({"F", "L"})}, 5)
    assert _mloc(MEGA["s5_right"], f({"F", "R"})) == {"F": "F", "R": "U"}
    for k in ("eo", "ep", "cp"): only(MEGA[k], set(), 5)
    c = _mega()
    for _ in range(6): c.apply(MEGA["co"])
    assert c.solved()
    # Helicopter: twist algorithms keep every corner in place; the cycle moves exactly three centres
    h = make_helicopter(); n = len(h.pts)
    corner = [i for i, p in enumerate(h.pts) if abs(sum(abs(x) for x in p) - 1 - 4 / 3) < 1e-6]
    for k in ("twist_a", "twist_b"):
        x = h.copy(); x.state = list(range(n)); x.apply(HELI[k])
        key = lambda i: tuple(1 if v > 0 else -1 for v in h.pts[i])
        assert all(key(x.state[i]) == key(i) for i in corner)
        assert {key(i) for i in corner if x.state[i] != i} == {(1, 1, 1), (-1, 1, 1)}
    x = h.copy(); x.state = list(range(n)); x.apply(HELI["cycle"])
    moved = [i for i in range(n) if x.state[i] != i]
    assert len(moved) == 3 and not set(moved) & set(corner)
    return True

def _mmask(upto, extra=None):
    g = _mega()
    return lambda k: _mstage(g.piece_faces[k]) <= upto or (extra is not None and extra(g, k))

def svg_mega(stage, size=190):
    g = _mega()
    if stage == "scrambled":
        return mega_svg(g.apply("R U F' L BR U2 R' DR F BL' U L2 DBR R F'"), size=size, label="A scrambled Megaminx")
    if stage in ("s1", "s2", "s3"):
        up = {"s1": 1, "s2": 2, "s3": 3}[stage]
        return mega_svg(g, view="bottom", mask=_mmask(up), size=size, label=stage)
    if stage in ("s4", "s5"):
        return mega_svg(g, mask=_mmask(int(stage[1])), size=size, label=stage)
    if stage == "star":
        return mega_svg(g, mask=_mmask(5, lambda q, k: len(q.piece_faces[k]) == 2 and q.home[k] == "U"), size=size, label="Top star")
    if stage == "ep":
        return mega_svg(g, mask=_mmask(5, lambda q, k: len(q.piece_faces[k]) == 2), size=size, label="Top edges solved")
    if stage == "cp":
        x = MEGA["co"] + " "; twist = (x * 2) + "U " + (x * 4) + "U'"
        return mega_svg(g.apply(twist), size=size, label="Corners in place, two twisted")
    return mega_svg(g, size=size, label="Solved Megaminx")

def _heli_idx(face, a, b, centre=True):
    """Sticker index on face with signs a, b for the two other axes (in x, y, z order)."""
    h = make_helicopter(); nv = FACES_CUBE[face]; ax = [i for i in range(3) if nv[i]][0]; o = [i for i in range(3) if i != ax]
    t = 1 / 3 if centre else 2 / 3
    for k, p in enumerate(h.pts):
        if abs(p[ax] - nv[ax]) < 1e-9 and abs(p[o[0]] - a * t) < 1e-9 and abs(p[o[1]] - b * t) < 1e-9: return k

def svg_heli(stage, size=170):
    h = make_helicopter()
    corner = [i for i, p in enumerate(h.pts) if abs(sum(abs(x) for x in p) - 1 - 4 / 3) < 1e-6]
    def grey_centres(x):
        for i in range(len(x.pts)):
            if i not in corner: x.state[i] = "X"
        return x
    if stage == "scrambled": return heli_svg(h.apply("UF FR UL DB UR FL DF UB BR DL UF FR"), size=size, label="A scrambled Helicopter cube")
    if stage == "corners": return heli_svg(grey_centres(h), size=size, label="Corners solved")
    if stage == "twist": return heli_svg(grey_centres(h.apply(HELI["twist_a"])), size=size, label="The two front corners twisted")
    if stage == "cycle":
        a = _heli_idx("F", -1, 1); b = _heli_idx("U", 1, 1); c = _heli_idx("R", 1, -1)
        return heli_svg(h, size=size, label="The three centres the algorithm cycles", marks={a: "1", b: "2", c: "3"})
    return heli_svg(h, size=size, label="Solved Helicopter cube")

# ---------------- page pieces ----------------
def alg(s):
    return f'<code class="alg">{E(s)}</code>'

def step(num, title, fig, body, cap=""):
    figure = f'<figure class="cube-fig">{fig}<figcaption>{cap}</figcaption></figure>' if fig else ""
    return f'<article class="cube-step"><div class="cube-step-text"><span class="cube-num">Step {num}</span><h3>{title}</h3>{body}</div>{figure}</article>'

TUTORIALS = [
    ("rubiks-cube-2x2.html", "2×2 cube", "The pocket cube. Corners only, three steps. The best place to start.", lambda: svg_2x2("scrambled", 150), "Beginner"),
    ("rubiks-cube-3x3.html", "3×3 cube", "The classic Rubik's cube, solved layer by layer in seven steps.", lambda: svg_3x3("scrambled", 150), "Beginner"),
    ("rubiks-cube-pyraminx.html", "Triangle (Pyraminx)", "The pyramid-shaped puzzle. Quick to learn with four short steps.", lambda: svg_pyra("scrambled", 150), "Beginner"),
    ("rubiks-cube-mirror.html", "Mirror cube", "A 3×3 where every piece has a different size and all faces look the same.", lambda: svg_mirror(150), "Intermediate"),
    ("rubiks-cube-4x4.html", "4×4 cube", "The Rubik's Revenge. Reduce it to a 3×3, then handle parity.", lambda: svg_4x4("scrambled", 150), "Intermediate"),
    ("rubiks-cube-megaminx.html", "Megaminx", "A 12-sided dodecahedron. Solved like a 3×3, layer by layer, with more layers.", lambda: svg_mega("scrambled", 160), "Intermediate"),
    ("rubiks-cube-helicopter.html", "Helicopter cube", "Turns around its edges and can jumble into non-cube shapes. Corners first, then centres.", lambda: svg_heli("scrambled", 150), "Advanced"),
]

def subnav(current):
    items = [("rubiks-cube.html", "Overview")] + [(h, t) for h, t, *_ in TUTORIALS] + [("rubiks-cube-request.html", "Request a tutorial or cube")]
    return '<nav class="chips cube-subnav" aria-label="Puzzle Corner pages">' + "".join(
        f'<a class="chip{" on" if h == current else ""}" href="{h}"{" aria-current=\"page\"" if h == current else ""}>{t}</a>' for h, t in items) + "</nav>"

def cta():
    return ('<section style="padding-top:0"><div class="wrap"><div class="join"><div><h2>Want a hand?</h2><p>Dr. Okolie offers personalised tutorials, and can send you a cube to practise on. '
            'Tell us which puzzle you are learning and where you are stuck.</p></div><div class="btns"><a class="btn pri" href="rubiks-cube-request.html">Request a tutorial or cube</a>'
            '<a class="btn" href="rubiks-cube.html">All tutorials</a></div></div></div></section>')

def notation_cube(big=False):
    rows = [("R", "Right face clockwise"), ("L", "Left face clockwise"), ("U", "Up (top) face clockwise"), ("D", "Down (bottom) face clockwise"),
            ("F", "Front face clockwise"), ("B", "Back face clockwise"), ("R'", "A prime (') means counter-clockwise"), ("R2", "A 2 means a half turn (180°)")]
    if big:
        rows += [("Rw", "Wide turn: the right face and the slice next to it together"), ("r", "Only the inner slice next to the right face"),
                 ("Uw, u", "Same idea for the top: two layers, or the inner slice only"), ("x", "Turn the whole cube the same way as R")]
    trs = "".join(f"<tr><td>{alg(a)}</td><td>{d}</td></tr>" for a, d in rows)
    return (f'<div class="cube-notation"><div><span class="tag">Notation</span><h2>Reading the moves</h2><p class="muted">Each letter is one turn of one face. '
            '"Clockwise" always means clockwise as if you were looking straight at that face. Hold the cube the way each step says, and keep it in that position while you do a sequence.</p></div>'
            f'<table class="cube-table"><tbody>{trs}</tbody></table></div>')

def tutorial_page(fname, h1, lede, body):
    return (f'<div class="page-hero cube-hero"><div class="wrap"><span class="tag">Puzzle Corner</span><h1>{h1}</h1><p>{lede}</p>{subnav(fname)}</div></div>' + body + cta())

def video_block(src, poster, title, caption):
    """Short clip of Dr. Okolie solving the puzzle, with background music. Plays muted in a loop; tap to unmute."""
    return (f'<section><div class="wrap cube-video"><div class="cv-text"><span class="tag">Watch</span><h2>{title}</h2><p>{caption}</p>'
            '<p class="muted" style="font-size:14px">The clip plays silently; tap the speaker icon to hear the music. Background music: an original track made for this site.</p></div>'
            f'<video src="img/{src}" poster="img/{poster}" controls autoplay muted loop playsinline preload="metadata"></video></div></section>')

# ---------------- pages ----------------
def page_landing():
    cards = "".join(
        f'<a class="card cube-card" href="{h}"><div class="cube-card-fig">{fig()}</div><div class="b"><span class="tag">{lvl}</span><h3>{t}</h3><p>{d}</p><span class="more">Start the tutorial →</span></div></a>'
        for h, t, d, fig, lvl in TUTORIALS)
    return f"""<div class="page-hero cube-hero"><div class="wrap cube-hero-grid"><div><span class="tag">Beyond the lab</span><h1>Dr. Okolie's puzzle corner</h1>
<p>Solving Rubik's cubes and other twisty puzzles is one of Dr. Okolie's hobbies. These free tutorials take you from a scrambled puzzle to a solved one, step by step: four cubes, a pyramid, a 12-sided Megaminx and the shape-shifting Helicopter cube.</p>
<div class="btns" style="margin-top:24px"><a class="btn pri" href="rubiks-cube-3x3.html">Learn the 3×3</a><a class="btn" href="rubiks-cube-request.html">Request a tutorial or cube</a></div></div>
<div class="cube-hero-art">{svg_3x3("scrambled", 230)}</div></div></div>
<section><div class="wrap cols" style="align-items:start"><div><span class="tag">A hobby that teaches</span><h2>Why a cube?</h2>
<p class="muted">Dr. Okolie has used the Rubik's cube to explain complex topics, and he has delivered a talk titled <em>Understanding Process Simulators with the Rubik's Cube</em>, which compares working with a process simulator to solving a cube.</p>
<p class="muted">The two have a lot in common. A cube is a system of connected parts: turn one face and pieces on four other faces move with it. A process flowsheet works the same way, where changing one unit changes the streams going into the next. In both, it helps to break a big problem into stages, use a small set of tested moves, and check the state of the whole system after every step.</p></div>
<div class="steps cube-parallels"><div class="step"><span>Cube</span><b>Layer by layer</b><p>Solve one layer, then keep it safe while you work on the next.</p></div>
<div class="step"><span>Simulator</span><b>Unit by unit</b><p>Converge one unit operation, then connect it to the rest of the flowsheet.</p></div>
<div class="step"><span>Cube</span><b>Algorithms</b><p>Short, proven move sequences that change only what you want changed.</p></div>
<div class="step"><span>Simulator</span><b>Models</b><p>Validated unit models and solvers you can trust to behave the same way every time.</p></div></div></div></section>
<section class="tint"><div class="wrap"><span class="tag">Tutorials</span><h2>Pick a puzzle</h2><p class="lede">Each tutorial uses a beginner method with only a few algorithms to memorise. New to cubing? Start with the 2×2 or the 3×3.</p>
<div class="cards cube-cards">{cards}</div></div></section>
<section><div class="wrap"><span class="tag">Gallery</span><h2>Solved and ready</h2><div class="gallery cube-gallery">
<figure><img src="img/cube-4x4-solved.jpg" alt="A young cuber smiling and holding up a solved 4×4 cube" loading="lazy"><figcaption>A solved 4×4: centres, paired edges, then the 3×3 finish.</figcaption></figure>
<figure><img src="img/cube-mirror-face.jpg" alt="A hand holding a mirror cube showing a flat face made of different-sized silver pieces, with the centre marked in pink" loading="lazy"><figcaption>One face of a mirror cube. Every piece is a different size, and the centre has been marked with a pen.</figcaption></figure></div></div></section>
<section class="tint"><div class="wrap"><span class="tag">Before you start</span><h2>Tips for every puzzle</h2><div class="eq">
<article><div><h3>Learn the notation first</h3><p>Every tutorial writes moves as letters (R, U, F and so on). Five minutes on the notation table saves an hour of confusion.</p></div></article>
<article><div><h3>Keep your grip</h3><p>Hold the puzzle the same way for a whole algorithm. Most mistakes come from rotating the cube in the middle of a sequence.</p></div></article>
<article><div><h3>Go slowly, then repeat</h3><p>Do each algorithm slowly until your hands remember it. Speed comes later, by itself.</p></div></article></div></div></section>""" + cta()

def page_3x3():
    s = [
        step(1, "Make the white cross", svg_3x3("cross"),
             "<p>Hold the cube with the <b>yellow centre on top</b>. Bring the four white edge pieces up around it to make a \"daisy\": a yellow centre with four white petals. Edges can be moved up without any algorithm; just turn the face that holds one until it reaches the top, then turn the top so you don't knock off a petal you already placed.</p>"
             "<p>Now turn the top until one petal's side colour matches the centre below it, then hold that petal at the front and turn the front face twice (" + alg("F2") + "). The white edge drops to the bottom. Repeat for all four petals. Flip the cube over and you should see a white cross whose side colours match each side centre.</p>",
             "Goal: a white cross whose side colours match the centres"),
        step(2, "Solve the white corners", svg_3x3("layer1"),
             "<p>Hold the cube with <b>white on the bottom</b> from now on. Find a corner in the top layer that has white on it. Turn the top layer until that corner sits directly above the place it belongs (between the two centres that match its other two colours), then turn the whole cube so that place is at the front-right.</p>"
             f"<p>Repeat {alg(A['corner'])} until the corner drops into place with white facing down. It takes one to five repeats. If a white corner is stuck in the bottom layer in the wrong spot, hold it at the front-right and do {alg(A['corner'])} once to bring it up.</p>",
             "Goal: the whole white layer solved"),
        step(3, "Solve the middle layer", svg_3x3("layer2"),
             "<p>Find an edge in the top layer with <b>no yellow</b> on it. Turn the top until the colour on its front matches the front centre, making an upside-down T. Look at its top colour. If it matches the right-hand centre, the edge goes to the right:</p>"
             f"<p class='alg-line'>{alg(A['mid_right'])}</p><p>If it matches the left-hand centre, the edge goes to the left:</p><p class='alg-line'>{alg(A['mid_left'])}</p>"
             "<p>If a middle edge is in the wrong slot or flipped, use either algorithm to push any top edge into that slot. That brings the wrong edge back up so you can insert it properly.</p>",
             "Goal: the first two layers solved"),
        step(4, "Make the yellow cross", svg_3x3("ycross"),
             f"<p>Look only at the yellow stickers on top, ignoring corners. You will see a dot, an L, a line, or a cross already. The algorithm is {alg(A['cross'])}.</p>"
             "<ul><li><b>Dot:</b> do the algorithm once to get an L.</li><li><b>L:</b> hold it so the two yellow edges point to the back and left (like a clock reading 9:00 to 12:00), then do the algorithm to get a line.</li><li><b>Line:</b> hold it horizontally (left to right), then do the algorithm to get the cross.</li></ul>",
             "Goal: a yellow cross on top"),
        step(5, "Match the yellow edges", svg_3x3("yedges"),
             "<p>Turn the top until at least two yellow edges have side colours that match their centres. If the two matching edges are next to each other, hold them at the <b>back</b> and the <b>right</b>, then do:</p>"
             f"<p class='alg-line'>{alg(A['edges'])}</p><p>If the two matching edges are opposite each other, do the algorithm once from any side, then turn the top to find two adjacent matching edges and do it again.</p>",
             "Goal: all four yellow edges match their centres"),
        step(6, "Put the yellow corners in place", svg_3x3("ycorners"),
             "<p>A corner is \"in place\" when it sits between the three centres that match its colours, even if it is twisted. Find a corner that is already in place and hold it at the <b>front-right</b> of the top layer. Then do:</p>"
             f"<p class='alg-line'>{alg(A['corners_place'])}</p><p>Repeat until all four corners are in place. If no corner is in place yet, do the algorithm once from any side and look again.</p>",
             "Goal: every corner in its spot (some may still be twisted)"),
        step(7, "Twist the yellow corners", svg_3x3("solved"),
             "<p>Hold the cube with yellow on top and an unsolved corner at the <b>front-right</b>. Repeat " + alg(A["corners_twist"]) + " until that corner shows yellow on top (two or four times). The bottom layers will look scrambled. <b>That's expected, so keep going.</b></p>"
             "<p>Now turn only the top layer (" + alg("U") + ") to bring the next unsolved corner to the front-right, and repeat. Don't turn the whole cube. When every corner shows yellow on top, the rest of the cube comes back together. Turn the top layer to finish.</p>",
             "Solved!"),
    ]
    body = f'<section><div class="wrap">{notation_cube()}</div></section><section class="tint"><div class="wrap cube-steps">{"".join(s)}</div></section>'
    return tutorial_page("rubiks-cube-3x3.html", "How to solve a 3×3 Rubik's cube", "The layer-by-layer beginner method: seven steps and six short algorithms. Colours below use the standard scheme (white opposite yellow, green opposite blue, red opposite orange).", body)

def page_2x2():
    s = [
        step(1, "Solve one layer", svg_2x2("layer1"),
             "<p>A 2×2 has no centres, so pick a colour (white is a good start) and build that face, making sure the side colours of the four corners match each other in pairs.</p>"
             f"<p>It's the same as the 3×3 corner step. Hold white on the bottom, put a white corner in the top layer directly above where it belongs at the front-right, and repeat {alg(A['corner'])} until it drops in with white facing down.</p>",
             "Goal: a full white layer with matching sides"),
        step(2, "Make the top face yellow", svg_2x2("top_grey"),
             "<p>Hold yellow on top. Put a corner that does not show yellow on top at the <b>front-right</b>, and repeat " + alg(A["corners_twist"]) + " until yellow faces up (two or four times). The bottom layer will look broken for a while. <b>Don't worry.</b></p>"
             "<p>Turn only the top layer (" + alg("U") + ") to bring the next corner without yellow on top to the front-right, and repeat. Once the whole top is yellow, the bottom layer is restored.</p>",
             "Goal: the top face all yellow"),
        step(3, "Swap the top corners into place", svg_2x2("top"),
             "<p>Look at the sides of the top layer for <b>headlights</b>: two corners on the same side whose side colours match. Hold the headlights at the <b>back</b> and do:</p>"
             f"<p class='alg-line'>{alg(A['aperm'])}</p><p>If there are no headlights on any side, do the algorithm once from any side; headlights will appear. Then turn the top layer to line it up with the bottom.</p>",
             "Before step 3: top is yellow, but the corners still need swapping"),
        step(4, "Done", svg_2x2("solved"), "<p>That's the whole 2×2. Because it is just the corners of a 3×3, everything you learned here carries straight over to the 3×3 tutorial.</p>", "Solved!"),
    ]
    body = f'<section><div class="wrap">{notation_cube()}</div></section><section class="tint"><div class="wrap cube-steps">{"".join(s)}</div></section>'
    return tutorial_page("rubiks-cube-2x2.html", "How to solve a 2×2 cube", "The 2×2 (pocket cube) is only corners, so it needs just three algorithms. It's the quickest way to learn how a cube moves.", body)

def page_pyraminx():
    ins = "".join(f"<tr><td>{w}</td><td>{f}</td><td>{alg(a)}</td></tr>" for w, f, a in PYR_INSERT)
    rows = [("U, L, R, B", "Turn the two layers around the top, left, right or back corner clockwise, as if you were looking at that corner from outside"),
            ("u, l, r, b", "Turn only the small tip at that corner"), ("U'", "Counter-clockwise")]
    notation = ('<div class="cube-notation"><div><span class="tag">Notation</span><h2>Reading the moves</h2><p class="muted">Hold the Pyraminx with one face toward you and one corner pointing up. '
                'Its four corners are U (top), L (bottom-left), R (bottom-right) and B (back).</p></div><table class="cube-table"><tbody>'
                + "".join(f"<tr><td>{alg(a)}</td><td>{d}</td></tr>" for a, d in rows) + "</tbody></table></div>")
    s = [
        step(1, "Turn the tips", svg_pyra("tips"),
             "<p>The four small tips at the corners turn on their own and never get in the way. Turn each tip until it matches the three centre triangles just below it. Done.</p>", "Goal: every tip matches its centres"),
        step(2, "Line up the centres", svg_pyra("centers"),
             "<p>Choose a colour for the bottom. One corner has three centres that don't include that colour; point that corner up. Now turn each of the three bottom corners (" + alg("L") + ", " + alg("R") + ", " + alg("B") + ") until its centre on the bottom face shows your bottom colour. Finally turn " + alg("U") + " so the top centres match the ones below them.</p>",
             "Goal: each face's three centres match"),
        step(3, "Solve the bottom edges", svg_pyra("bottom"),
             "<p>Work on the edge at the front of the bottom face. Find the edge piece with the bottom colour and the front colour. If it is in the top layer, find its case below and do that algorithm (each one restores the top centres at the end). Then turn the whole puzzle, keeping the bottom down, and repeat for the other two bottom edges.</p>"
             f'<table class="cube-table cube-table-3"><thead><tr><th>Edge is at the…</th><th>Bottom colour faces the…</th><th>Do</th></tr></thead><tbody>{ins}</tbody></table>'
             "<p class=\"muted\">If the edge is already in the bottom but in the wrong place or flipped, do any of these algorithms once to bring it up to the top, then insert it.</p>",
             "Goal: the bottom face and its edges solved"),
        step(4, "Solve the last three edges", svg_pyra("flip"),
             "<p>Only the three edges around the top corner are left. First, get each edge into the right position even if it is flipped. If they need to cycle, do:</p>"
             f"<p class='alg-line'>{alg(A['pyr_cycle'])}</p><p>If that sent them the wrong way round, do it once more. Then, if two edges are flipped, turn the whole puzzle (bottom still down) so the flipped two are at the front-left and front-right, and do:</p>"
             f"<p class='alg-line'>{alg(A['pyr_flip'])}</p>", "Two flipped edges at the front, ready for the last algorithm"),
        step(5, "Done", svg_pyra("solved"), "<p>Solved. The Pyraminx has far fewer positions than a 3×3, so with a little practice you'll be solving it in under a minute.</p>", "Solved!"),
    ]
    body = (video_block("cube-pyraminx-solve.mp4", "cube-pyraminx-solve.jpg", "Dr. Okolie solves the Pyraminx", "A quick Pyraminx solve by Dr. Okolie in his office. Once the tips and centres are set, the last edges go fast.")
            + f'<section><div class="wrap">{notation}</div></section><section class="tint"><div class="wrap cube-steps">{"".join(s)}</div></section>')
    return tutorial_page("rubiks-cube-pyraminx.html", "How to solve the triangle (Pyraminx)", "The pyramid puzzle looks harder than a cube but is easier: four steps and two algorithms for the finish.", body)

def page_mirror():
    s = [
        step(1, "Understand the pieces", svg_mirror(),
             "<p>The mirror cube is a 3×3 in disguise. Inside, it turns exactly like a Rubik's cube, but every layer is cut at a different thickness and all faces have the same mirror finish. Instead of colours, you identify pieces by their <b>size and shape</b>.</p>"
             "<p>Like the 3×3, there are six centres, twelve edges and eight corners, and the centres never move relative to each other. A piece is solved when its outer surfaces sit flush with its neighbours.</p>",
             "Solved: a perfect cube again"),
        step(2, "Pick your \"white\" face", '<img class="cube-photo" src="img/cube-mirror-face.jpg" alt="A mirror cube face with a pen mark on the centre" loading="lazy">',
             "<p>Choose one face to solve first. A face whose centre is easy to recognise, such as the thinnest one, is a good choice. Build a cross on that face: find the four edges whose height matches the face's centre and line each one up so both of its surfaces are flush with the centres it touches.</p>",
             "Tip: a small pen mark on one centre helps you find your starting face again"),
        step(3, "Follow the 3×3 method", None,
             "<p>From here, follow the <a href=\"rubiks-cube-3x3.html\">3×3 tutorial</a> step by step, using the same algorithms. Wherever it says \"match the colours\", match the heights instead:</p>"
             "<ul><li><b>Corners and middle layer:</b> a corner or edge belongs in a slot when all of its surfaces line up flush with the centres around it.</li>"
             f"<li><b>Last layer:</b> the yellow-cross, edge and corner steps work the same way ({alg(A['cross'])}, {alg(A['edges'])}, {alg(A['corners_place'])}, {alg(A['corners_twist'])}).</li>"
             "<li><b>Run your fingers over it:</b> feel for steps along each face. A flat face with no ledges means that layer is solved.</li></ul>", ""),
        step(4, "Tips", None,
             "<ul><li>Learn the 3×3 first. It's much easier to recognise a stage you have already seen in colour.</li><li>Work in good light and turn the cube to catch reflections; edges stand out better from an angle.</li>"
             "<li>Your last layer is the face opposite the one you started with. Remember which it is before you begin.</li></ul>", ""),
    ]
    body = (video_block("cube-mirror-solve.mp4", "cube-mirror-solve.jpg", "Dr. Okolie solves the mirror cube", "Watch Dr. Okolie solve a mirror cube. Every face is silver, so the pieces are told apart by their size and shape rather than colour.")
            + f'<section class="tint"><div class="wrap cube-steps">{"".join(s)}</div></section>')
    return tutorial_page("rubiks-cube-mirror.html", "How to solve the mirror cube", "Same moves as a 3×3, different senses: you solve this one by shape, not colour.", body)

def page_4x4():
    s = [
        step(1, "Solve the centres", svg_4x4("centers"),
             "<p>Each face of a 4×4 has a 2×2 block of centre pieces that can move around. First solve the white centre: pair two white centre pieces into a 1×2 bar, pair the other two, then bring the bars together. Next solve the yellow centre on the <b>opposite</b> face. Moves like " + alg("Rw U Rw'") + " lift pieces in and out without disturbing the bottom centre.</p>"
             "<p>Then turn the cube so white and yellow are on the <b>left and right</b>. The other four centres (green, red, blue, orange) can now be built with " + alg("r") + ", " + alg("r'") + ", " + alg("U") + ", " + alg("F") + ", " + alg("D") + " and " + alg("B") + " turns, which never touch the left and right centres. Short moves such as " + alg("r U r'") + " and " + alg("r U2 r'") + " move a bar between the top and front centres. Make sure the four go in the right order around the cube: green, red, blue, orange (with white on top, green in front, red is on the right).</p>",
             "Goal: all six centres solved"),
        step(2, "Pair up the edges", svg_4x4("edges"),
             "<p>Each 3×3 edge becomes two edge pieces on a 4×4, so you pair the 24 pieces into 12 \"dedges\". Outer-layer turns (" + alg("R") + ", " + alg("U") + ", " + alg("F") + " and so on) never break up centres or finished pairs, so use them freely to set up.</p>"
             "<p>Hold white on top. Find two matching edge pieces and put them both in the <b>upper of the two middle rows</b>: one on the left edge of the front face, one on the right edge, <b>both showing the same colour on the front</b>. Then do:</p>"
             f"<p class='alg-line'>{alg(A['pair'])}</p><p>The pair is now finished at the front-right. Move it into the top or bottom layer with outer turns and repeat. If the piece on the right shows the wrong colour on the front, {alg(A['flip'])} flips the front-right edge in place. For the final two edges, the same algorithm finishes both at once when the lower halves match too.</p>",
             "Goal: centres solved and every edge paired"),
        step(3, "Solve it like a 3×3", '<img class="cube-photo" src="img/cube-4x4-solved.jpg" alt="A young cuber holding up a solved 4×4 cube" loading="lazy">',
             "<p>Now treat each 2×2 centre as one centre and each pair as one edge, and follow the <a href=\"rubiks-cube-3x3.html\">3×3 tutorial</a> using outer-layer turns only. Two situations that a 3×3 can't have may appear at the end. They're called <b>parity</b>, and each has its own fix below.</p>", "Solved!"),
        step(4, "Fix OLL parity: one flipped edge", svg_4x4("oll"),
             "<p>While making the yellow cross, you might find a single edge flipped (an odd number of yellow edges point up, so you can never make the cross). Hold the flipped edge at the <b>front</b> of the top layer and do:</p>"
             f"<p class='alg-line'>{alg(A['oll_parity'])}</p><p>In this algorithm " + alg("r") + " and " + alg("l") + " turn only the inner slice. Then carry on with the yellow cross.</p>",
             "OLL parity: the front edge is flipped"),
        step(5, "Fix PLL parity: two edges swapped", svg_4x4("pll"),
             "<p>At the very end you may find two opposite edges in the top layer swapped, with everything else solved. Hold them at the <b>front</b> and <b>back</b> and do:</p>"
             f"<p class='alg-line'>{alg(A['pll_parity'])}</p><p>Here " + alg("r2") + " turns only the inner right slice, " + alg("Uw2") + " the top two layers, and " + alg("u2") + " only the inner top slice.</p>",
             "PLL parity: front and back edges swapped"),
    ]
    body = f'<section><div class="wrap">{notation_cube(big=True)}</div></section><section class="tint"><div class="wrap cube-steps">{"".join(s)}</div></section>'
    return tutorial_page("rubiks-cube-4x4.html", "How to solve a 4×4 cube", "The reduction method: build the centres, pair the edges, and you're left with a big 3×3. Learn the 3×3 first.", body)


def notation_mega():
    rows = [("U", "Top face, one-fifth turn (72°) clockwise"), ("F", "Front face: the upper face pointing at you"), ("R, L", "The upper faces to the right and left of F"),
            ("BR, BL", "The two upper faces at the back"), ("DR, DL", "The lower faces at the front-right and front-left (below where F meets R or L)"),
            ("D", "The bottom face (white)"), ("R'", "A prime (') means counter-clockwise"), ("U2, U2'", "Two-fifths of a turn (144°) clockwise or counter-clockwise")]
    trs = "".join(f"<tr><td>{alg(a)}</td><td>{d}</td></tr>" for a, d in rows)
    return ('<div class="cube-notation"><div><span class="tag">Notation</span><h2>Reading the moves</h2><p class="muted">Hold the Megaminx with the <b>white face at the bottom</b> for the whole tutorial. '
            'One of the five upper faces points at you: that is F. "Clockwise" means clockwise as if you were looking straight at that face. To work on a different spot, turn the whole puzzle, keeping white at the bottom.</p></div>'
            f'<table class="cube-table"><tbody>{trs}</tbody></table></div>')

def page_megaminx():
    m = MEGA
    s4 = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{alg(m[k])}</td></tr>" for a, b, k in (
        ("Front and lower-left (F + DL colours)", "The F colour is on top", "s4_dl_a"), ("Front and lower-left (F + DL colours)", "The F colour faces the front", "s4_dl_b"),
        ("Front and lower-right (F + DR colours)", "The F colour is on top", "s4_dr_a"), ("Front and lower-right (F + DR colours)", "The F colour faces the front", "s4_dr_b")))
    st = [
        step(1, "Make the white star", svg_mega("s1"),
             "<p>Bring the five white edges down next to the white centre, each with its other colour matching the centre of the face beside it. This is intuitive: a lower face turn (" + alg("DR") + ", " + alg("DL") + " and so on) swings an edge down into the white face, and top-layer turns let you line it up first. Tip: turn the puzzle upside down while you do this, so you can see the white face.</p>",
             "Goal: a white star with matching side colours (seen from below)"),
        step(2, "Solve the white corners", svg_mega("s2"),
             "<p>Turn the puzzle (white still at the bottom) so the corner slot you want to fill is at the front, between " + alg("DL") + ", " + alg("DR") + " and white. Using only " + alg("U") + " and " + alg("F") + " turns (they never touch the white face), bring the corner to the spot <b>directly above its slot</b>, where F, DL and DR meet. Then repeat:</p>"
             f"<p class='alg-line'>{alg(m['s2'])}</p><p>until the corner drops in with white facing down (one to five times). If a white corner is in the wrong slot, hold that slot at the front and do the algorithm once to lift it out.</p>",
             "Goal: the whole white face, seen from below"),
        step(3, "Second layer edges", svg_mega("s3"),
             "<p>These five edges sit between neighbouring lower faces. Hold the slot you want at the front, between " + alg("DL") + " and " + alg("DR") + ". Bring the edge into the front face F (with " + alg("U") + " and " + alg("F") + " turns), then turn " + alg("F") + " until its side colour matches the centre beside it.</p>"
             f"<p>If it's on the lower-left of F, matching DL, it goes to the right:</p><p class='alg-line'>{alg(m['s3_right'])}</p><p>If it's on the lower-right of F, matching DR, it goes to the left:</p><p class='alg-line'>{alg(m['s3_left'])}</p>"
             "<p class=\"muted\">These are the 3×3 middle-layer algorithms, with F playing the part of the top face. If an edge is in the wrong slot, use either one to push another edge in, which brings the wrong one back out.</p>",
             "Goal: white face and second-layer edges"),
        step(4, "Finish the lower faces", svg_mega("s4"),
             "<p>Each of the five lower faces still needs one corner and two edges. Work on one front face at a time: its slot is the corner where " + alg("F") + ", " + alg("DL") + " and " + alg("DR") + " meet, plus the edges F–DL and F–DR.</p>"
             "<p><b>Corner first.</b> Turn " + alg("U") + " until the corner is at the top-front-left, then do " + alg("F'") + " to bring it to the front-left middle spot (where F, L and DL meet). Now repeat:</p>"
             f"<p class='alg-line'>{alg(m['s4_corner'])}</p><p>until the corner is solved (one to five times). Then the two edges: turn " + alg("U") + " to bring the edge to the top-front, and find its case:</p>"
             f'<table class="cube-table cube-table-3"><thead><tr><th>The edge belongs at the…</th><th>When</th><th>Do</th></tr></thead><tbody>{s4}</tbody></table>'
             f"<p class=\"muted\">These moves never disturb the other lower faces. If a piece is stuck in the middle ring of the puzzle, turn the puzzle so it's at the front-left middle spot and do {alg(m['lift'])} to lift it to the top without breaking anything you've solved. If a piece is in the wrong slot, hold that slot at the front and do the matching algorithm once to swap it out.</p>",
             "Goal: all lower faces finished"),
        step(5, "Fill the upper ring", svg_mega("s5"),
             "<p>Now only the top face and the ring of slots just below it remain, and the top face is free to move, just like the last layers of a 3×3. For each slot (the corner where F, R and DR meet, and the edge between F and R):</p>"
             f"<p><b>Corner:</b> turn " + alg("U") + " to bring it to the top-front-right, then repeat " + alg(m["s5_corner"]) + " until it drops in correctly.</p>"
             f"<p><b>Edge:</b> turn " + alg("U") + f" until the edge's front colour matches F. If its top colour matches R, do {alg(m['s5_right'])}; if it matches L, do {alg(m['s5_left'])}.</p>",
             "Goal: everything except the top face"),
        step(6, "Make the top star", svg_mega("star"),
             f"<p>Look at the five top edges. Some show the top colour on top, some don't (there is always an even number that don't). The algorithm is {alg(m['eo'])}.</p>"
             "<ul><li><b>Two wrong, not next to each other:</b> one at the front, the other at the back-right. Do the algorithm once.</li>"
             "<li><b>Two wrong, next to each other:</b> hold them at the front and front-right. Do it once to get the case above.</li>"
             "<li><b>Four wrong:</b> hold the correct one at the front-right. Do it once to get two wrong next to each other.</li></ul>",
             "Goal: a star of the top colour"),
        step(7, "Match the top edges", svg_mega("ep"),
             f"<p>Turn {alg('U')} until as many top edges as possible match their side centres. The algorithm is {alg(m['ep'])}; it cycles the three edges at the right and back, leaving the front and left edges in place.</p>"
             "<ul><li><b>Two edges next to each other match:</b> hold them at the front and left. Do the algorithm, then once more if needed.</li>"
             "<li><b>Two edges match but not next to each other:</b> hold one at the front, the other at the back-right. Do the algorithm.</li>"
             "<li><b>Only one matches:</b> hold it at the left. Do the algorithm.</li></ul><p>After each one, turn " + alg("U") + " again to line up as many as possible, and repeat.</p>",
             "Goal: all five top edges match"),
        step(8, "Put the top corners in place", svg_mega("cp"),
             f"<p>Don't turn the top any more: the edges are solved. A corner is in place when it sits between the three centres that match its colours, even if twisted. The algorithm is {alg(m['cp'])}.</p>"
             "<ul><li><b>Two neighbouring corners in place:</b> hold them at the top front-left and front-right. Do the algorithm, then once more if needed.</li>"
             "<li><b>Two corners in place, not neighbours:</b> hold one at the front-right, the other at the back (between BR and BL). Do the algorithm.</li>"
             "<li><b>One corner in place:</b> hold it at the front-left. Do the algorithm.</li><li><b>None:</b> do it from any side.</li></ul><p>Look again after each one and repeat until all five are in place.</p>",
             "Goal: corners in place (two still twisted here)"),
        step(9, "Twist the top corners", svg_mega("solved"),
             "<p>Exactly like the last step of the 3×3. Hold an unsolved corner at the <b>top-front-right</b> and repeat " + alg(m["co"]) + " until the top colour faces up (two or four times). The rest of the puzzle will look scrambled. <b>Keep going.</b> Turn only " + alg("U") + " to bring the next unsolved corner to the front-right and repeat. When all five are done, everything comes back; turn the top to line it up.</p>",
             "Solved!"),
    ]
    body = f'<section><div class="wrap">{notation_mega()}</div></section><section class="tint"><div class="wrap cube-steps">{"".join(st)}</div></section>'
    return tutorial_page("rubiks-cube-megaminx.html", "How to solve the Megaminx", "The 12-sided Megaminx is solved just like a 3×3, one layer at a time, only with more layers. If you can solve a 3×3, every idea here will feel familiar.", body)

def page_helicopter():
    h = HELI
    rows = [("UF", "Half turn (180°) around the edge between the top (U) and front (F) faces"), ("UR, UL, UB", "The other three top edges"),
            ("FR, FL", "The two front vertical edges"), ("DF, DR…", "Edges on the bottom work the same way")]
    trs = "".join(f"<tr><td>{alg(a)}</td><td>{d}</td></tr>" for a, d in rows)
    notation = ('<div class="cube-notation"><div><span class="tag">Notation</span><h2>Reading the moves</h2><p class="muted">The Helicopter cube turns around its <b>edges</b>, not its faces. '
                'Each move is a half turn around one edge, named after the two faces that meet there. Because every move is a half turn, there is no clockwise or counter-clockwise, and doing the same move twice undoes it.</p>'
                '<p class="muted"><b>Only make full half turns.</b> If you stop part-way, the pieces can jump into a strange non-cube shape. That\'s called jumbling, and it\'s fun later but confusing now. If it happens, turn back.</p></div>'
                f'<table class="cube-table"><tbody>{trs}</tbody></table></div>')
    st = [
        step(1, "Put the corners in place", svg_heli("corners"),
             "<p>Solve the corners first and ignore the triangle-shaped centres for now. Every turn swaps the two corners at the ends of that edge (and twists them).</p>"
             "<p>Pick one corner as your reference; every other corner then has one correct place in the colour scheme (white opposite yellow, green opposite blue, red opposite orange). Move the corners home one at a time: turning the edge between two corners swaps them. To swap two corners that don't share an edge, use three swaps through a corner between them: A↔B, then B↔C, then A↔B again. That swaps A and C and leaves B where it was. Don't worry about twisted corners yet.</p>",
             "Goal: every corner in its place (centres greyed out)"),
        step(2, "Twist the corners", svg_heli("twist"),
             "<p>Hold the cube so a twisted corner is at the <b>top front-right</b>, with a neighbour at the top front-left. There are two algorithms, and each twists both front corners at once:</p>"
             f"<p class='alg-line'>{alg(h['twist_a'])}</p><p>moves the top sticker of both front corners down onto the front face, and</p><p class='alg-line'>{alg(h['twist_b'])}</p>"
             "<p>moves the top sticker of each front corner out to the side (right for the right corner, left for the left). Use one of them to fix the front-right corner. The front-left corner gets twisted too, so make it your next corner: turn the whole cube so it becomes the front-right corner and repeat with its next neighbour. Work your way around the top, then the bottom. When you reach the last corner, it will already be right.</p>",
             "The two front corners after the first twist algorithm"),
        step(3, "Solve the centres", svg_heli("cycle"),
             f"<p>The centres are solved with one algorithm that swaps three centres in a loop without touching the corners:</p><p class='alg-line'>{alg(h['cycle'])}</p>"
             "<p>It moves the centre at spot 1 (front face, upper-left) to spot 2 (top face, front-right), spot 2 to spot 3 (right face, upper-back), and spot 3 back to spot 1. Doing the moves in reverse order sends them the other way.</p>"
             "<p>To use it on any centre: first do one or two <b>setup moves</b> that bring the centre you want into one of the three spots, without moving the other two spots. Do the algorithm, then undo your setup moves in reverse order. Because the corners are only moved by the setup moves, undoing them puts the corners back. Work one face at a time. Centres of the same colour are identical, so any matching centre will do.</p>",
             "The three centres the algorithm cycles: 1 → 2 → 3 → 1"),
        step(4, "Done", svg_heli("solved"), "<p>Solved! Once you're comfortable, try jumbling turns. They take the puzzle into shapes no cube can make.</p>", "Solved!"),
    ]
    body = f'<section><div class="wrap">{notation}</div></section><section class="tint"><div class="wrap cube-steps">{"".join(st)}</div></section>'
    return tutorial_page("rubiks-cube-helicopter.html", "How to solve the Helicopter cube", "It looks like a cube, but it turns around its edges, and an uneven turn sends it into wild non-cube shapes. Corners first, then centres.", body)

def page_request():
    opts = "".join(f'<option value="{E(t)}">{t}</option>' for t in ["2×2 cube", "3×3 cube", "Triangle (Pyraminx)", "Mirror cube", "4×4 cube", "Megaminx", "Helicopter cube", "Not sure yet"])
    radio = lambda name, vals, req=True: "".join(f'<label class="opt"><input type="radio" name="{name}" value="{E(v)}"{" required" if req and i == 0 else ""}><span>{v}</span></label>' for i, v in enumerate(vals))
    form = f"""<form class="cube-form" name="cube-request" method="POST" action="rubiks-cube-thanks.html" data-netlify="true" netlify-honeypot="company">
<input type="hidden" name="form-name" value="cube-request"><p class="hp" hidden><label>Leave this empty <input name="company"></label></p>
<fieldset><legend>About you</legend><div class="f-row"><div class="f"><label for="cr-name">Name</label><input type="text" id="cr-name" name="name" autocomplete="name" required></div>
<div class="f"><label for="cr-email">Email</label><input type="email" id="cr-email" name="email" autocomplete="email" required></div></div></fieldset>
<fieldset><legend>What would you like?</legend><div class="opts">{radio("request", ["A personalised tutorial", "A cube to practise with", "Both"])}</div></fieldset>
<fieldset><legend>Which puzzle?</legend><div class="f"><label for="cr-puzzle">Puzzle</label><select id="cr-puzzle" name="puzzle" required><option value="">Choose one</option>{opts}</select></div></fieldset>
<fieldset><legend>Your experience</legend><div class="opts">{radio("level", ["I've never solved one", "I can solve part of it", "I can solve it and want to improve"])}</div></fieldset>
<fieldset><legend>Tutorial format <small>If you asked for a tutorial</small></legend><div class="opts">{radio("format", ["In person at Bucknell", "Online video call", "Either is fine"], False)}</div></fieldset>
<fieldset><legend>Anything else?</legend><div class="f"><label for="cr-msg">Message</label><textarea id="cr-msg" name="message" rows="5" placeholder="Where are you stuck? Is this for a class, a club or yourself?"></textarea></div>
<p class="muted" style="font-size:14px;margin:10px 0 0">If you'd like a cube, we'll reply by email to arrange how to get it to you. Please don't include a home address here.</p></fieldset>
<button class="btn pri" type="submit">Send request</button></form>"""
    side = """<div><span class="tag">Get in touch</span><h2>Personalised tutorials and practice cubes</h2>
<p class="muted">Stuck on a step, or teaching a group and want help? Dr. Okolie offers personalised tutorials on the 2×2, 3×3, Pyraminx, mirror cube, 4×4, Megaminx and Helicopter cube. If you don't have a puzzle yet, ask for one to practise with.</p>
<ul class="list"><li><b>Students and beginners</b><br><span class="muted">One-on-one help to get your first solve.</span></li><li><b>Classes and clubs</b><br><span class="muted">Using the cube to explain systems thinking and problem solving.</span></li><li><b>Practice cubes</b><br><span class="muted">Ask, and we'll be in touch about sending one.</span></li></ul></div>"""
    body = f'<section><div class="wrap cols" style="align-items:start">{side}{form}</div></section>'
    return (f'<div class="page-hero cube-hero"><div class="wrap"><span class="tag">Puzzle Corner</span><h1>Request a tutorial or a cube</h1><p>Fill in the form and Dr. Okolie will get back to you by email.</p>{subnav("rubiks-cube-request.html")}</div></div>' + body)

def page_thanks():
    return ('<div class="page-hero cube-hero"><div class="wrap"><span class="tag">Puzzle Corner</span><h1>Thank you!</h1><p>Your request has been sent. Dr. Okolie will reply by email.</p></div></div>'
            f'<section><div class="wrap cube-thanks">{svg_3x3("solved", 180)}<div><h2>While you wait</h2><p class="muted">Pick a tutorial and try the first step.</p><div class="btns"><a class="btn pri" href="rubiks-cube.html">All tutorials</a><a class="btn" href="index.html">Back to the lab website</a></div></div></div></section>')

PAGES = [
    ("rubiks-cube.html", "Puzzle Corner · SETD Research Group", "Dr. Jude Okolie's puzzle corner: free beginner tutorials for the 2x2, 3x3, Pyraminx, mirror cube, 4x4, Megaminx and Helicopter cube.", page_landing),
    ("rubiks-cube-2x2.html", "How to Solve a 2x2 Cube · SETD Research Group", "Step-by-step beginner tutorial for the 2x2 pocket cube.", page_2x2),
    ("rubiks-cube-3x3.html", "How to Solve a 3x3 Rubik's Cube · SETD Research Group", "Layer-by-layer beginner tutorial for the 3x3 Rubik's cube.", page_3x3),
    ("rubiks-cube-pyraminx.html", "How to Solve the Pyraminx · SETD Research Group", "Beginner tutorial for the triangle-shaped Pyraminx puzzle.", page_pyraminx),
    ("rubiks-cube-mirror.html", "How to Solve the Mirror Cube · SETD Research Group", "How to solve the mirror cube using the 3x3 method.", page_mirror),
    ("rubiks-cube-4x4.html", "How to Solve a 4x4 Cube · SETD Research Group", "Beginner reduction method for the 4x4 cube, including parity fixes.", page_4x4),
    ("rubiks-cube-megaminx.html", "How to Solve the Megaminx · SETD Research Group", "Beginner layer-by-layer tutorial for the Megaminx (12-sided puzzle).", page_megaminx),
    ("rubiks-cube-helicopter.html", "How to Solve the Helicopter Cube · SETD Research Group", "Beginner tutorial for the Helicopter cube: corners first, then centres.", page_helicopter),
    ("rubiks-cube-request.html", "Request a Puzzle Tutorial · SETD Research Group", "Request a personalised Rubik's cube tutorial or a practice cube from Dr. Jude Okolie.", page_request),
    ("rubiks-cube-thanks.html", "Thank You · SETD Research Group", "Your Rubik's cube tutorial request was sent.", page_thanks),
]

def build_cube_pages(page):
    verify(); verify_mega_heli()
    for fname, title, desc, fn in PAGES:
        page(fname, title, desc, fn())
