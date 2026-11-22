"""Small sticker simulators for the Rubik's cube tutorials.

Used by cube_pages.py to (1) check that every algorithm printed on the site does
what the tutorial says it does, and (2) draw the cube diagrams as inline SVG.

Cube notation (standard): R L U D F B turn one outer face clockwise as seen when
looking at that face; ' = counter-clockwise, 2 = half turn. On big cubes Rw (two
right layers), r (inner right slice only), x y z whole-cube rotations.
Pyraminx: U L R B turn two layers around that vertex clockwise (seen looking at
the vertex); u l r b turn only the tip.
"""
import math, re, itertools

# ---------------- NxN cube ----------------
FACES = {"U": (0, 1, 0), "D": (0, -1, 0), "R": (1, 0, 0), "L": (-1, 0, 0), "F": (0, 0, 1), "B": (0, 0, -1)}
COLOR = {"U": "#FFFFFF", "D": "#FFD500", "F": "#009E60", "B": "#0051BA", "R": "#C41E3A", "L": "#FF5800", "X": "#C9CED6"}

def _rot(v, axis, q):
    """Rotate integer vector v by q quarter turns (+ = counter-clockwise seen from +axis)."""
    x, y, z = v
    for _ in range(q % 4):
        if axis == 0: y, z = -z, y
        elif axis == 1: z, x = -x, z
        else: x, y = -y, x
    return (x, y, z)

class Cube:
    def __init__(self, n=3):
        self.n = n
        m = n - 1                       # coordinates are odd/even ints in [-m, m] step 2
        self.st = {}                    # (pos, normal) -> colour letter
        r = range(-m, m + 1, 2)
        for f, nv in FACES.items():
            ax = [i for i in range(3) if nv[i]][0]
            for a in r:
                for b in r:
                    p = [0, 0, 0]; p[ax] = nv[ax] * m
                    o = [i for i in range(3) if i != ax]
                    p[o[0]] = a; p[o[1]] = b
                    self.st[(tuple(p), nv)] = f

    def copy(self):
        c = Cube.__new__(Cube); c.n = self.n; c.st = dict(self.st); return c

    def _turn(self, axis, layers, q):
        """layers: set of layer coordinates along axis. q quarter turns CCW about +axis."""
        new = {}
        for (p, nv), col in self.st.items():
            if p[axis] in layers:
                new[(_rot(p, axis, q), _rot(nv, axis, q))] = col
            else:
                new[(p, nv)] = col
        self.st = new

    def move(self, mv):
        m = self.n - 1
        g = re.fullmatch(r"([RLUDFBrludfbxyzMES])(w?)(['2]?)", mv)
        if not g: raise ValueError(mv)
        f, w, suf = g.groups()
        k = {"": 1, "'": -1, "2": 2}[suf]
        if f in "xyz":
            axis = "xyz".index(f); self._turn(axis, set(range(-m, m + 1)), -k); return
        if f in "MES":                 # 3x3 slices: M like L, E like D, S like F
            axis, sign = {"M": (0, -1), "E": (1, -1), "S": (2, 1)}[f]
            self._turn(axis, {0}, -sign * k); return
        F = f.upper(); nv = FACES[F]
        axis = [i for i in range(3) if nv[i]][0]; sign = nv[axis]
        outer = sign * m; inner = sign * (m - 2)
        if w: layers = {outer, inner}
        elif f.islower(): layers = {inner}
        else: layers = {outer}
        self._turn(axis, layers, -sign * k)   # clockwise seen from the face

    def apply(self, alg):
        for mv in alg.split():
            self.move(mv)
        return self

    def solved(self):
        faces = {}
        for (p, nv), col in self.st.items():
            faces.setdefault(nv, set()).add(col)
        return all(len(s) == 1 for s in faces.values())

    def face(self, f):
        """Stickers of face f as rows (top-left first) seen from outside, standard net orientation."""
        m = self.n - 1; nv = FACES[f]; r = list(range(-m, m + 1, 2))
        # (right, down) direction vectors when looking at the face
        ori = {"U": ((1, 0, 0), (0, 0, 1)), "D": ((1, 0, 0), (0, 0, -1)), "F": ((1, 0, 0), (0, -1, 0)),
               "B": ((-1, 0, 0), (0, -1, 0)), "R": ((0, 0, -1), (0, -1, 0)), "L": ((0, 0, 1), (0, -1, 0))}[f]
        rows = []
        for b in r:
            row = []
            for a in r:
                p = tuple(nv[i] * m + ori[0][i] * a + ori[1][i] * b for i in range(3))
                row.append(self.st[(p, nv)])
            rows.append(row)
        return rows

