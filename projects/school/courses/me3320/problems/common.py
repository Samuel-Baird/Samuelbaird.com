"""Shared helpers for the original ME 3320 practice problems.

Every published number in a solution is computed here, never typed by hand.
Templating: write text with <<name>> or <<name:.3g>> and pass values as keyword args, so
KaTeX braces never collide with Python format strings.
"""
import math, re

SIGMA = 5.67e-8  # W/m^2 K^4
G = 9.81


def T(s, **kw):
    """Fill <<name:fmt>> placeholders. Default format is .4g."""
    def rep(m):
        name, fmt = m.group(1), m.group(2) or ".4g"
        if name not in kw:          # leave for a later pass; build.py rejects any leftover <<...>>
            return m.group(0)
        if fmt.startswith("sci"):   # TeX scientific notation, e.g. sci3 -> 1.95\times10^{7}
            digs = int(fmt[3:] or 3) - 1
            mant, exp = f"{kw[name]:.{digs}e}".split("e")
            return f"{mant}\\times10^{{{int(exp)}}}"
        return format(kw[name], fmt)
    return re.sub(r"<<(\w+)(?::([^>]+))?>>", rep, s)


def bisect(f, lo, hi, tol=1e-10, it=200):
    flo = f(lo)
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def bessel_j(n, x, terms=60):
    """Bessel function of the first kind, integer order, power series (fine for x < ~10)."""
    s = 0.0
    for k in range(terms):
        s += ((-1) ** k) * (x / 2) ** (2 * k + n) / (math.factorial(k) * math.factorial(k + n))
    return s


def planck_fraction(lam_T_um_K):
    """F(0 -> lambda*T): fraction of blackbody emission below lambda*T (um*K). Numerical integral."""
    c2 = 14387.77  # um K
    x_end = c2 / lam_T_um_K

    def f(x):
        return x ** 3 / (math.exp(x) - 1.0) if x > 0 else 0.0
    # integrate from x_end (short wavelengths -> large x) to infinity of x^3/(e^x-1) dx
    # F = 15/pi^4 * integral_{x_end}^{inf} f(x) dx
    n, hi = 20000, 60.0
    a, b = x_end, max(hi, x_end + 1)
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += f(a + i * h) * (4 if i % 2 else 2)
    return 15 / math.pi ** 4 * s * h / 3


def fill(p, **kw):
    """Fill remaining <<placeholders>> in a problem's solution text with computed values."""
    p["solution"]["steps"] = [T(s, **kw) for s in p["solution"]["steps"]]
    p["solution"]["answers"] = [T(s, **kw) for s in p["solution"]["answers"]]
    return p


def problem(pid, title, level, minutes, statement, given, find, steps, answers, hint=None):
    return {
        "id": pid, "title": title, "level": level, "minutes": minutes,
        "statement": statement, "given": given, "find": find,
        "hint": hint, "solution": {"steps": steps, "answers": answers},
    }
