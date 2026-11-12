"""Original warm-up problems (5-8 minutes, one idea each) for units 6-18, so every unit has an easy first step
before the exam-style problems (playbook rule 5). All answers computed. Ids end in 'w' and sort first in their unit."""
import math
from common import T, SIGMA, bisect, problem, fill

AIR300 = "air at 300 K: $k=0.0263$ W/m·K, $\\nu=15.89\\times10^{-6}$ m²/s, $Pr=0.707$"
WATER300 = "water at 300 K: $k=0.613$ W/m·K, $\\nu=0.855\\times10^{-6}$ m²/s, $\\mu=855\\times10^{-6}$ kg/m·s, $Pr=5.83$"


def zeta_wall(Bi):
    return bisect(lambda z: z * math.tan(z) - Bi, 1e-9, math.pi / 2 - 1e-9)


def build():
    W = {}

    # ---- u06: shape factor given S (resistance form)
    D, k, T1, T2 = 0.50, 1.5, 80.0, 20.0
    S = 2 * math.pi * D
    q = S * k * (T1 - T2)
    W["u06"] = fill(problem(
        "6w", "Hot sphere in a large soil mass (resistance form)", "warm-up", 6,
        "A spherical heat source of diameter $D=0.50$ m is buried deep in soil of $k=1.5$ W/m·K, far from any surface, so the soil acts as an infinite medium. The sphere surface is at $80^\\circ$C and the soil far away is at $20^\\circ$C. "
        "Find the shape factor, the conduction resistance and the heat rate. What happens to the heat rate if $D$ doubles?",
        ["$D=0.50$ m", "$k=1.5$ W/m·K", "$T_1=80^\\circ$C, $T_2=20^\\circ$C"],
        ["$S$", "$R$ and $q$", "effect of doubling $D$"],
        [T("Isothermal sphere in an infinite medium (Table 4.1): $S=2\\pi D=<<S:.3f>>$ m."),
         T("$R=\\dfrac{1}{Sk}=<<R:.4f>>$ K/W and $q=Sk(T_1-T_2)=<<q:.1f>>$ W."),
         T("$S\\propto D$, so doubling $D$ doubles the heat rate to <<q2:.1f>> W.")],
        [T("$S=<<S:.3f>>$ m"), T("$R=<<R:.4f>>$ K/W, $q=<<q:.0f>>$ W"), "$q$ doubles"],
        hint="Shape factor $S$ has units of length; resistance is $1/(Sk)$."),
        S=S, R=1 / (S * k), q=q, q2=2 * q)

    # ---- u07: interior node with generation
    nb, qd, dx, kk = [80.0, 60.0, 70.0, 90.0], 5e5, 0.01, 20.0
    g = qd * dx ** 2 / kk
    Tn = (sum(nb) + g) / 4
    W["u07"] = fill(problem(
        "7w", "Interior node with generation", "warm-up", 6,
        "An interior node of a square grid ($\\Delta x=\\Delta y=10$ mm) has neighbors at $80$, $60$, $70$ and $90^\\circ$C. The material has $k=20$ W/m·K and generates heat uniformly at $\\dot q=5\\times10^5\\ \\mathrm{W/m^3}$. "
        "Write the nodal equation and find the node temperature (steady state).",
        ["neighbors: 80, 60, 70, 90 °C", "$\\Delta x=\\Delta y=0.010$ m", "$k=20$ W/m·K", "$\\dot q=5\\times10^5$ W/m³"],
        ["Nodal equation", "$T_{m,n}$"],
        ["Energy balance on the node's cell: $T_{up}+T_{down}+T_{left}+T_{right}-4T_{m,n}+\\dfrac{\\dot q\\,\\Delta x^2}{k}=0$.",
         T("Generation term: $\\dot q\\Delta x^2/k=<<g:.2f>>$ K. Sum of neighbors $=<<sm:.0f>>$."),
         T("$T_{m,n}=\\dfrac{<<sm:.0f>>+<<g:.2f>>}{4}=<<Tn:.2f>>^\\circ$C (a bit above the plain average of <<avg:.1f>>$^\\circ$C because of generation).")],
        [T("$T_{m,n}=<<Tn:.1f>>^\\circ$C")],
        hint="Without generation the node is the average of its neighbors; generation adds $\\dot q\\Delta x^2/k$ to the sum."),
        g=g, sm=sum(nb), Tn=Tn, avg=sum(nb) / 4)

    # ---- u08: Biot screening of three bodies
    cases = [("copper sphere", 0.010, 50.0, 401.0), ("stainless-steel sphere", 0.050, 500.0, 15.0), ("glass sphere", 0.020, 100.0, 1.4)]
    rows = [(n, d, h, kk_, d / 6, h * (d / 6) / kk_) for n, d, h, kk_ in cases]
    W["u08"] = fill(problem(
        "8w", "Which bodies can be treated as lumped?", "warm-up", 6,
        "Three spheres start hot and are cooled by a fluid. (A) copper, $D=10$ mm, $k=401$ W/m·K, $h=50$ W/m²K. (B) stainless steel, $D=50$ mm, $k=15$ W/m·K, $h=500$ W/m²K. (C) glass, $D=20$ mm, $k=1.4$ W/m·K, $h=100$ W/m²K. "
        "For each, find the Biot number and decide whether lumped capacitance is valid.",
        ["A: $D=10$ mm, $k=401$, $h=50$", "B: $D=50$ mm, $k=15$, $h=500$", "C: $D=20$ mm, $k=1.4$, $h=100$"],
        ["$L_c$ and $Bi$ for each", "valid or not"],
        ["For a sphere $L_c=V/A_s=D/6$ (not the radius). Then $Bi=hL_c/k$ and compare with 0.1.",
         T("A: $L_c=<<lA:.5f>>$ m, $Bi=<<bA:sci3>>$, " + "valid. B: $L_c=<<lB:.5f>>$ m, $Bi=<<bB:.3f>>$, not valid. C: $L_c=<<lC:.5f>>$ m, $Bi=<<bC:.3f>>$, not valid."),
         "Conductive solids with small $h$ are lumped; poor conductors or large $h$ need the spatial (one-term or numerical) methods."],
        [T("A: $Bi=<<bA:sci3>>$ — lumped"), T("B: $Bi=<<bB:.3f>>$ — not lumped"), T("C: $Bi=<<bC:.3f>>$ — not lumped")],
        hint="Use $L_c=V/A_s$; for a sphere that is $D/6$."),
        lA=rows[0][4], bA=rows[0][5], lB=rows[1][4], bB=rows[1][5], lC=rows[2][4], bC=rows[2][5])

    # ---- u09: Bi/Fo screening, then center temperature
    Lw, kw, al, hw, tw, Tiw, Tinfw = 0.025, 20.0, 5e-6, 200.0, 60.0, 300.0, 20.0
    Bi9, Fo9 = hw * Lw / kw, al * tw / Lw ** 2
    z1 = zeta_wall(Bi9)
    C1 = 4 * math.sin(z1) / (2 * z1 + math.sin(2 * z1))
    th0 = C1 * math.exp(-z1 ** 2 * Fo9)
    To = Tinfw + th0 * (Tiw - Tinfw)
    W["u09"] = fill(problem(
        "9w", "Pick the transient model, then the center temperature", "warm-up", 8,
        "A plane wall of thickness $2L=50$ mm ($k=20$ W/m·K, $\\alpha=5\\times10^{-6}$ m²/s) at $300^\\circ$C is suddenly exposed on both faces to fluid at $20^\\circ$C with $h=200$ W/m²K. "
        "(a) Compute $Bi$ and $Fo$ at $t=60$ s and say which model applies (lumped, one-term, or neither). (b) Find the center temperature.",
        ["$L=0.025$ m", "$k=20$, $\\alpha=5\\times10^{-6}$", "$h=200$, $T_\\infty=20^\\circ$C", "$T_i=300^\\circ$C, $t=60$ s"],
        ["$Bi$, $Fo$ and model", "$T_0$ at $t=60$ s"],
        [T("$Bi=hL/k=<<Bi:.3f>>>0.1$, so lumped capacitance is not valid. $Fo=\\alpha t/L^2=<<Fo:.3f>>>0.2$, so the one-term series is valid."),
         T("Solve $\\zeta_1\\tan\\zeta_1=Bi$: $\\zeta_1=<<z1:.4f>>$ rad; $C_1=\\dfrac{4\\sin\\zeta_1}{2\\zeta_1+\\sin2\\zeta_1}=<<C1:.4f>>$ (matches Table 5.1)."),
         T("$\\theta_o^*=C_1e^{-\\zeta_1^2Fo}=<<th0:.4f>>$, so $T_0=T_\\infty+\\theta_o^*(T_i-T_\\infty)=<<To:.1f>>^\\circ$C.")],
        [T("$Bi=<<Bi:.2f>>$, $Fo=<<Fo:.2f>>$ — one-term series"), T("$T_0=<<To:.0f>>^\\circ$C")],
        hint="Both numbers use the half-thickness $L$, not $V/A$."),
        Bi=Bi9, Fo=Fo9, z1=z1, C1=C1, th0=th0, To=To)

    # ---- u11: dimensionless groups from measured data
    nu, kf, Pr, u, L, hh = 0.855e-6, 0.613, 5.83, 2.0, 0.20, 3000.0
    Re = u * L / nu
    Nu = hh * L / kf
    St = Nu / (Re * Pr)
    W["u11"] = fill(problem(
        "11w", "Dimensionless groups from a measurement", "warm-up", 6,
        f"Water flows at $u_\\infty=2.0$ m/s over a plate of length $L=0.20$ m and the measured average coefficient is $\\bar h=3000$ W/m²K. Use {WATER300}. "
        "Compute $Re_L$, $\\overline{Nu}_L$ and the Stanton number, and say whether the thermal boundary layer is thicker or thinner than the velocity boundary layer.",
        ["$u_\\infty=2.0$ m/s, $L=0.20$ m", "$\\bar h=3000$ W/m²K", WATER300],
        ["$Re_L$", "$\\overline{Nu}_L$, $St$", "$\\delta_t$ vs $\\delta$"],
        [T("$Re_L=u_\\infty L/\\nu=<<Re:sci3>>$ (just below the $5\\times10^5$ transition)."),
         T("$\\overline{Nu}_L=\\bar hL/k=<<Nu:.1f>>$ and $St=\\dfrac{Nu}{RePr}=<<St:sci3>>$."),
         "Because $Pr=5.83>1$, momentum diffuses faster than heat, so $\\delta_t<\\delta$ ($\\delta_t/\\delta\\sim Pr^{-1/3}$)."],
        [T("$Re_L=<<Re:sci3>>$"), T("$Nu=<<Nu:.0f>>$, $St=<<St:sci3>>$"), "$\\delta_t<\\delta$"],
        hint="$St=Nu/(Re\\,Pr)=h/(\\rho u_\\infty c_p)$."),
        Re=Re, Nu=Nu, St=St)

    # ---- u12: laminar flat-plate average h
    uu, LL, dT, wid = 2.0, 0.5, 30.0, 1.0
    nua, ka, Pra = 15.89e-6, 0.0263, 0.707
    ReL = uu * LL / nua
    NuL = 0.664 * ReL ** 0.5 * Pra ** (1 / 3)
    hbar = NuL * ka / LL
    qq = hbar * (LL * wid) * dT
    W["u12"] = fill(problem(
        "12w", "Laminar flat plate: average h and heat rate", "warm-up", 6,
        f"Air at $u_\\infty=2$ m/s flows along a flat plate $L=0.5$ m long and $1$ m wide, held $30$ K above the air. Use {AIR300}. "
        "Check the flow regime, find $\\bar h$ and the heat rate from one face.",
        ["$u_\\infty=2$ m/s, $L=0.5$ m, width 1 m", "$T_s-T_\\infty=30$ K", AIR300],
        ["$Re_L$ and regime", "$\\bar h$", "$q$"],
        [T("$Re_L=u_\\infty L/\\nu=<<Re:.0f>><5\\times10^5$, laminar over the whole plate."),
         T("$\\overline{Nu}_L=0.664Re_L^{1/2}Pr^{1/3}=<<Nu:.1f>>$, so $\\bar h=\\overline{Nu}_Lk/L=<<h:.2f>>$ W/m²K."),
         T("$q=\\bar hA\\Delta T=<<h:.2f>>(0.5)(30)=<<q:.0f>>$ W.")],
        [T("$Re_L=<<Re:sci3>>$ (laminar)"), T("$\\bar h=<<h:.2f>>$ W/m²K"), T("$q=<<q:.0f>>$ W")],
        hint="Laminar average correlation: $0.664\\,Re_L^{1/2}Pr^{1/3}$ — twice the local value at $x=L$."),
        Re=ReL, Nu=NuL, h=hbar, q=qq)

    # ---- u13: Hilpert, choose the right Re band
    Vc, Dc, dTc = 4.0, 0.020, 40.0
    Rec = Vc * Dc / nua
    C, m = 0.193, 0.618
    Nuc = C * Rec ** m * Pra ** (1 / 3)
    hc = Nuc * ka / Dc
    qlin = hc * math.pi * Dc * dTc
    W["u13"] = fill(problem(
        "13w", "Cylinder in cross flow with the Hilpert correlation", "warm-up", 7,
        f"Air at $V=4$ m/s crosses a long cylinder of diameter $D=20$ mm whose surface is $40$ K above the air. Use {AIR300} and the Hilpert correlation $\\overline{{Nu}}_D=C\\,Re_D^mPr^{{1/3}}$ with the Table 7.2 rows: "
        "$40<Re_D<4000$: $C=0.683$, $m=0.466$; $4000<Re_D<40000$: $C=0.193$, $m=0.618$. Find $Re_D$, choose the row, then find $\\bar h$ and the heat loss per meter.",
        ["$V=4$ m/s, $D=20$ mm", "$T_s-T_\\infty=40$ K", AIR300],
        ["$Re_D$ and the row", "$\\bar h$", "$q'$"],
        [T("$Re_D=VD/\\nu=<<Re:.0f>>$, which lies in the $4000$–$40000$ band: $C=0.193$, $m=0.618$."),
         T("$\\overline{Nu}_D=0.193\\,Re_D^{0.618}Pr^{1/3}=<<Nu:.1f>>$, so $\\bar h=<<h:.1f>>$ W/m²K."),
         T("$q'=\\bar h\\pi D\\Delta T=<<ql:.0f>>$ W/m.")],
        [T("$Re_D=<<Re:.0f>>$ → row 4000–40000"), T("$\\bar h=<<h:.1f>>$ W/m²K"), T("$q'=<<ql:.0f>>$ W/m")],
        hint="Compute $Re_D$ first; it decides which $(C,m)$ row to use."),
        Re=Rec, Nu=Nuc, h=hc, ql=qlin)

    # ---- u14: internal flow Re and Dittus-Boelter
    mdot, Di, mu, kw2, Prw = 0.20, 0.025, 855e-6, 0.613, 5.83
    Red = 4 * mdot / (math.pi * Di * mu)
    Nud = 0.023 * Red ** 0.8 * Prw ** 0.4
    hd = Nud * kw2 / Di
    W["u14"] = fill(problem(
        "14w", "Internal flow: regime and Dittus–Boelter", "warm-up", 6,
        f"Water ($\\dot m=0.20$ kg/s) is heated inside a tube of inner diameter $D=25$ mm. Use properties at the mean temperature: {WATER300}. "
        "Find $Re_D$, say whether the flow is laminar or turbulent, and estimate $\\bar h$ with Dittus–Boelter (heating).",
        ["$\\dot m=0.20$ kg/s, $D=25$ mm", WATER300, "heating"],
        ["$Re_D$ and regime", "$Nu_D$, $\\bar h$", "entry length (turbulent)"],
        [T("$Re_D=\\dfrac{4\\dot m}{\\pi D\\mu}=<<Re:.0f>>>10^4$, fully turbulent."),
         T("Heating, $n=0.4$: $Nu_D=0.023Re_D^{4/5}Pr^{0.4}=<<Nu:.1f>>$, so $\\bar h=Nu_Dk/D=<<h:.0f>>$ W/m²K."),
         T("Turbulent entry length is about $10D=<<ent:.2f>>$ m; the correlation applies after that.")],
        [T("$Re_D=<<Re:.0f>>$ (turbulent)"), T("$\\bar h=<<h:.0f>>$ W/m²K")],
        hint="Use the mean-temperature properties, and $n=0.4$ for heating."),
        Re=Red, Nu=Nud, h=hd, ent=10 * Di)

    # ---- u15: C_min, C_r, q_max, NTU
    mh, cph, mc, cpc, Thi, Tci, UA = 0.5, 2100.0, 0.3, 4180.0, 120.0, 20.0, 1500.0
    Ch, Cc = mh * cph, mc * cpc
    Cmin, Cmax = min(Ch, Cc), max(Ch, Cc)
    Cr = Cmin / Cmax
    qmax = Cmin * (Thi - Tci)
    NTU = UA / Cmin
    which = "hot oil" if Ch < Cc else "cold water"
    W["u15"] = fill(problem(
        "15w", "Capacity rates, q_max and NTU", "warm-up", 6,
        "Hot oil ($\\dot m=0.5$ kg/s, $c_p=2100$ J/kg·K) enters a heat exchanger at $120^\\circ$C and cold water ($\\dot m=0.3$ kg/s, $c_p=4180$ J/kg·K) enters at $20^\\circ$C. The exchanger has $UA=1500$ W/K. "
        "Find $C_{min}$, $C_r$, the maximum possible heat rate and NTU. Which stream has the larger temperature change?",
        ["oil: $\\dot m=0.5$, $c_p=2100$, $T_{h,i}=120^\\circ$C", "water: $\\dot m=0.3$, $c_p=4180$, $T_{c,i}=20^\\circ$C", "$UA=1500$ W/K"],
        ["$C_{min}$, $C_r$", "$q_{max}$", "NTU"],
        [T("$C_h=\\dot m c_p=<<Ch:.0f>>$ W/K and $C_c=<<Cc:.0f>>$ W/K, so $C_{min}=<<Cmin:.0f>>$ W/K (<<which:s>>) and $C_r=C_{min}/C_{max}=<<Cr:.3f>>$."),
         T("$q_{max}=C_{min}(T_{h,i}-T_{c,i})=<<qmax:.0f>>$ W."),
         T("$NTU=UA/C_{min}=<<NTU:.3f>>$. The $C_{min}$ stream (<<which:s>>) has the larger temperature change because the same $q$ is carried by a smaller $C$.")],
        [T("$C_{min}=<<Cmin:.0f>>$ W/K, $C_r=<<Cr:.3f>>$"), T("$q_{max}=<<qmax:.0f>>$ W"), T("$NTU=<<NTU:.3f>>$")],
        hint="$C_{min}$ is the smaller of $\\dot m c_p$ for the two streams, whichever fluid that is."),
        Ch=Ch, Cc=Cc, Cmin=Cmin, Cr=Cr, qmax=qmax, NTU=NTU, which=which)

    # ---- u16: Rayleigh number, regime, why kelvin
    Ts16, Tinf16, L16 = 350.0, 300.0, 0.40
    nu16, al16, k16, Pr16 = 18.4e-6, 26.2e-6, 0.0282, 0.703
    Tf16 = (Ts16 + Tinf16) / 2
    g = 9.81
    Ra = g * (1 / Tf16) * (Ts16 - Tinf16) * L16 ** 3 / (nu16 * al16)
    beta_bad = 1 / (Tf16 - 273.15)
    Ra_bad = g * beta_bad * (Ts16 - Tinf16) * L16 ** 3 / (nu16 * al16)
    Nu16 = 0.68 + 0.670 * Ra ** 0.25 / (1 + (0.492 / Pr16) ** (9 / 16)) ** (4 / 9)
    h16 = Nu16 * k16 / L16
    W["u16"] = fill(problem(
        "16w", "Rayleigh number and flow regime", "warm-up", 7,
        "A vertical plate $L=0.40$ m tall at $350$ K stands in still air at $300$ K. Use air properties at the film temperature: $\\nu=18.4\\times10^{-6}$ m²/s, $\\alpha=26.2\\times10^{-6}$ m²/s, $k=0.0282$ W/m·K, $Pr=0.703$. "
        "Compute $Ra_L$ (treating air as an ideal gas), decide laminar or turbulent, and find $\\bar h$ with the laminar Churchill–Chu form. What error would using °C in $\\beta$ cause?",
        ["$T_s=350$ K, $T_\\infty=300$ K, $L=0.40$ m", "$\\nu=18.4\\times10^{-6}$, $\\alpha=26.2\\times10^{-6}$", "$k=0.0282$, $Pr=0.703$"],
        ["$Ra_L$ and regime", "$\\bar h$", "effect of using °C"],
        [T("$T_f=<<Tf:.0f>>$ K, $\\beta=1/T_f=<<beta:sci3>>$ K$^{-1}$. $Ra_L=\\dfrac{g\\beta\\Delta TL^3}{\\nu\\alpha}=<<Ra:sci3>>$, below $10^9$, so the boundary layer is laminar."),
         T("$\\overline{Nu}_L=0.68+\\dfrac{0.670Ra_L^{1/4}}{[1+(0.492/Pr)^{9/16}]^{4/9}}=<<Nu:.1f>>$, so $\\bar h=<<h:.2f>>$ W/m²K."),
         T("Using °C would give $\\beta=1/<<TfC:.0f>>=<<bb:.4f>>$, overstating $Ra_L$ by a factor of <<fac:.1f>>.")],
        [T("$Ra_L=<<Ra:sci3>>$ (laminar)"), T("$\\bar h=<<h:.2f>>$ W/m²K")],
        hint="$\\beta=1/T_f$ requires kelvin."),
        Tf=Tf16, beta=1 / Tf16, Ra=Ra, Nu=Nu16, h=h16, TfC=Tf16 - 273.15, bb=beta_bad, fac=Ra_bad / Ra)

    # ---- u17: absorbed / reflected / radiosity bookkeeping
    Ts17, eps17, G17 = 500.0, 0.6, 800.0
    Eb17 = SIGMA * Ts17 ** 4
    E17 = eps17 * Eb17
    rho17 = 1 - eps17
    J17 = E17 + rho17 * G17
    W["u17"] = fill(problem(
        "17w", "Irradiation, absorption and radiosity", "warm-up", 6,
        "An opaque, diffuse, gray surface at $500$ K has emissivity $\\varepsilon=0.6$ and receives irradiation $G=800\\ \\mathrm{W/m^2}$. "
        "Find the absorbed and reflected irradiation, the emissive power, the radiosity and the net radiative flux leaving the surface.",
        ["$T_s=500$ K, $\\varepsilon=0.6$", "$G=800$ W/m²", "opaque, diffuse, gray"],
        ["$\\alpha G$, $\\rho G$", "$E$, $J$", "net flux"],
        ["Gray and diffuse means $\\alpha=\\varepsilon=0.6$; opaque means $\\rho=1-\\alpha=0.4$.",
         T("Absorbed $\\alpha G=<<abs:.0f>>$ W/m²; reflected $\\rho G=<<ref:.0f>>$ W/m². $E=\\varepsilon\\sigma T^4=<<E:.1f>>$ W/m²."),
         T("Radiosity $J=E+\\rho G=<<J:.1f>>$ W/m². Net flux leaving the surface $q''=J-G=E-\\alpha G=<<net:.1f>>$ W/m².")],
        [T("$J=<<J:.0f>>$ W/m²"), T("$q''=<<net:.0f>>$ W/m²")],
        hint="Radiosity is everything leaving: emitted plus reflected."),
        abs=eps17 * G17, ref=rho17 * G17, E=E17, J=J17, net=J17 - G17)

    # ---- u18: reciprocity and summation, concentric spheres
    D1, D2, T1s, T2s = 0.20, 0.50, 600.0, 300.0
    A1, A2 = math.pi * D1 ** 2, math.pi * D2 ** 2
    F21 = A1 / A2
    q12 = A1 * SIGMA * (T1s ** 4 - T2s ** 4)
    W["u18"] = fill(problem(
        "18w", "Concentric spheres: reciprocity and summation", "warm-up", 6,
        "A black sphere of diameter $D_1=0.20$ m sits inside a larger black spherical shell of diameter $D_2=0.50$ m. Find $F_{11}$, $F_{12}$, $F_{21}$ and $F_{22}$. "
        "If the inner sphere is at $600$ K and the shell at $300$ K, find the net radiation from the inner sphere.",
        ["$D_1=0.20$ m, $D_2=0.50$ m", "$T_1=600$ K, $T_2=300$ K", "both black"],
        ["$F_{11},F_{12},F_{21},F_{22}$", "$q_{12}$"],
        ["The inner sphere is convex and fully enclosed: $F_{11}=0$ and, by summation, $F_{12}=1$.",
         T("Reciprocity: $F_{21}=A_1F_{12}/A_2=(D_1/D_2)^2=<<F21:.2f>>$. Summation for the shell: $F_{22}=1-F_{21}=<<F22:.2f>>$."),
         T("$q_{12}=A_1\\sigma(T_1^4-T_2^4)=<<A1:.4f>>(5.67\\times10^{-8})(<<dT4:sci3>>)=<<q:.0f>>$ W.")],
        ["$F_{11}=0$, $F_{12}=1$", T("$F_{21}=<<F21:.2f>>$, $F_{22}=<<F22:.2f>>$"), T("$q_{12}=<<q:.0f>>$ W")],
        hint="Flat or convex surfaces cannot see themselves: $F_{ii}=0$."),
        F21=F21, F22=1 - F21, A1=A1, dT4=T1s ** 4 - T2s ** 4, q=q12)
    return {uid: [p] for uid, p in W.items()}


if __name__ == "__main__":
    import json
    for uid, lst in build().items():
        for p in lst:
            txt = json.dumps(p)
            assert "<<" not in txt and "nan" not in txt.lower(), p["id"]
            print(p["id"], p["title"], "|", " ; ".join(p["solution"]["answers"])[:150])