def invert(alg):
    out = []
    for mv in reversed(alg.split()):
        out.append(mv[:-1] if mv.endswith("'") else mv if mv.endswith("2") else mv + "'")
    return " ".join(out)

def cube_diff(alg, n=3, pre=""):
    """Set of (pos,normal) stickers whose colour differs after applying alg to a solved cube."""
    a = Cube(n); b = Cube(n).apply(pre + " " + alg if pre else alg)
    return {k for k in a.st if a.st[k] != b.st[k]}

def cubie_positions(keys):
    return {p for p, _ in keys}

# ---------------- SVG drawing (isometric view of U, F, R) ----------------
def cube_svg(cube, mask=None, size=150, label=""):
    """Isometric picture of U, F and R faces. mask(face, row, col, colour) -> colour or 'X' to grey out."""
    n = cube.n
    s = size / (n * 2.0)               # sticker edge
    cx, cy = size / 2, size * 0.52
    # unit vectors on screen
    ex = (math.cos(math.radians(30)) * s, math.sin(math.radians(30)) * s)      # to the right-down
    ez = (-math.cos(math.radians(30)) * s, math.sin(math.radians(30)) * s)     # to the left-down
    ey = (0, -s)                                                                 # up
    def pt(x, y, z):  # x,y,z in sticker units from cube centre (range -n/2..n/2)
        return (cx + x * ex[0] + z * ez[0] + y * ey[0], cy + x * ex[1] + z * ez[1] + y * ey[1])
    polys = []
    h = n / 2
    def quad(f, i, j, col):
        if f == "U":   # rows go toward front (+z), cols toward right (+x)
            c = [(-h + j, h, -h + i), (-h + j + 1, h, -h + i), (-h + j + 1, h, -h + i + 1), (-h + j, h, -h + i + 1)]
        elif f == "F":
            c = [(-h + j, h - i, h), (-h + j + 1, h - i, h), (-h + j + 1, h - i - 1, h), (-h + j, h - i - 1, h)]
        else:          # R: cols go toward back (-z)
            c = [(h, h - i, h - j), (h, h - i, h - j - 1), (h, h - i - 1, h - j - 1), (h, h - i - 1, h - j)]
        d = " ".join(f"{a:.1f},{b:.1f}" for a, b in (pt(*q) for q in c))
        polys.append(f'<polygon points="{d}" fill="{COLOR[col]}" stroke="#1d2330" stroke-width="{max(1.2, s * 0.08):.1f}" stroke-linejoin="round"/>')
    for f in "UFR":
        rows = cube.face(f)
        for i, row in enumerate(rows):
            for j, col in enumerate(row):
                if mask: col = mask(f, i, j, col)
                quad(f, i, j, col)
    return _fit_svg(polys, size, label)

def _fit_svg(polys, size, label, defs=""):
    """Wrap polygons in an svg whose viewBox fits all their points (plus stroke)."""
    nums = [float(v) for poly in polys for pair in re.findall(r'points="([^"]+)"', poly)[0].split() for v in pair.split(",")]
    xs, ys = nums[0::2], nums[1::2]
    pad = 4
    x0, y0, w, h = min(xs) - pad, min(ys) - pad, max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
    sc = size / max(w, h)
    return (f'<svg class="cube-svg" viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}" width="{w * sc:.0f}" height="{h * sc:.0f}" role="img" aria-label="{label}">'
            + defs + "".join(polys) + "</svg>")

