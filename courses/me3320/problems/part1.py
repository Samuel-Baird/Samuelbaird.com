"""Original practice problems, units 1-5 (Ch 1-3). All answers computed."""
import math
from common import T, SIGMA, bisect, problem


def build():
    P = {}

    # ---------------------------------------------------------------- Unit 1
    # 1a  convection + radiation from a hot plate
    Ts, Tinf, Tsur, h, eps, A = 90 + 273.15, 25 + 273.15, 25 + 273.15, 18.0, 0.8, 0.5
    qc = h * (Ts - Tinf)
    qr = eps * SIGMA * (Ts ** 4 - Tsur ** 4)
    hr = eps * SIGMA * (Ts + Tsur) * (Ts ** 2 + Tsur ** 2)
    qtot = qc + qr
    Q = qtot * A
    P["u01"] = [problem(
        "1a", "Hot plate: convection plus radiation", "warm-up", 8,
        "A thin flat plate of area $A=0.5\\ \\mathrm{m^2}$ has one face at $T_s=90^\\circ$C, exposed to room air at "
        "$T_\\infty=25^\\circ$C with $h=18\\ \\mathrm{W/m^2K}$ and to large surroundings at $T_{sur}=25^\\circ$C. "
        "The surface emissivity is $\\varepsilon=0.8$. (a) Find the convective and radiative heat fluxes. "
        "(b) Find the radiation heat-transfer coefficient $h_r$ and the total heat rate from the face.",
        ["$T_s=90^\\circ$C", "$T_\\infty=T_{sur}=25^\\circ$C", "$h=18$ W/m²K", "$\\varepsilon=0.8$", "$A=0.5$ m²"],
        ["$q''_{conv}$, $q''_{rad}$", "$h_r$ and $q$ (W)"],
        [T("Convection (Newton): $q''_{conv}=h(T_s-T_\\infty)=18(363.15-298.15)=<<qc:.0f>>\\ \\mathrm{W/m^2}$.", qc=qc),
         T("Radiation uses **absolute** temperatures: $q''_{rad}=\\varepsilon\\sigma(T_s^4-T_{sur}^4)=0.8(5.67\\times10^{-8})(363.15^4-298.15^4)=<<qr:.0f>>\\ \\mathrm{W/m^2}$.", qr=qr),
         T("Linearize radiation: $h_r=\\varepsilon\\sigma(T_s+T_{sur})(T_s^2+T_{sur}^2)=<<hr:.2f>>\\ \\mathrm{W/m^2K}$ — comparable to $h$, so radiation cannot be ignored here.", hr=hr),
         T("Total flux $=<<qtot:.0f>>$ W/m²; $q=q''A=<<Q:.0f>>$ W.", qtot=qtot, Q=Q)],
        [T("$q''_{conv}=<<qc:.0f>>$ W/m²; $q''_{rad}=<<qr:.0f>>$ W/m²", qc=qc, qr=qr), T("$h_r=<<hr:.2f>>$ W/m²K; $q=<<Q:.0f>>$ W", hr=hr, Q=Q)],
        hint="Radiation always needs kelvin. Convection and radiation from the same surface add (parallel paths).")]

    # 1b chip energy balance with radiation (nonlinear -> solve)
    Pel, side, hh, ee, Tinf2 = 2.0, 0.02, 60.0, 0.9, 22 + 273.15
    A2 = side ** 2
    qpp = Pel / A2
    f = lambda Tw_: hh * (Tw_ - Tinf2) + ee * SIGMA * (Tw_ ** 4 - Tinf2 ** 4) - qpp
    Tw = bisect(f, Tinf2, Tinf2 + 400)
    Tconv_only = Tinf2 + qpp / hh
    hr2 = ee * SIGMA * (Tw + Tinf2) * (Tw ** 2 + Tinf2 ** 2)
    TsC, Tco, dT = Tw - 273.15, Tconv_only - 273.15, Tconv_only - Tw
    P["u01"].append(problem(
        "1b", "Chip energy balance (find the surface temperature)", "exam", 15,
        "A square chip, $20\\times20$ mm, dissipates $P=2$ W. Its back and edges are perfectly insulated, so all the power leaves "
        "through the top face to $T_\\infty=22^\\circ$C air ($h=60\\ \\mathrm{W/m^2K}$) and by radiation to surroundings at 22 °C "
        "($\\varepsilon=0.9$). Write the surface energy balance and find the steady surface temperature. "
        "How much error results from ignoring radiation?",
        ["$P=2$ W", "$A=4\\times10^{-4}$ m²", "$h=60$ W/m²K", "$\\varepsilon=0.9$", "$T_\\infty=T_{sur}=22^\\circ$C"],
        ["Surface energy balance", "$T_s$ with radiation", "$T_s$ without radiation"],
        [T("Control surface at the top face: $E_{in}-E_{out}=0$, so $P/A=q''_{conv}+q''_{rad}$, i.e. $P/A=h(T_s-T_\\infty)+\\varepsilon\\sigma(T_s^4-T_{sur}^4)$. Here $P/A=<<qpp:.0f>>$ W/m².", qpp=qpp),
         "The equation is quartic in $T_s$, so iterate (or use the linearized $h_r$): guess $T_s$, compute both fluxes, adjust until they sum to $P/A$.",
         T("Solution: $T_s=<<TsC:.1f>>^\\circ$C (at that temperature $h_r\\approx<<hr2:.2f>>$ W/m²K).", TsC=TsC, hr2=hr2),
         T("Convection only: $T_s=T_\\infty+P/(hA)=<<Tco:.1f>>^\\circ$C. Ignoring radiation overpredicts the surface temperature by about <<dT:.0f>> K.", Tco=Tco, dT=dT)],
        [T("$T_s=<<TsC:.1f>>^\\circ$C with radiation", TsC=TsC), T("$T_s=<<Tco:.1f>>^\\circ$C convection only (error <<dT:.0f>> K)", Tco=Tco, dT=dT)],
        hint="Setting up the balance on the correct control surface is where the points are."))

    # ---------------------------------------------------------------- Unit 2
    k, L = 15.0, 0.10
    a, b, c = 120.0, -1000.0, -20000.0   # T(x) = a + b x + c x^2   [C, x in m]
    qL0 = -k * b                       # q'' at x=0
    qL1 = -k * (b + 2 * c * L)         # q'' at x=L
    qgen = -k * 2 * c                  # W/m3
    chk = (qL1 - qL0) - qgen * L
    P["u02"] = [problem(
        "2a", "Reading a temperature profile", "exam", 12,
        "Steady one-dimensional conduction occurs in a plane wall of thickness $L=0.10$ m and $k=15\\ \\mathrm{W/m\\,K}$. The measured temperature "
        "distribution is $T(x)=120-1000x-20000x^2$ with $T$ in °C and $x$ in m. (a) Find the heat flux at $x=0$ and $x=L$. "
        "(b) Use the heat diffusion equation to find the volumetric generation rate $\\dot q$. (c) Confirm with an overall energy balance on the wall.",
        ["$k=15$ W/m·K", "$L=0.10$ m", "$T(x)=120-1000x-20000x^2$"],
        ["$q''_x(0)$, $q''_x(L)$", "$\\dot q$", "Energy-balance check"],
        [T("Fourier: $q''_x=-k\\,dT/dx=-15(-1000-40000x)$. At $x=0$: $q''=<<q0:.0f>>$ W/m²; at $x=L$: $q''=<<q1:.0f>>$ W/m² (both positive: flow is in $+x$)."),
         T("1-D steady heat equation with generation: $k\\,d^2T/dx^2+\\dot q=0\\Rightarrow\\dot q=-k(2c)=-15(-40000)=<<qg:sci3>>$ W/m³."),
         T("Overall balance (steady): $\\dot E_{in}-\\dot E_{out}+\\dot E_g=0$ per unit area: $q''(0)-q''(L)+\\dot qL=<<chk0:.0f>>-<<chk1:.0f>>+<<chk2:.0f>>=0$ ✓. "
           "More energy leaves at $x=L$ than enters at $x=0$, exactly the generated amount.", chk0=qL0, chk1=qL1, chk2=qgen * L)],
        [T("$q''(0)=<<q0:.0f>>$, $q''(L)=<<q1:.0f>>$ W/m²", q0=qL0, q1=qL1), T("$\\dot q=<<qg:sci3>>$ W/m³", qg=qgen)],
        hint="Differentiate once for the flux, twice for $\\dot q$. A profile with curvature means generation (or variable k).")]
    P["u02"][0]["solution"]["answers"] = [T(s_, q0=qL0, q1=qL1, qg=qgen) for s_ in P["u02"][0]["solution"]["answers"]]
    P["u02"][0]["solution"]["steps"] = [T(s_, q0=qL0, q1=qL1, qg=qgen) for s_ in P["u02"][0]["solution"]["steps"]]

    # 2b cylinder profile
    k2, r0 = 20.0, 0.02
    A_ = 5e5  # T = T0 - A r^2
    qg2 = 4 * A_ * k2
    qs = k2 * 2 * A_ * r0
    qprime = qs * 2 * math.pi * r0
    qprime_gen = qg2 * math.pi * r0 ** 2
    dTc = A_ * r0 ** 2
    P["u02"].append(problem(
        "2b", "Radial profile in a heated rod", "exam", 12,
        "A long solid rod of radius $r_0=20$ mm and $k=20\\ \\mathrm{W/m\\,K}$ has steady radial temperatures $T(r)=T_0-Ar^2$ with $A=5\\times10^{5}\\ \\mathrm{K/m^2}$. "
        "(a) Start from the cylindrical heat equation and find $\\dot q$. (b) Find the surface heat flux and the heat rate per unit length. "
        "(c) Verify with an energy balance. (d) How much hotter is the centerline than the surface?",
        ["$k=20$ W/m·K", "$r_0=0.02$ m", "$T=T_0-Ar^2$, $A=5\\times10^5$ K/m²"],
        ["$\\dot q$", "$q''(r_0)$, $q'$", "Check", "$T(0)-T(r_0)$"],
        [T("Cylindrical, steady, 1-D: $\\dfrac1r\\dfrac{d}{dr}\\!\\left(kr\\dfrac{dT}{dr}\\right)+\\dot q=0$. With $dT/dr=-2Ar$: $r\\,dT/dr=-2Ar^2$, derivative $=-4Ar$, so $\\dot q=4Ak=<<qg:sci3>>$ W/m³."),
         T("Surface flux (outward): $q''(r_0)=-k\\,dT/dr=2Akr_0=<<qs:sci3>>$ W/m²; per unit length $q'=q''(2\\pi r_0)=<<qp:.0f>>$ W/m."),
         T("Energy balance on a unit length: generated $=\\dot q\\pi r_0^2=<<qpg:.0f>>$ W/m $=q'$ ✓."),
         T("$T(0)-T(r_0)=Ar_0^2=<<dTc:.0f>>$ K.")],
        [T("$\\dot q=<<qg:sci3>>$ W/m³"), T("$q''(r_0)=<<qs:sci3>>$ W/m²; $q'=<<qp:.0f>>$ W/m"), T("$\\Delta T=<<dTc:.0f>>$ K")],
        hint="Use the radial form with the $r$ inside the derivative. Check units of $\\dot q$."))
    P["u02"][1]["solution"]["steps"] = [T(s_, qg=qg2, qs=qs, qp=qprime, qpg=qprime_gen, dTc=dTc) for s_ in P["u02"][1]["solution"]["steps"]]
    P["u02"][1]["solution"]["answers"] = [T(s_, qg=qg2, qs=qs, qp=qprime, dTc=dTc) for s_ in P["u02"][1]["solution"]["answers"]]

    # ---------------------------------------------------------------- Unit 3
    # 3a composite wall + contact resistance
    A3 = 1.0
    layers = [("brick", 0.70, 0.120), ("insulation", 0.04, 0.080), ("gypsum", 0.17, 0.0125)]
    hi, ho, Ti, To = 8.0, 25.0, 21.0, -10.0
    Rtc = 0.020  # m2K/W between brick and insulation
    Rs = {"conv_i": 1 / hi}
    for nme, kk, LL in layers:
        Rs[nme] = LL / kk
    Rs["contact"] = Rtc
    Rs["conv_o"] = 1 / ho
    Rtot = sum(Rs.values())
    q3 = (Ti - To) / Rtot
    Ts_i = Ti - q3 * Rs["conv_i"]
    # order inside->outside: conv_i, gypsum? we define wall order from inside: gypsum, insulation, brick(outside)
    # put contact between insulation and brick
    order = ["conv_i", "gypsum", "insulation", "contact", "brick", "conv_o"]
    T_node = [Ti]
    for nm in order:
        T_node.append(T_node[-1] - q3 * Rs[nm])
    P["u03"] = [problem(
        "3a", "Composite wall with contact resistance", "exam", 15,
        "An exterior wall is built, from inside to outside, of gypsum board ($L=12.5$ mm, $k=0.17$), glass-fiber insulation ($L=80$ mm, $k=0.04$) and brick "
        "($L=120$ mm, $k=0.70$; all W/m·K). Imperfect contact between the insulation and brick gives $R''_{t,c}=0.020\\ \\mathrm{m^2K/W}$. "
        "Inside air is $21^\\circ$C with $h_i=8\\ \\mathrm{W/m^2K}$; outside air is $-10^\\circ$C with $h_o=25\\ \\mathrm{W/m^2K}$. "
        "Draw the thermal circuit, then find (a) the heat loss per m², (b) the inside wall-surface temperature, and (c) the temperature drop across the contact resistance.",
        ["gypsum 12.5 mm, k=0.17", "insulation 80 mm, k=0.04", "brick 120 mm, k=0.70", "$R''_{t,c}=0.020$", "$h_i=8$, $h_o=25$", "$T_{\\infty,i}=21^\\circ$C, $T_{\\infty,o}=-10^\\circ$C"],
        ["$q''$", "inside surface temperature", "$\\Delta T$ across contact"],
        ["Series circuit (per m² of wall): $R''_{tot}=\\dfrac1{h_i}+\\dfrac{L_g}{k_g}+\\dfrac{L_{ins}}{k_{ins}}+R''_{t,c}+\\dfrac{L_b}{k_b}+\\dfrac1{h_o}$.",
         T("Numbers: $0.1250+0.0735+2.0000+0.0200+0.1714+0.0400=<<Rtot:.4f>>\\ \\mathrm{m^2K/W}$ (the insulation dominates)."),
         T("$q''=\\dfrac{T_{\\infty,i}-T_{\\infty,o}}{R''_{tot}}=\\dfrac{31}{<<Rtot:.4f>>}=<<q3:.2f>>$ W/m²."),
         T("Inside surface: $T_{s,i}=T_{\\infty,i}-q''/h_i=21-<<q3:.2f>>(0.125)=<<Tsi:.2f>>^\\circ$C."),
         T("Contact drop: $\\Delta T_c=q''R''_{t,c}=<<q3:.2f>>(0.020)=<<dTc:.3f>>$ K. (Interface temperatures on either side: <<Tl:.2f>> °C and <<Tr:.2f>> °C.)")],
        [T("$q''=<<q3:.2f>>$ W/m²"), T("$T_{s,i}=<<Tsi:.2f>>^\\circ$C"), T("$\\Delta T_c=<<dTc:.3f>>$ K")],
        hint="Same $q''$ flows through every series element. $\\Delta T=q''R''$ for each.")]
    sub = dict(Rtot=Rtot, q3=q3, Tsi=Ts_i, dTc=q3 * Rtc, Tl=T_node[3], Tr=T_node[4])
    # T_node indices: 0 Ti, 1 after conv_i(=Ts_i), 2 after gypsum, 3 after insulation (left of contact), 4 after contact, ...
    P["u03"][0]["solution"]["steps"] = [T(s_, **sub) for s_ in P["u03"][0]["solution"]["steps"]]
    P["u03"][0]["solution"]["answers"] = [T(s_, **sub) for s_ in P["u03"][0]["solution"]["answers"]]

    # 3b insulated pipe
    k_i, r1, r2, T1, Tinf3, h3 = 0.05, 0.030, 0.055, 150.0, 20.0, 15.0
    Rcond = math.log(r2 / r1) / (2 * math.pi * k_i)
    Rconv = 1 / (2 * math.pi * r2 * h3)
    qp3 = (T1 - Tinf3) / (Rcond + Rconv)
    Ts_out = Tinf3 + qp3 * Rconv
    r_cr = k_i / h3
    qp_bare = (T1 - Tinf3) / (1 / (2 * math.pi * r1 * h3))
    P["u03"].append(problem(
        "3b", "Insulated steam pipe and critical radius", "exam", 12,
        "A steam pipe of outer radius $r_1=30$ mm has an outer wall at $150^\\circ$C. It is wrapped with insulation ($k=0.05\\ \\mathrm{W/m\\,K}$, outer radius $r_2=55$ mm). "
        "Surrounding air is $20^\\circ$C with a combined (convection+radiation) coefficient $h=15\\ \\mathrm{W/m^2K}$. "
        "(a) Find the heat loss per meter of pipe and the outer insulation-surface temperature. (b) Find the critical radius and say whether this insulation is helping. "
        "(c) Compare with the bare pipe.",
        ["$r_1=0.030$ m, $r_2=0.055$ m", "$k=0.05$ W/m·K", "$T_1=150^\\circ$C", "$T_\\infty=20^\\circ$C, $h=15$"],
        ["$q'$", "$T_{s,2}$", "$r_{cr}$", "bare-pipe $q'$"],
        [T("Radial circuit: $R'_{cond}=\\dfrac{\\ln(r_2/r_1)}{2\\pi k}=<<Rc:.4f>>$ m·K/W; $R'_{conv}=\\dfrac1{2\\pi r_2h}=<<Rv:.4f>>$ m·K/W."),
         T("$q'=\\dfrac{T_1-T_\\infty}{R'_{cond}+R'_{conv}}=\\dfrac{130}{<<Rt:.4f>>}=<<qp:.1f>>$ W/m."),
         T("$T_{s,2}=T_\\infty+q'R'_{conv}=<<Ts2:.1f>>^\\circ$C."),
         T("Critical radius (cylinder) $r_{cr}=k/h=<<rcr:.2f>>$ mm $<r_1=30$ mm, so any added insulation reduces the loss."),
         T("Bare pipe: $q'=h(2\\pi r_1)(T_1-T_\\infty)=<<qb:.0f>>$ W/m, so the insulation cuts the loss by <<red:.0f>>%.")],
        [T("$q'=<<qp:.1f>>$ W/m; $T_{s,2}=<<Ts2:.1f>>^\\circ$C"), T("$r_{cr}=<<rcr:.2f>>$ mm (< $r_1$: insulation helps)"), T("bare: $<<qb:.0f>>$ W/m")],
        hint="In cylindrical coordinates the conduction resistance is a log term per unit length."))
    sub = dict(Rc=Rcond, Rv=Rconv, Rt=Rcond + Rconv, qp=qp3, Ts2=Ts_out, rcr=r_cr * 1000, qb=qp_bare, red=100 * (1 - qp3 / qp_bare))
    P["u03"][1]["solution"]["steps"] = [T(s_, **sub) for s_ in P["u03"][1]["solution"]["steps"]]
    P["u03"][1]["solution"]["answers"] = [T(s_, **sub) for s_ in P["u03"][1]["solution"]["answers"]]

    # ---------------------------------------------------------------- Unit 4
    kw, Lw, qdot, hh4, Tinf4 = 25.0, 0.020, 2e6, 1000.0, 100.0
    Ts4 = Tinf4 + qdot * Lw / hh4
    T04 = Ts4 + qdot * Lw ** 2 / (2 * kw)
    P["u04"] = [problem(
        "4a", "Plane wall with generation, convection both sides", "exam", 15,
        "A wall of thickness $2L=40$ mm ($k=25$ W/m·K) generates $\\dot q=2\\times10^6\\ \\mathrm{W/m^3}$ uniformly. Both surfaces see fluid at $100^\\circ$C with $h=1000\\ \\mathrm{W/m^2K}$. "
        "(a) Derive $T(x)$ using the midplane as $x=0$. (b) Find the surface and midplane temperatures. (c) Where is the maximum temperature?",
        ["$L=0.020$ m", "$k=25$", "$\\dot q=2\\times10^6$ W/m³", "$h=1000$, $T_\\infty=100^\\circ$C"],
        ["$T(x)$", "$T_s$, $T_0$", "location of $T_{max}$"],
        ["$k\\,T''+\\dot q=0$, so $T=-\\dfrac{\\dot q}{2k}x^2+C_1x+C_2$. Symmetry ($dT/dx|_0=0$) gives $C_1=0$.",
         T("Surface energy balance at $x=L$: heat conducted to the surface equals heat convected away, $\\dot qL=h(T_s-T_\\infty)$, so $T_s=T_\\infty+\\dot qL/h=<<Ts:.1f>>^\\circ$C."),
         T("$T(x)=T_s+\\dfrac{\\dot q}{2k}(L^2-x^2)$, so $T_0=T_s+\\dfrac{\\dot qL^2}{2k}=<<T0:.1f>>^\\circ$C."),
         "Maximum temperature is at the midplane $x=0$ (symmetry, adiabatic there)."],
        [T("$T_s=<<Ts:.1f>>^\\circ$C"), T("$T_0=<<T0:.1f>>^\\circ$C at $x=0$")],
        hint="Do the energy balance at the surface instead of fighting the second boundary condition algebraically.")]
    sub = dict(Ts=Ts4, T0=T04)
    P["u04"][0]["solution"]["steps"] = [T(s_, **sub) for s_ in P["u04"][0]["solution"]["steps"]]
    P["u04"][0]["solution"]["answers"] = [T(s_, **sub) for s_ in P["u04"][0]["solution"]["answers"]]

    # 4b electric wire
    rho_e, D, I, k4, h4, Tinf5 = 1.08e-6, 3e-3, 30.0, 20.0, 100.0, 25.0
    Ac = math.pi * D ** 2 / 4
    Rp = rho_e / Ac
    qp4 = I ** 2 * Rp
    qd4 = qp4 / Ac
    Ts5 = Tinf5 + qp4 / (math.pi * D * h4)
    dT5 = qd4 * (D / 2) ** 2 / (4 * k4)
    P["u04"].append(problem(
        "4b", "Current-carrying wire", "exam", 12,
        "A long nichrome wire ($D=3$ mm, $k=20$ W/m·K, electrical resistivity $\\rho_e=1.08\\times10^{-6}\\ \\Omega\\,$m) carries $I=30$ A in $25^\\circ$C air with $h=100\\ \\mathrm{W/m^2K}$. "
        "Find (a) $\\dot q$, (b) the surface temperature, and (c) the centerline-to-surface temperature difference. Which resistance dominates?",
        ["$D=3$ mm", "$I=30$ A", "$\\rho_e=1.08\\times10^{-6}\\ \\Omega$m", "$k=20$", "$h=100$, $T_\\infty=25^\\circ$C"],
        ["$\\dot q$", "$T_s$", "$T_0-T_s$"],
        [T("$A_c=\\pi D^2/4=<<Ac:sci3>>$ m²; $R'_e=\\rho_e/A_c=<<Rp:.4f>>\\ \\Omega$/m; power per length $q'=I^2R'_e=<<qp:.1f>>$ W/m; $\\dot q=q'/A_c=<<qd:sci3>>$ W/m³."),
         T("Steady: all generated heat leaves by convection: $q'=h\\pi D(T_s-T_\\infty)$, so $T_s=T_\\infty+\\dfrac{q'}{\\pi Dh}=<<Ts:.1f>>^\\circ$C."),
         T("Solid cylinder with generation: $T_0-T_s=\\dfrac{\\dot qr_o^2}{4k}=<<dT:.2f>>$ K."),
         "Convection resistance dominates by a factor of several hundred: the wire is essentially isothermal."],
        [T("$\\dot q=<<qd:sci3>>$ W/m³"), T("$T_s=<<Ts:.1f>>^\\circ$C"), T("$T_0-T_s=<<dT:.2f>>$ K")],
        hint="Convert current into $\\dot q$ first. Surface energy balance sets $T_s$, conduction only sets the small internal rise."))
    sub = dict(Ac=Ac, Rp=Rp, qp=qp4, qd=qd4, Ts=Ts5, dT=dT5)
    P["u04"][1]["solution"]["steps"] = [T(s_, **sub) for s_ in P["u04"][1]["solution"]["steps"]]
    P["u04"][1]["solution"]["answers"] = [T(s_, **sub) for s_ in P["u04"][1]["solution"]["answers"]]

    # ---------------------------------------------------------------- Unit 5
    kf, Df, Lf, hf, Tinf6, Tb = 200.0, 0.004, 0.040, 50.0, 25.0, 120.0
    Pf = math.pi * Df
    Acf = math.pi * Df ** 2 / 4
    m = math.sqrt(hf * Pf / (kf * Acf))
    th = Tb - Tinf6
    M = math.sqrt(hf * Pf * kf * Acf) * th
    mL = m * Lf
    g = hf / (m * kf)
    q_conv_tip = M * (math.sinh(mL) + g * math.cosh(mL)) / (math.cosh(mL) + g * math.sinh(mL))
    Lc = Lf + Df / 4
    q_corr = M * math.tanh(m * Lc)
    q_adia = M * math.tanh(mL)
    Af = Pf * Lf + Acf
    eta = q_conv_tip / (hf * Af * th)
    P["u05"] = [problem(
        "5a", "Pin fin: heat rate and efficiency", "exam", 15,
        "An aluminum pin fin ($k=200$ W/m·K) has diameter $D=4$ mm and length $L=40$ mm. Its base is at $120^\\circ$C and the air is $25^\\circ$C with $h=50\\ \\mathrm{W/m^2K}$ (also acting on the tip). "
        "(a) Find $m$ and $mL$. (b) Find the heat rate with the convective tip, and compare with the adiabatic-tip and corrected-length approximations. (c) Find the fin efficiency.",
        ["$k=200$, $D=4$ mm, $L=40$ mm", "$h=50$", "$T_b=120^\\circ$C, $T_\\infty=25^\\circ$C"],
        ["$m$, $mL$", "$q_f$ (three ways)", "$\\eta_f$"],
        [T("$P=\\pi D$, $A_c=\\pi D^2/4$. $m=\\sqrt{hP/(kA_c)}=\\sqrt{4h/(kD)}=<<m:.2f>>\\ \\mathrm{m^{-1}}$, so $mL=<<mL:.3f>>$. $M=\\sqrt{hPkA_c}\\,\\theta_b=<<M:.3f>>$ W."),
         T("Convective tip: $q_f=M\\dfrac{\\sinh mL+(h/mk)\\cosh mL}{\\cosh mL+(h/mk)\\sinh mL}$ with $h/mk=<<g:.4f>>$, giving $q_f=<<qct:.3f>>$ W."),
         T("Adiabatic tip: $M\\tanh mL=<<qa:.3f>>$ W (a <<ea:.1f>>% underprediction). Corrected length $L_c=L+D/4=<<Lc:.4f>>$ m: $M\\tanh mL_c=<<qc:.3f>>$ W (within <<ec:.2f>>% of the exact convective-tip value)."),
         T("Efficiency: $\\eta_f=q_f/(hA_f\\theta_b)$ with $A_f=\\pi DL+\\pi D^2/4=<<Af:sci3>>$ m², so $\\eta_f=<<eta:.3f>>$.")],
        [T("$q_f=<<qct:.3f>>$ W (convective tip)"), T("$q_f\\approx<<qc:.3f>>$ W (corrected length)"), T("$\\eta_f=<<eta:.3f>>$")],
        hint="Corrected length is the fastest accurate shortcut on an exam.")]
    sub = dict(m=m, mL=mL, M=M, g=g, qct=q_conv_tip, qa=q_adia, ea=100 * (1 - q_adia / q_conv_tip), Lc=Lc, qc=q_corr,
               ec=100 * abs(q_corr - q_conv_tip) / q_conv_tip, Af=Af, eta=eta)
    P["u05"][0]["solution"]["steps"] = [T(s_, **sub) for s_ in P["u05"][0]["solution"]["steps"]]
    P["u05"][0]["solution"]["answers"] = [T(s_, **sub) for s_ in P["u05"][0]["solution"]["answers"]]

    # 5b array
    N, W = 25, 0.10
    Ab = W * W
    Aunf = Ab - N * Acf
    q_arr = N * q_conv_tip + hf * Aunf * th
    q_bare = hf * Ab * th
    eff = q_arr / q_bare
    P["u05"].append(problem(
        "5b", "Finned surface vs bare surface", "exam", 12,
        "A $100\\times100$ mm base plate at $120^\\circ$C carries $N=25$ of the pin fins from Problem 5a (same $h$, air at $25^\\circ$C). "
        "Find the total heat rate, the heat rate from the bare plate without fins, and the overall effectiveness of the finned surface. "
        "Is adding fins worthwhile at this $h$?",
        ["25 fins from 5a", "$A_b=0.01$ m²", "$h=50$ W/m²K", "$\\theta_b=95$ K"],
        ["$q_{tot}$", "$q_{bare}$", "$\\varepsilon$"],
        [T("Unfinned base area: $A_u=A_b-N A_{c}=0.01-25(<<Ac:sci3>>)=<<Au:.5f>>$ m²."),
         T("$q_{tot}=Nq_f+hA_u\\theta_b=25(<<qf:.3f>>)+50(<<Au:.5f>>)(95)=<<qt:.1f>>$ W."),
         T("Bare plate: $q=hA_b\\theta_b=<<qb:.1f>>$ W."),
         T("Effectiveness $=q_{tot}/q_{bare}=<<eff:.2f>>$. Fins pay off here because $h$ is low (natural/forced air); with a liquid at high $h$ the gain would shrink.")],
        [T("$q_{tot}=<<qt:.1f>>$ W; $q_{bare}=<<qb:.1f>>$ W; $\\varepsilon=<<eff:.2f>>$")],
        hint="Subtract the fin footprint from the base area before computing the unfinned convection."))
    sub = dict(Ac=Acf, Au=Aunf, qf=q_conv_tip, qt=q_arr, qb=q_bare, eff=eff)
    P["u05"][1]["solution"]["steps"] = [T(s_, **sub) for s_ in P["u05"][1]["solution"]["steps"]]
    P["u05"][1]["solution"]["answers"] = [T(s_, **sub) for s_ in P["u05"][1]["solution"]["answers"]]
    return P


if __name__ == "__main__":
    import json, sys
    sys.stdout.reconfigure(encoding="utf-8")
    d = build()
    for u, ps in d.items():
        for p in ps:
            print(u, p["id"], "|", " || ".join(p["solution"]["answers"]))