def face_svg(rows, size=120, label="", side=None):
    """Flat top-down view of one face (rows of colour letters). side: optional dict
    {'top':[...], 'bottom':[...], 'left':[...], 'right':[...]} of side-sticker colours."""
    n = len(rows); pad = size * 0.12 if side else 2; cell = (size - 2 * pad) / n
    out = []
    for i, row in enumerate(rows):
        for j, col in enumerate(row):
            out.append(f'<rect x="{pad + j * cell:.1f}" y="{pad + i * cell:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="{cell * .12:.1f}" fill="{COLOR[col]}" stroke="#1d2330" stroke-width="2"/>')
    if side:
        t = pad * 0.7
        for k, col in enumerate(side.get("top", [])):
            out.append(f'<rect x="{pad + k * cell + 3:.1f}" y="2" width="{cell - 6:.1f}" height="{t:.1f}" rx="2" fill="{COLOR[col]}" stroke="#1d2330" stroke-width="1.5"/>')
        for k, col in enumerate(side.get("bottom", [])):
            out.append(f'<rect x="{pad + k * cell + 3:.1f}" y="{size - 2 - t:.1f}" width="{cell - 6:.1f}" height="{t:.1f}" rx="2" fill="{COLOR[col]}" stroke="#1d2330" stroke-width="1.5"/>')
        for k, col in enumerate(side.get("left", [])):
            out.append(f'<rect x="2" y="{pad + k * cell + 3:.1f}" width="{t:.1f}" height="{cell - 6:.1f}" rx="2" fill="{COLOR[col]}" stroke="#1d2330" stroke-width="1.5"/>')
        for k, col in enumerate(side.get("right", [])):
            out.append(f'<rect x="{size - 2 - t:.1f}" y="{pad + k * cell + 3:.1f}" width="{t:.1f}" height="{cell - 6:.1f}" rx="2" fill="{COLOR[col]}" stroke="#1d2330" stroke-width="1.5"/>')
    return f'<svg class="cube-svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}" role="img" aria-label="{label}">' + "".join(out) + "</svg>"

# ---------------- Pyraminx ----------------
PCOLOR = {"F": "#009E60", "Lf": "#C41E3A", "Rf": "#0051BA", "D": "#FFD500"}

class Pyraminx:
    """Faces: F (front), Lf (left), Rf (right), D (bottom). Vertices: U (top), L, R, B."""
    def __init__(self):
        # Regular tetrahedron. Choose U top, front face = face opposite B.
        V = {"U": (0.0, 1.0, 0.0)}
        a = math.acos(-1 / 3)                         # angle between vertex directions
        y = math.cos(a); rr = math.sin(a)
        for name, ang in (("L", 330), ("R", 210), ("B", 90)):   # around y axis, front = -z? we set front at +z
            t = math.radians(ang)
            V[name] = (rr * math.cos(t), y, rr * math.sin(t))
        # make front (+z side) contain L and R: L at angle 210 -> x<0,z<0 ; flip z so front is -z? use check below
        self.V = V
        self.faces = {"F": ("U", "L", "R"), "Lf": ("U", "B", "L"), "Rf": ("U", "R", "B"), "D": ("L", "B", "R")}
        self.st = {}
        for f, (A, Bv, C) in self.faces.items():
            for p in self._tri_points(V[A], V[Bv], V[C]):
                self.st[self._key(p)] = (p, f)
        self.canon = [p for p, _ in self.st.values()]
        self.top = 1.0
        self.h = 4 / 3                                  # vertex-to-opposite-face distance (unit circumradius)

    @staticmethod
    def _key(p): return tuple(round(c, 4) for c in p)

    @staticmethod
    def _tri_points(A, B, C):
        """Centroids of the 9 small triangles of face ABC (order-3 subdivision)."""
        pts = []
        def P(i, j):  # barycentric grid point, i+j<=3, weights (3-i-j, i, j)/3 on A,B,C
            k = 3 - i - j
            return tuple((k * A[t] + i * B[t] + j * C[t]) / 3 for t in range(3))
        for i in range(3):
            for j in range(3 - i):
                a, b, c = P(i, j), P(i + 1, j), P(i, j + 1)
                pts.append(tuple((a[t] + b[t] + c[t]) / 3 for t in range(3)))
                if i + j < 2:
                    a, b, c = P(i + 1, j), P(i + 1, j + 1), P(i, j + 1)
                    pts.append(tuple((a[t] + b[t] + c[t]) / 3 for t in range(3)))
        return pts

    def copy(self):
        c = Pyraminx.__new__(Pyraminx); c.__dict__ = dict(self.__dict__); c.st = dict(self.st); return c

    def _turn(self, vname, depth, k):
        v = self.V[vname]
        thr = 1.0 - depth * self.h / 3 + 1e-6         # keep points with dot > thr
        ang = -2 * math.pi / 3 * k                     # clockwise seen from the vertex
        ux, uy, uz = v; c = math.cos(ang); s = math.sin(ang)
        def R(p):
            x, y, z = p
            d = ux * x + uy * y + uz * z
            cx = (uy * z - uz * y, uz * x - ux * z, ux * y - uy * x)
            return tuple(p[i] * c + cx[i] * s + v[i] * d * (1 - c) for i in range(3))
        new = {}
        for key, (p, col) in self.st.items():
            if sum(p[i] * v[i] for i in range(3)) > thr:
                q = R(p); q = min(self.canon, key=lambda c: sum((c[i] - q[i]) ** 2 for i in range(3)))
                new[self._key(q)] = (q, col)
            else:
                new[key] = (p, col)
        assert len(new) == 36
        self.st = new

    def move(self, mv):
        g = re.fullmatch(r"([ULRBulrb])(['2]?)", mv)
        if not g: raise ValueError(mv)
        f, suf = g.groups(); k = {"": 1, "'": -1, "2": 2}[suf]
        self._turn(f.upper(), 1 if f.islower() else 2, k)

    def apply(self, alg):
        for mv in alg.split(): self.move(mv)
        return self

    def face_of(self, p):
        best = None
        for f, (A, B, C) in self.faces.items():
            n = [sum(self.V[x][i] for x in (A, B, C)) for i in range(3)]
            d = sum(p[i] * n[i] for i in range(3))
            if best is None or d > best[0]: best = (d, f)
        return best[1]

    def solved(self):
        s = {}
        for p, col in self.st.values(): s.setdefault(self.face_of(p), set()).add(col)
        return all(len(v) == 1 for v in s.values())

    def piece_kind(self, p):
        """'tip', 'center' or 'edge' for a sticker position."""
        dots = sorted((sum(p[i] * v[i] for i in range(3)) for v in self.V.values()), reverse=True)
        if dots[0] > 1 - self.h / 3 + 1e-6: return "tip"
        if dots[0] > 1 - 2 * self.h / 3 + 1e-6 and dots[1] < 1 - 2 * self.h / 3 - 1e-6: return "center"
        return "edge"

    def diff(self, other):
        return {k for k in self.st if self.st[k][1] != other.st[k][1]}

def pyra_svg(pyr, mask=None, size=170, label=""):
    """Front face flat view (U top, L bottom-left, R bottom-right) with small side strips omitted."""
    A, B, C = (pyr.V[x] for x in pyr.faces["F"])
    # 2D frame for front face
    W = size * 0.92; H = W * math.sqrt(3) / 2; ox = (size - W) / 2; oy = (size - H) / 2
    T2 = {"U": (ox + W / 2, oy), "L": (ox, oy + H), "R": (ox + W, oy + H)}
    def to2d(p):
        # solve barycentric of p in A,B,C via least squares on two edges
        e1 = [B[i] - A[i] for i in range(3)]; e2 = [C[i] - A[i] for i in range(3)]; d = [p[i] - A[i] for i in range(3)]
        a11 = sum(x * x for x in e1); a12 = sum(e1[i] * e2[i] for i in range(3)); a22 = sum(x * x for x in e2)
        b1 = sum(d[i] * e1[i] for i in range(3)); b2 = sum(d[i] * e2[i] for i in range(3))
        det = a11 * a22 - a12 * a12; u = (b1 * a22 - b2 * a12) / det; w = (a11 * b2 - a12 * b1) / det
        return (T2["U"][0] + u * (T2["L"][0] - T2["U"][0]) + w * (T2["R"][0] - T2["U"][0]),
                T2["U"][1] + u * (T2["L"][1] - T2["U"][1]) + w * (T2["R"][1] - T2["U"][1]))
    out = []
    for key, (p, col) in pyr.st.items():
        if pyr.face_of(p) != "F": continue
        c2 = to2d(p)
        # triangle orientation: up-pointing if centroid is in lower 2/3 of its row
        row_h = H / 3; r = int((c2[1] - oy) // row_h); yt = oy + r * row_h
        up = (c2[1] - yt) > row_h / 2
        hw = W / 6
        if up: pts = [(c2[0], yt), (c2[0] - hw, yt + row_h), (c2[0] + hw, yt + row_h)]
        else: pts = [(c2[0] - hw, yt), (c2[0] + hw, yt), (c2[0], yt + row_h)]
        fill = PCOLOR[col] if not mask or mask(pyr, p, col) != "X" else COLOR["X"]
        out.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}" stroke="#1d2330" stroke-width="2.5" stroke-linejoin="round"/>')
    return _fit_svg(out, size, label)

# ---------------- generic sticker puzzles (Megaminx, Helicopter cube) ----------------
def _unit(v):
    l = math.sqrt(sum(x * x for x in v)); return tuple(x / l for x in v)

def _dot(a, b): return sum(x * y for x, y in zip(a, b))

def _rotate(p, axis, ang):
    ux, uy, uz = axis; c, s = math.cos(ang), math.sin(ang); d = _dot(p, axis)
    cx = (uy * p[2] - uz * p[1], uz * p[0] - ux * p[2], ux * p[1] - uy * p[0])
    return tuple(p[i] * c + cx[i] * s + axis[i] * d * (1 - c) for i in range(3))

class GeoPuzzle:
    """Stickers at fixed 3D points; a move turns every sticker whose depth along a move
    axis exceeds a threshold. Moves are stored as index permutations for speed."""
    def __init__(self, pts, colors, axes, depth, ang_unit):
        self.pts = pts; self.home = list(colors); self.state = list(colors)
        self.axes = axes; self.perms = {}
        for name, (axis, q) in axes.items():
            ang = -ang_unit * q                       # clockwise seen from outside
            perm = list(range(len(pts)))
            for i, p in enumerate(pts):
                if _dot(p, axis) > depth:
                    r = _rotate(p, axis, ang)
                    j = min(range(len(pts)), key=lambda k: sum((pts[k][t] - r[t]) ** 2 for t in range(3)))
                    perm[j] = i                       # new[j] = old[i]
            assert sorted(perm) == list(range(len(pts))), name
            self.perms[name] = perm

    def copy(self):
        c = GeoPuzzle.__new__(GeoPuzzle); c.__dict__ = dict(self.__dict__); c.state = list(self.state); return c

    def apply(self, alg):
        for mv in alg.split():
            p = self.perms[mv]; s = self.state; self.state = [s[p[j]] for j in range(len(s))]
        return self

    def solved(self): return self.state == self.home

PHI = (1 + 5 ** .5) / 2

def make_megaminx():
    """Megaminx with face names. Upper ring around U: F, R, BR, BL, L (going right from the front);
    lower ring: DR (below F/R), DBR, DB, DBL, DL (below F/L); D at the bottom."""
    N = []
    for s1 in (1, -1):
        for s2 in (1, -1):
            N += [_unit((0, s1 * PHI, s2)), _unit((s2, 0, s1 * PHI)), _unit((s1 * PHI, s2, 0))]
    V = [s for s in itertools.product((1, -1), repeat=3)]
    for s1 in (1, -1):
        for s2 in (1, -1):
            V += [(0, s1 / PHI, s2 * PHI), (s1 / PHI, s2 * PHI, 0), (s2 * PHI, 0, s1 / PHI)]
    U = N[0]
    ring = [n for n in N if abs(_dot(n, U) - 1 / 5 ** .5) < 1e-6]
    F = ring[0]
    def ang(n, up):   # angle of n around axis up, measured clockwise seen from above (from +up)
        x = _unit(tuple(F[i] - up[i] * _dot(F, up) for i in range(3)))
        y = (up[1] * x[2] - up[2] * x[1], up[2] * x[0] - up[0] * x[2], up[0] * x[1] - up[1] * x[0])
        return math.atan2(_dot(n, y), _dot(n, x)) % (2 * math.pi)
    ring.sort(key=lambda n: ang(n, U))
    names = dict(zip(["F", "R", "BR", "BL", "L"], ring))
    low = [n for n in N if abs(_dot(n, U) + 1 / 5 ** .5) < 1e-6]
    upper = dict(names)
    def touching(n): return {k for k, m in upper.items() if abs(_dot(n, m) - 1 / 5 ** .5) < 1e-6}
    lname = {frozenset({"F", "R"}): "DR", frozenset({"R", "BR"}): "DBR", frozenset({"BR", "BL"}): "DB", frozenset({"BL", "L"}): "DBL", frozenset({"L", "F"}): "DL"}
    for n in low: names[lname[frozenset(touching(n))]] = n
    names["U"] = U; names["D"] = tuple(-x for x in U)
    pts, cols, piece = [], [], []
    rk = lambda v: tuple(round(x, 4) for x in v)
    for fname, n in names.items():
        fv = sorted(V, key=lambda v: -_dot(v, n))[:5]
        c = tuple(sum(v[i] for v in fv) / 5 for i in range(3))
        pts.append(c); cols.append(fname); piece.append(("c", fname))
        for v in fv:
            pts.append(tuple(c[i] + .72 * (v[i] - c[i]) for i in range(3))); cols.append(fname); piece.append(("v", rk(v)))
        for a, b in itertools.combinations(fv, 2):
            if abs(math.dist(a, b) - 2 / PHI) < 1e-6:
                m = tuple((a[i] + b[i]) / 2 for i in range(3))
                pts.append(tuple(c[i] + .82 * (m[i] - c[i]) for i in range(3))); cols.append(fname); piece.append(("e", rk(m)))
    axes = {}
    for fname, n in names.items():
        axes[fname] = (n, 1); axes[fname + "'"] = (n, -1)
        axes[fname + "2"] = (n, 2); axes[fname + "2'"] = (n, -2)
    g = GeoPuzzle(pts, cols, axes, 1.0, 2 * math.pi / 5)
    g.names = names; g.piece = piece
    faces_of = {}
    for i, k in enumerate(piece): faces_of.setdefault(k, set()).add(cols[i])
    g.piece_faces = [frozenset(faces_of[k]) for k in piece]   # faces of the piece each sticker slot belongs to
    return g

HELI_EDGES = {"UF": (0, 1, 1), "UR": (1, 1, 0), "UB": (0, 1, -1), "UL": (-1, 1, 0), "DF": (0, -1, 1), "DR": (1, -1, 0),
              "DB": (0, -1, -1), "DL": (-1, -1, 0), "FR": (1, 0, 1), "FL": (-1, 0, 1), "BR": (1, 0, -1), "BL": (-1, 0, -1)}

def make_helicopter():
    """Helicopter cube on [-1,1]^3. Each face: 4 corner triangles and 4 centre triangles.
    A move (named after an edge, e.g. UF) turns that edge's half 180 degrees."""
    pts, cols = [], []
    for fname, nv in FACES.items():
        ax = [i for i in range(3) if nv[i]][0]; o = [i for i in range(3) if i != ax]
        for a in (1, -1):
            for b in (1, -1):
                for t in (2 / 3, 1 / 3):            # corner triangle, then centre triangle
                    p = [0.0, 0.0, 0.0]; p[ax] = float(nv[ax]); p[o[0]] = a * t; p[o[1]] = b * t
                    pts.append(tuple(p)); cols.append(fname)
    axes = {k: (_unit(v), 1) for k, v in HELI_EDGES.items()}
    return GeoPuzzle(pts, cols, axes, 1 / 2 ** .5 + 1e-6, math.pi)

# ---------------- drawing: Megaminx and Helicopter ----------------
MEGA_COLOR = {"U": "#D7DCE2", "D": "#FFFFFF", "F": "#009E60", "R": "#C41E3A", "BR": "#0051BA", "BL": "#FFD500", "L": "#7B3FA0",
              "DR": "#FF8FC7", "DBR": "#8BD346", "DB": "#FF5800", "DBL": "#5BC0EB", "DL": "#C68E4E", "X": "#5B6573"}

def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

def _mega_polys(g):
    """3D sticker polygons for a Megaminx built by make_megaminx: list of (face, polygon, sticker index)."""
    V = [s for s in itertools.product((1, -1), repeat=3)]
    for s1 in (1, -1):
        for s2 in (1, -1):
            V += [(0, s1 / PHI, s2 * PHI), (s1 / PHI, s2 * PHI, 0), (s2 * PHI, 0, s1 / PHI)]
    out = []
    for fname, nrm in g.names.items():
        fv = sorted(V, key=lambda v: -_dot(v, nrm))[:5]
        c = tuple(sum(v[i] for v in fv) / 5 for i in range(3))
        x = _unit(tuple(fv[0][i] - c[i] for i in range(3))); y = _cross(nrm, x)
        fv.sort(key=lambda v: math.atan2(_dot(tuple(v[i] - c[i] for i in range(3)), y), _dot(tuple(v[i] - c[i] for i in range(3)), x)))
        a = .5
        q = [tuple(c[i] + a * (v[i] - c[i]) for i in range(3)) for v in fv]
        def inter(p1, p2, p3, p4):   # line p1p2 with line p3p4 (coplanar)
            d1 = tuple(p2[i] - p1[i] for i in range(3)); d2 = tuple(p4[i] - p3[i] for i in range(3))
            w = tuple(p3[i] - p1[i] for i in range(3)); cr = _cross(d1, d2); cc = _dot(cr, cr)
            t = _dot(_cross(w, d2), cr) / cc
            return tuple(p1[i] + t * d1[i] for i in range(3))
        X, Y = [], []
        for i in range(5):
            X.append(inter(q[i - 1], q[i], fv[i], fv[(i + 1) % 5]))   # line through q[i-1],q[i] meets edge v_i v_{i+1}
            Y.append(inter(q[(i + 1) % 5], q[i], fv[i - 1], fv[i]))    # line through q[i+1],q[i] meets edge v_{i-1} v_i
        polys = [q]
        for i in range(5):
            polys.append([fv[i], X[i], q[i], Y[i]])
            polys.append([X[i], Y[(i + 1) % 5], q[(i + 1) % 5], q[i]])
        idx = [k for k in range(len(g.pts)) if g.home[k] == fname]
        for poly in polys:
            cen = tuple(sum(p[i] for p in poly) / len(poly) for i in range(3))
            k = min(idx, key=lambda k: sum((g.pts[k][i] - cen[i]) ** 2 for i in range(3)))
            out.append((fname, poly, k))
    return out

def mega_svg(g, view="top", mask=None, size=190, label=""):
    """Orthographic picture of a Megaminx. view 'top' looks down at U and the upper ring from the front;
    'bottom' looks up at the white D face from the front. mask(sticker_index) -> True keeps colour."""
    U = g.names["U"]; F = g.names["F"]
    up = U if view == "top" else tuple(-x for x in U)
    d = _unit(tuple(.95 * up[i] + .75 * F[i] for i in range(3)))       # towards the viewer
    sy = _unit(tuple(up[i] - d[i] * _dot(up, d) for i in range(3)))
    sx = _cross(sy, d)
    if view == "bottom": sx = tuple(-v for v in sx)
    polys = []
    for fname, poly, k in sorted(_mega_polys(g), key=lambda t: _dot(tuple(sum(p[i] for p in t[1]) / len(t[1]) for i in range(3)), d)):
        if _dot(g.names[fname], d) <= .05: continue
        col = g.state[k] if (mask is None or mask(k)) else "X"
        pts = " ".join(f"{_dot(p, sx) * 50:.1f},{-_dot(p, sy) * 50:.1f}" for p in poly)
        polys.append(f'<polygon points="{pts}" fill="{MEGA_COLOR[col]}" stroke="#1d2330" stroke-width="2.2" stroke-linejoin="round"/>')
    return _fit_svg(polys, size, label)

def heli_svg(g, size=170, label="", marks=None):
    """Isometric picture of U, F, R of a Helicopter cube. marks: {sticker index: text} labels."""
    s = size / 4.2; cx, cy = size / 2, size * .52
    ex = (math.cos(math.radians(30)) * s, math.sin(math.radians(30)) * s)
    ez = (-math.cos(math.radians(30)) * s, math.sin(math.radians(30)) * s)
    def P(x, y, z): return (cx + x * ex[0] + z * ez[0], cy + x * ex[1] + z * ez[1] - y * s)
    polys, labels = [], []
    for k, p in enumerate(g.pts):
        nv = [i for i in range(3) if abs(abs(p[i]) - 1) < 1e-9 and all(abs(p[j]) < 1 - 1e-9 for j in range(3) if j != i)]
        if not nv: continue
        ax = nv[0]; sgn = 1 if p[ax] > 0 else -1
        if (ax, sgn) not in ((1, 1), (2, 1), (0, 1)): continue
        o = [i for i in range(3) if i != ax]
        a = 1 if p[o[0]] > 0 else -1; b = 1 if p[o[1]] > 0 else -1
        corner = abs(p[o[0]]) > .5
        tri2 = [(a, b), (a, 0), (0, b)] if corner else [(0, 0), (a, 0), (0, b)]
        pts3 = []
        for u, v in tri2:
            q = [0.0, 0.0, 0.0]; q[ax] = float(sgn); q[o[0]] = u; q[o[1]] = v; pts3.append(P(*q))
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts3)
        polys.append(f'<polygon points="{d}" fill="{COLOR[g.state[k]]}" stroke="#1d2330" stroke-width="{max(1.2, s * .05):.1f}" stroke-linejoin="round"/>')
        if marks and k in marks:
            mx = sum(x for x, _ in pts3) / 3; my = sum(y for _, y in pts3) / 3
            labels.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{s * .17:.1f}" fill="#0F2B46"/><text x="{mx:.1f}" y="{my + s * .07:.1f}" font-size="{s * .2:.1f}" font-weight="700" text-anchor="middle" fill="#fff" font-family="system-ui,sans-serif">{marks[k]}</text>')
    svg = _fit_svg(polys, size, label)
    return svg.replace("</svg>", "".join(labels) + "</svg>")
