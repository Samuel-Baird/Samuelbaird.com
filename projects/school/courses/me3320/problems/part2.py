"""Original practice problems, units 6-11 (Ch 4-6). All answers computed."""
import math
from common import T, SIGMA, bisect, bessel_j, problem, fill

AIR300 = "air at 300 K: $k=0.0263$ W/m·K, $\\nu=15.89\\times10^{-6}$ m²/s, $Pr=0.707$"


def solve_linear(A, b):
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[piv] = M[piv], M[i]
        for r in range(i + 1, n):
            f = M[r][i] / M[i][i]
            for c in range(i, n + 1):
                M[r][c] -= f * M[i][c]
    x = [0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x


def zeta_wall(Bi):
    return bisect(lambda z: z * math.tan(z) - Bi, 1e-9, math.pi / 2 - 1e-9)


def zeta_cyl(Bi):
    return bisect(lambda z: z * bessel_j(1, z) / bessel_j(0, z) - Bi, 1e-9, 2.404)


def build():
    P = {}

    # ---------------------------------------------------------------- Unit 6 (Ch 4.1-4.3)
    L, D, z, k, T1, T2 = 30.0, 0.20, 1.5, 1.0, 60.0, 5.0
    S_cosh = 2 * math.pi * L / math.acosh(2 * z / D)
    S_ln = 2 * math.pi * L / math.log(4 * z / D)
    q = S_cosh * k * (T1 - T2)
    P["u06"] = [fill(problem(
        "6a", "Buried pipe (Table 4.1, horizontal cylinder)", "exam", 10,
        "A hot-water pipe of diameter $D=0.20$ m and length $L=30$ m is buried with its axis $z=1.5$ m below the ground surface. The pipe wall is at $60^\\circ$C, the ground surface is held at $5^\\circ$C and the soil has $k=1.0$ W/m·K. "
        "Find the shape factor and the heat loss. Compare the exact $\\cosh^{-1}$ expression with the $\\ln(4z/D)$ approximation.",
        ["$D=0.20$ m, $L=30$ m, $z=1.5$ m", "$k=1.0$ W/m·K", "$T_1=60^\\circ$C, $T_2=5^\\circ$C"],
        ["$S$", "$q$", "check approximate form"],
        ["Two-dimensional conduction between two isothermal boundaries, so $q=Sk(T_1-T_2)$. Table 4.1, horizontal isothermal cylinder in a semi-infinite medium ($L\\gg D$): $S=\\dfrac{2\\pi L}{\\cosh^{-1}(2z/D)}$.",
         T("$2z/D=15$, $\\cosh^{-1}(15)=<<ac:.4f>>$, so $S=<<S:.2f>>$ m. Approximation ($z>3D/2$ ✓): $S=2\\pi L/\\ln(4z/D)=<<S2:.2f>>$ m (<<err:.2f>>% off)."),
         T("$q=Sk(T_1-T_2)=<<S:.2f>>(1.0)(55)=<<q:.0f>>$ W, i.e. <<qpl:.1f>> W per meter of pipe.")],
        [T("$S=<<S:.2f>>$ m"), T("$q=<<q:.0f>>$ W")],
        hint="Use the ratio $2z/D$, not $z/D$, inside the $\\cosh^{-1}$ expression."),
        ac=math.acosh(15), S=S_cosh, S2=S_ln, err=100 * abs(S_ln - S_cosh) / S_cosh, q=q, qpl=q / L),
        fill(problem(
        "6b", "Buried spherical tank (Table 4.1, sphere)", "exam", 10,
        "A spherical tank of diameter $D=2$ m contains a process fluid so that its wall is at $40^\\circ$C. The center is $z=4$ m below a ground surface at $10^\\circ$C; the soil has $k=1.2$ W/m·K. "
        "Find the heat loss. By what percentage would you misestimate it if you treated the soil as an infinite medium?",
        ["$D=2$ m, $z=4$ m", "$k=1.2$ W/m·K", "$\\Delta T=30$ K"],
        ["$q$", "error of infinite-medium shortcut"],
        [T("Table 4.1, isothermal sphere in a semi-infinite medium ($z>D/2$): $S=\\dfrac{2\\pi D}{1-D/4z}=\\dfrac{<<num:.3f>>}{1-0.125}=<<S:.2f>>$ m."),
         T("$q=Sk\\Delta T=<<S:.2f>>(1.2)(30)=<<q:.0f>>$ W."),
         T("Infinite medium: $S=2\\pi D=<<Sinf:.2f>>$ m, a <<d:.1f>>% underestimate — the nearby surface (at $10^\\circ$C) increases the loss.")],
        [T("$q=<<q:.0f>>$ W"), T("infinite-medium shortcut is <<d:.1f>>% low")],
        hint="Both cases-1-through-4 formulas appear in Table 4.1, which the study guide says to know."),
        num=2 * math.pi * 2, S=2 * math.pi * 2 / (1 - 2 / 16), q=2 * math.pi * 2 / (1 - 2 / 16) * 1.2 * 30,
        Sinf=2 * math.pi * 2, d=100 * (1 - (2 * math.pi * 2) / (2 * math.pi * 2 / (1 - 2 / 16))))]

    # ---------------------------------------------------------------- Unit 7 (Ch 4.4-4.5)
    # 2x2 interior, top edge 100, other edges 0
    A_ = [[4, -1, -1, 0], [-1, 4, 0, -1], [-1, 0, 4, -1], [0, -1, -1, 4]]
    b_ = [100, 100, 0, 0]
    x1, x2, x3, x4 = solve_linear(A_, b_)
    Bi, Tinf_, Tu, Td, Tin = 0.5, 20.0, 90.0, 90.0, 85.0
    Ts_node = (Tu + Td + 2 * Tin + 2 * Bi * Tinf_) / (2 * (Bi + 2))
    P["u07"] = [fill(problem(
        "7a", "Four-node finite-difference solution", "exam", 15,
        "A square plate has its top edge held at $100^\\circ$C and its left, right and bottom edges at $0^\\circ$C. The plate is discretized with $\\Delta x=\\Delta y$ so that there are four interior nodes: "
        "nodes 1 (top-left) and 2 (top-right) in the top row, nodes 3 (bottom-left) and 4 (bottom-right) in the bottom row (each one grid spacing from its neighboring edges). "
        "Write the finite-difference equation for each node and solve for the temperatures. Use symmetry as a check.",
        ["interior nodes 1–4", "$T_{top}=100^\\circ$C", "other edges $0^\\circ$C", "$\\Delta x=\\Delta y$, no generation"],
        ["Node equations", "$T_1,\\dots,T_4$"],
        ["Interior node, no generation: $T_{m,n}=\\tfrac14(T_{m+1,n}+T_{m-1,n}+T_{m,n+1}+T_{m,n-1})$.",
         "Node 1: $4T_1=100+0+T_2+T_3$. Node 2: $4T_2=100+0+T_1+T_4$. Node 3: $4T_3=T_1+0+0+T_4$. Node 4: $4T_4=T_2+0+T_3+0$.",
         "Symmetry about the vertical centerline gives $T_1=T_2=a$, $T_3=T_4=b$: $3a-b=100$ and $3b=a$.",
         T("$b=<<b:.2f>>$, $a=<<a:.2f>>$. Direct solve of the 4×4 system: $T_1=<<x1:.2f>>$, $T_2=<<x2:.2f>>$, $T_3=<<x3:.2f>>$, $T_4=<<x4:.2f>>$ °C (matches symmetry).")],
        [T("$T_1=T_2=<<a:.1f>>^\\circ$C"), T("$T_3=T_4=<<b:.1f>>^\\circ$C")],
        hint="One equation per unknown; exploit symmetry to reduce to 2×2."),
        a=x1, b=x3, x1=x1, x2=x2, x3=x3, x4=x4),
        fill(problem(
        "7b", "Convective boundary node", "exam", 12,
        "A node lies on a plane surface exposed to fluid at $T_\\infty=20^\\circ$C with $Bi=h\\Delta x/k=0.5$. Its two neighbors along the surface (above and below) are at $90^\\circ$C each, and its interior neighbor (one $\\Delta x$ into the solid) is at $85^\\circ$C. "
        "Derive the energy balance for the node and find its temperature. No generation, steady state.",
        ["$Bi=0.5$", "$T_\\infty=20^\\circ$C", "neighbors: 90, 90 (along surface), 85 (interior)"],
        ["Node equation", "$T_{surface\\ node}$"],
        ["Control volume is a half-cell of size $\\Delta x/2\\times\\Delta y$: conduction in from the interior neighbor (full height) and from the two side neighbors (half height each), plus convection from the fluid.",
         "Energy balance: $\\;T_{up}+T_{down}+2T_{in}+2Bi\\,T_\\infty-2(Bi+2)T_{node}=0$.",
         T("$90+90+2(85)+2(0.5)(20)-2(2.5)T=0\\Rightarrow 370=5T\\Rightarrow T_{node}=<<Tn:.1f>>^\\circ$C.")],
        [T("$T_{node}=<<Tn:.1f>>^\\circ$C")],
        hint="Remember the factor of 2 on the interior neighbor and the $Bi$ term; the corner-node version has different coefficients."),
        Tn=Ts_node)]

    # ---------------------------------------------------------------- Unit 8 (Ch 5.1-5.3)
    rho, c, kk, Dd, hh, Ti, Tinf, Tf = 7800.0, 470.0, 44.0, 0.025, 300.0, 500.0, 40.0, 100.0
    Lc = Dd / 6
    Bi8 = hh * Lc / kk
    tau = rho * c * Lc / hh
    th_ratio = (Ti - Tinf) / (Tf - Tinf)
    t8 = tau * math.log(th_ratio)
    V = math.pi * Dd ** 3 / 6
    Q8 = rho * V * c * (Ti - Tf)
    P["u08"] = [fill(problem(
        "8a", "Quenching a steel ball (lumped capacitance)", "exam", 12,
        "A steel sphere ($\\rho=7800$ kg/m³, $c=470$ J/kg·K, $k=44$ W/m·K) of diameter $25$ mm at $500^\\circ$C is quenched in an oil bath at $40^\\circ$C with $h=300\\ \\mathrm{W/m^2K}$. "
        "(a) Check whether the lumped-capacitance method is valid. (b) Find the time constant and the time to reach $100^\\circ$C. (c) How much energy has left the ball by then?",
        ["$\\rho=7800$, $c=470$, $k=44$", "$D=25$ mm", "$T_i=500^\\circ$C, $T_\\infty=40^\\circ$C", "$h=300$"],
        ["$Bi$", "$\\tau$, $t$", "$Q$"],
        [T("$L_c=V/A_s=D/6=<<Lc:.5f>>$ m, $Bi=hL_c/k=<<Bi:.4f>>$ < 0.1, so lumped capacitance is valid."),
         T("$\\tau_t=\\dfrac{\\rho Vc}{hA_s}=\\dfrac{\\rho cL_c}{h}=<<tau:.1f>>$ s. From $\\dfrac{T-T_\\infty}{T_i-T_\\infty}=e^{-t/\\tau_t}$: $t=\\tau_t\\ln\\dfrac{460}{60}=<<t:.1f>>$ s."),
         T("$V=<<V:sci3>>$ m³; $Q=\\rho Vc(T_i-T)=<<Q:.0f>>$ J (≈ <<Qk:.1f>> kJ).")],
        [T("$Bi=<<Bi:.3f>>$ (valid)"), T("$\\tau_t=<<tau:.1f>>$ s; $t=<<t:.0f>>$ s"), T("$Q=<<Qk:.1f>>$ kJ")],
        hint="Characteristic length is $V/A_s$, not the radius. Always compute $Bi$ first."),
        Lc=Lc, Bi=Bi8, tau=tau, t=t8, V=V, Q=Q8, Qk=Q8 / 1000)]
    # 8b plate
    rho2, c2, k2, th2, h2, Ti2, Tinf2, Tf2 = 2700.0, 900.0, 237.0, 0.002, 35.0, 200.0, 25.0, 60.0
    Lc2 = th2 / 2
    Bi2 = h2 * Lc2 / k2
    tau2 = rho2 * c2 * Lc2 / h2
    t2 = tau2 * math.log((Ti2 - Tinf2) / (Tf2 - Tinf2))
    tau2b = tau2 / 2
    t2b = tau2b * math.log((Ti2 - Tinf2) / (Tf2 - Tinf2))
    frac3 = math.exp(-3)
    P["u08"].append(fill(problem(
        "8b", "Thin plate cooling in air", "exam", 12,
        "A thin aluminum plate ($\\rho=2700$, $c=900$ J/kg·K, $k=237$ W/m·K), $2$ mm thick, at $200^\\circ$C is suddenly exposed on both faces to air at $25^\\circ$C with $h=35\\ \\mathrm{W/m^2K}$ (neglect edges and radiation). "
        "(a) Show that the plate is effectively isothermal. (b) Find the time to cool to $60^\\circ$C. (c) What happens to that time if $h$ is doubled? (d) What fraction of the initial temperature difference remains after $3\\tau_t$?",
        ["thickness 2 mm, both faces", "$\\rho=2700$, $c=900$, $k=237$", "$T_i=200^\\circ$C, $T_\\infty=25^\\circ$C, $h=35$"],
        ["$Bi$", "$t$", "effect of $2h$", "$\\theta/\\theta_i$ at $3\\tau$"],
        [T("Both faces exposed: $L_c=V/A_s=(\\text{thickness})/2=<<Lc:.4f>>$ m. $Bi=hL_c/k=<<Bi:sci3>>\\ll0.1$ ✓ (isothermal)."),
         T("$\\tau_t=\\rho cL_c/h=<<tau:.1f>>$ s; $t=\\tau_t\\ln\\dfrac{175}{35}=\\tau_t\\ln5=<<t:.0f>>$ s (≈ <<tm:.1f>> min)."),
         T("Doubling $h$ halves $\\tau_t$ and so halves the time: $t=<<t2:.0f>>$ s."),
         T("$\\theta/\\theta_i=e^{-3}=<<f3:.3f>>$ — about 5% of the initial difference remains.")],
        [T("$Bi=<<Bi:sci2>>$"), T("$t=<<t:.0f>>$ s"), T("$t=<<t2:.0f>>$ s with $2h$"), T("$e^{-3}=<<f3:.3f>>$")],
        hint="Two exposed faces: the characteristic length is half the thickness."),
        Lc=Lc2, Bi=Bi2, tau=tau2, t=t2, tm=t2 / 60, t2=t2b, f3=frac3))

    # ---------------------------------------------------------------- Unit 9 (Ch 5.4-5.6)
    # plane wall
    L9, k9, al9, h9, Ti9, Tinf9, t9 = 0.05, 1.2, 6e-7, 100.0, 20.0, 400.0, 1800.0
    Bi9 = h9 * L9 / k9
    z9 = zeta_wall(Bi9)
    C9 = 4 * math.sin(z9) / (2 * z9 + math.sin(2 * z9))
    Fo9 = al9 * t9 / L9 ** 2
    th0 = C9 * math.exp(-z9 ** 2 * Fo9)
    T0_9 = Tinf9 + th0 * (Ti9 - Tinf9)
    Ts9 = Tinf9 + th0 * math.cos(z9) * (Ti9 - Tinf9)
    QQ = 1 - math.sin(z9) / z9 * th0
    rhoc9 = k9 / al9
    Q09 = rhoc9 * 2 * L9 * abs(Ti9 - Tinf9)
    P["u09"] = [fill(problem(
        "9a", "Heating a slab: one-term solution (plane wall)", "exam", 18,
        "A concrete-like slab of thickness $2L=100$ mm ($k=1.2$ W/m·K, $\\alpha=6\\times10^{-7}\\ \\mathrm{m^2/s}$) is initially uniform at $20^\\circ$C and is suddenly exposed on both faces to gas at $400^\\circ$C with $h=100\\ \\mathrm{W/m^2K}$. "
        "After $t=30$ min find (a) the midplane temperature, (b) the surface temperature, and (c) the energy absorbed per unit area. State whether the one-term approximation is valid. "
        "(Solve the eigenvalue equation $\\zeta\\tan\\zeta=Bi$ or interpolate Table 5.1.)",
        ["$L=0.05$ m, $k=1.2$, $\\alpha=6\\times10^{-7}$", "$h=100$", "$T_i=20^\\circ$C, $T_\\infty=400^\\circ$C", "$t=1800$ s"],
        ["$T(0,t)$", "$T(L,t)$", "$Q$ per area"],
        [T("$Bi=hL/k=<<Bi:.3f>>$ (not lumped — spatial gradients matter). $Fo=\\alpha t/L^2=<<Fo:.3f>>>0.2$ ✓ so one term is accurate."),
         T("First root of $\\zeta_1\\tan\\zeta_1=Bi$: $\\zeta_1=<<z:.4f>>$ rad, $C_1=\\dfrac{4\\sin\\zeta_1}{2\\zeta_1+\\sin2\\zeta_1}=<<C:.4f>>$."),
         T("Midplane: $\\theta_0^*=C_1e^{-\\zeta_1^2Fo}=<<th0:.4f>>$, so $T_0=T_\\infty+\\theta_0^*(T_i-T_\\infty)=<<T0:.1f>>^\\circ$C."),
         T("Surface ($x^*=1$): $\\theta^*=\\theta_0^*\\cos\\zeta_1=<<ths:.4f>>$, $T_s=<<Ts:.1f>>^\\circ$C."),
         T("Energy: $Q/Q_o=1-\\dfrac{\\sin\\zeta_1}{\\zeta_1}\\theta_0^*=<<QQ:.4f>>$ with $Q_o=\\rho c(2L)(T_\\infty-T_i)=<<Q0:sci3>>$ J/m² (using $\\rho c=k/\\alpha$), so $Q=<<Q:sci3>>$ J/m².")],
        [T("$T_0=<<T0:.0f>>^\\circ$C; $T_s=<<Ts:.0f>>^\\circ$C"), T("$Q=<<Q:sci3>>$ J/m² (<<QQ:.1%>> of the maximum)")],
        hint="Check $Fo>0.2$ before trusting the one-term form. Surface values use $\\cos(\\zeta_1x^*)$ at $x^*=1$."),
        Bi=Bi9, Fo=Fo9, z=z9, C=C9, th0=th0, T0=T0_9, ths=th0 * math.cos(z9), Ts=Ts9, QQ=QQ, Q0=Q09, Q=QQ * Q09)]
    # cylinder
    r0, k10, al10, h10, Ti10, Tinf10, t10 = 0.03, 15.0, 3.9e-6, 250.0, 600.0, 30.0, 100.0
    Bi10 = h10 * r0 / k10
    z10 = zeta_cyl(Bi10)
    J0, J1 = bessel_j(0, z10), bessel_j(1, z10)
    C10 = 2 * J1 / (z10 * (J0 ** 2 + J1 ** 2))
    Fo10 = al10 * t10 / r0 ** 2
    th10 = C10 * math.exp(-z10 ** 2 * Fo10)
    T010 = Tinf10 + th10 * (Ti10 - Tinf10)
    Ts10 = Tinf10 + th10 * J0 * (Ti10 - Tinf10)
    # sanity: known table values at Bi=1
    zc1 = zeta_cyl(1.0)
    assert abs(zc1 - 1.2558) < 2e-3, zc1
    zw1 = zeta_wall(1.0)
    assert abs(zw1 - 0.8603) < 2e-3, zw1
    P["u09"].append(fill(problem(
        "9b", "Cooling a long steel cylinder", "exam", 18,
        "A long steel cylinder of radius $r_o=30$ mm ($k=15$ W/m·K, $\\alpha=3.9\\times10^{-6}\\ \\mathrm{m^2/s}$) leaves a furnace at $600^\\circ$C and is cooled in air at $30^\\circ$C with $h=250\\ \\mathrm{W/m^2K}$. "
        "After $t=100$ s find the centerline and surface temperatures. Is lumped capacitance acceptable? "
        "(One-term series for a cylinder: $\\theta^*=C_1e^{-\\zeta_1^2Fo}J_0(\\zeta_1r^*)$ with $\\zeta_1J_1(\\zeta_1)/J_0(\\zeta_1)=Bi$.)",
        ["$r_o=0.03$ m, $k=15$, $\\alpha=3.9\\times10^{-6}$", "$h=250$", "$T_i=600^\\circ$C, $T_\\infty=30^\\circ$C", "$t=100$ s"],
        ["lumped check", "$T(0,t)$", "$T(r_o,t)$"],
        [T("$Bi=hr_o/k=<<Bi:.3f>>$. With $L_c=r_o/2$, $Bi_{lump}=<<Bil:.3f>>>0.1$, so lumped capacitance is **not** acceptable."),
         T("$Fo=\\alpha t/r_o^2=<<Fo:.3f>>>0.2$ ✓. Solve $\\zeta_1J_1/J_0=Bi$: $\\zeta_1=<<z:.4f>>$; $C_1=\\dfrac{2J_1(\\zeta_1)}{\\zeta_1[J_0^2(\\zeta_1)+J_1^2(\\zeta_1)]}=<<C:.4f>>$."),
         T("$\\theta_0^*=C_1e^{-\\zeta_1^2Fo}=<<th:.4f>>$, so $T_0=<<T0:.1f>>^\\circ$C."),
         T("Surface: $\\theta^*=\\theta_0^*J_0(\\zeta_1)=<<ths:.4f>>$, $T_s=<<Ts:.1f>>^\\circ$C (a <<dT:.0f>> K gradient across the cylinder).")],
        [T("$T_0=<<T0:.0f>>^\\circ$C"), T("$T_s=<<Ts:.0f>>^\\circ$C")],
        hint="For a cylinder the characteristic length in the lumped check is $r_o/2$, but the Heisler/one-term $Bi$ uses $r_o$."),
        Bi=Bi10, Bil=h10 * (r0 / 2) / k10, Fo=Fo10, z=z10, C=C10, th=th10, T0=T010, ths=th10 * J0, Ts=Ts10, dT=T010 - Ts10))

    # ---------------------------------------------------------------- Unit 10 (Ch 5.7, 5.10)
    Ts_s, Ti_s, al_s, t_s = -15.0, 5.0, 0.5e-6, 30 * 24 * 3600.0
    ratio = (0 - Ts_s) / (Ti_s - Ts_s)
    eta = bisect(lambda e: math.erf(e) - ratio, 0, 3)
    x_front = 2 * eta * math.sqrt(al_s * t_s)
    # contact temperature
    def eff(kv, rv, cv): return math.sqrt(kv * rv * cv)
    e_skin, e_tile, e_wood = eff(0.37, 1000, 3500), eff(1.0, 2000, 800), eff(0.15, 700, 1600)
    Tc_tile = (e_skin * 33 + e_tile * 18) / (e_skin + e_tile)
    Tc_wood = (e_skin * 33 + e_wood * 18) / (e_skin + e_wood)
    P["u10"] = [fill(problem(
        "10a", "Frost penetration into soil (semi-infinite solid)", "exam", 12,
        "Soil initially at $T_i=5^\\circ$C (thermal diffusivity $\\alpha=0.5\\times10^{-6}\\ \\mathrm{m^2/s}$) has its surface suddenly held at $T_s=-15^\\circ$C for 30 days. "
        "Ignoring latent heat, how deep is the $0^\\circ$C isotherm? Write the solution you use and the similarity variable.",
        ["$T_i=5^\\circ$C", "$T_s=-15^\\circ$C", "$\\alpha=5\\times10^{-7}$ m²/s", "$t=30$ d $=2.592\\times10^6$ s"],
        ["depth where $T=0^\\circ$C"],
        ["Constant surface temperature, semi-infinite solid: $\\dfrac{T(x,t)-T_s}{T_i-T_s}=\\mathrm{erf}\\!\\left(\\dfrac{x}{2\\sqrt{\\alpha t}}\\right)$.",
         T("At $T=0$: $\\mathrm{erf}(\\eta)=\\dfrac{0-(-15)}{5-(-15)}=<<r:.2f>>\\Rightarrow\\eta=<<eta:.4f>>$ (from the erf table)."),
         T("$x=2\\eta\\sqrt{\\alpha t}=2(<<eta:.4f>>)\\sqrt{<<at:.3f>>}=<<x:.2f>>$ m.")],
        [T("$x_{0^\\circ C}=<<x:.2f>>$ m")],
        hint="Penetration depth scales as $\\sqrt{\\alpha t}$: four times as long, only twice as deep."),
        r=ratio, eta=eta, at=al_s * t_s, x=x_front),
        fill(problem(
        "10b", "Why tile feels colder than wood (contact temperature)", "warm-up", 8,
        "Treat skin and the floor as semi-infinite solids that are suddenly brought into contact. Skin at $33^\\circ$C ($k=0.37$, $\\rho=1000$, $c=3500$ in SI units) touches (i) ceramic tile at $18^\\circ$C "
        "($k=1.0$, $\\rho=2000$, $c=800$) and (ii) wood at $18^\\circ$C ($k=0.15$, $\\rho=700$, $c=1600$). Find the contact temperature in each case.",
        ["skin 33 °C, floor 18 °C", "tile, wood properties as above"],
        ["$T_{contact}$ for tile and wood"],
        ["For two semi-infinite solids in perfect contact the interface temperature is constant: $T_s=\\dfrac{e_1T_1+e_2T_2}{e_1+e_2}$ with effusivity $e=\\sqrt{k\\rho c}$.",
         T("$e_{skin}=<<es:.0f>>$, $e_{tile}=<<et:.0f>>$, $e_{wood}=<<ew:.0f>>$ W·s^½/m²K."),
         T("Tile: $T_s=<<Tt:.1f>>^\\circ$C. Wood: $T_s=<<Tw:.1f>>^\\circ$C. High effusivity pulls the interface toward the floor temperature, so tile feels colder.")],
        [T("tile $<<Tt:.1f>>^\\circ$C; wood $<<Tw:.1f>>^\\circ$C")],
        hint="Compare the effusivities, not the thermal conductivities alone."),
        es=e_skin, et=e_tile, ew=e_wood, Tt=Tc_tile, Tw=Tc_wood)]
    # explicit FD stability
    dx, al3, hh3, k3 = 0.01, 1e-6, 100.0, 2.0
    Bi3 = hh3 * dx / k3
    dt_int = dx ** 2 / (2 * al3)
    dt_surf = dx ** 2 / (2 * al3 * (1 + Bi3))
    dt_use = 30.0
    Fo3 = al3 * dt_use / dx ** 2
    Tm_new = Fo3 * (90 + 60) + (1 - 2 * Fo3) * 70
    Ts_new = 2 * Fo3 * (65 + Bi3 * 20) + (1 - 2 * Fo3 - 2 * Bi3 * Fo3) * 75
    P["u10"].append(fill(problem(
        "10c", "Explicit finite-difference: stability and one time step", "exam", 12,
        "A solid ($k=2.0$ W/m·K, $\\alpha=1\\times10^{-6}\\ \\mathrm{m^2/s}$) is modeled in 1-D with $\\Delta x=10$ mm, with a convective surface ($h=100$ W/m²K, $T_\\infty=20^\\circ$C). "
        "(a) Find the maximum stable time step for the interior nodes and for the surface node. (b) Using $\\Delta t=30$ s, advance one step for an interior node (at $70^\\circ$C with neighbors $90^\\circ$C and $60^\\circ$C) "
        "and for the surface node (at $75^\\circ$C with interior neighbor at $65^\\circ$C).",
        ["$\\Delta x=0.01$ m, $\\alpha=10^{-6}$, $k=2$", "$h=100$, $T_\\infty=20^\\circ$C", "$\\Delta t=30$ s"],
        ["$\\Delta t_{max}$ (interior, surface)", "$T_m^{p+1}$, $T_0^{p+1}$"],
        [T("$Bi=h\\Delta x/k=<<Bi:.2f>>$. Interior stability: $Fo\\le\\tfrac12\\Rightarrow\\Delta t\\le\\dfrac{\\Delta x^2}{2\\alpha}=<<dti:.0f>>$ s. Surface node: $Fo(1+Bi)\\le\\tfrac12\\Rightarrow\\Delta t\\le<<dts:.1f>>$ s. The surface node governs."),
         T("$\\Delta t=30$ s gives $Fo=<<Fo:.2f>>$ (stable, since 30 s < <dts:.1f>> s)."),
         T("Interior: $T_m^{p+1}=Fo(T_{m+1}+T_{m-1})+(1-2Fo)T_m=<<Tm:.1f>>^\\circ$C."),
         T("Surface: $T_0^{p+1}=2Fo(T_1+BiT_\\infty)+(1-2Fo-2BiFo)T_0=<<Tn:.1f>>^\\circ$C.")],
        [T("$\\Delta t_{max}=<<dts:.1f>>$ s (surface node)"), T("$T_m=<<Tm:.1f>>$, $T_0=<<Tn:.1f>>^\\circ$C")],
        hint="Stability is checked for every node type; the convective surface node is the strictest."),
        Bi=Bi3, dti=dt_int, dts=dt_surf, Fo=Fo3, Tm=Tm_new, Tn=Ts_new))

    # ---------------------------------------------------------------- Unit 11 (Ch 6)
    k_a, nu, Pr, rho_a, cp_a = 0.0263, 15.89e-6, 0.707, 1.1614, 1007.0
    U, x_, Lp = 5.0, 0.4, 1.0
    Rex = U * x_ / nu
    delta = 5 * x_ / math.sqrt(Rex)
    delta_t = delta * Pr ** (-1 / 3)
    Nux = 0.332 * math.sqrt(Rex) * Pr ** (1 / 3)
    hx = Nux * k_a / x_
    ReL = U * Lp / nu
    hL = 0.332 * math.sqrt(ReL) * Pr ** (1 / 3) * k_a / Lp
    hbar = 2 * hL
    xc = 5e5 * nu / U
    cfx = 0.664 / math.sqrt(Rex)
    tau_s = cfx * rho_a * U ** 2 / 2
    P["u11"] = [fill(problem(
        "11a", "Laminar boundary layer on a flat plate", "exam", 15,
        "Air at 300 K ($k=0.0263$ W/m·K, $\\nu=15.89\\times10^{-6}$ m²/s, $Pr=0.707$, $\\rho=1.161$ kg/m³) flows at $U_\\infty=5$ m/s over a flat plate of length $L=1$ m. "
        "(a) Is the flow laminar over the whole plate? (b) At $x=0.4$ m find the hydrodynamic and thermal boundary-layer thicknesses, the local friction coefficient and wall shear stress, and the local convection coefficient. "
        "(c) Find the average coefficient over $0<x<L$. Use $\\delta=5x/\\sqrt{Re_x}$, $\\delta_t=\\delta Pr^{-1/3}$, $Cf_x=0.664Re_x^{-1/2}$, $Nu_x=0.332Re_x^{1/2}Pr^{1/3}$.",
        ["air at 300 K properties above", "$U_\\infty=5$ m/s, $L=1$ m", "$Re_{x,c}=5\\times10^5$"],
        ["transition location", "$\\delta$, $\\delta_t$, $Cf_x$, $\\tau_s$, $h_x$ at 0.4 m", "$\\bar h_L$"],
        [T("$x_c=Re_{x,c}\\nu/U_\\infty=<<xc:.2f>>$ m $>L=1$ m, so the flow is laminar over the entire plate ($Re_L=<<ReL:sci3>>$)."),
         T("At $x=0.4$: $Re_x=<<Rex:sci3>>$, $\\delta=5x/\\sqrt{Re_x}=<<d:.2f>>$ mm, $\\delta_t=\\delta Pr^{-1/3}=<<dt:.2f>>$ mm (thermal layer slightly thicker since $Pr<1$)."),
         T("$Cf_x=0.664/\\sqrt{Re_x}=<<cf:.5f>>$, $\\tau_s=Cf_x\\rho U^2/2=<<tau:.4f>>$ N/m². $Nu_x=<<Nu:.1f>>$, so $h_x=Nu_xk/x=<<hx:.2f>>$ W/m²K."),
         T("Laminar plate: $h_x\\propto x^{-1/2}$, so $\\bar h_L=2h_{x=L}=2(<<hL:.2f>>)=<<hb:.2f>>$ W/m²K.")],
        [T("laminar everywhere ($x_c=<<xc:.2f>>$ m)"), T("$\\delta=<<d:.2f>>$ mm, $\\delta_t=<<dt:.2f>>$ mm, $h_x=<<hx:.2f>>$ W/m²K"), T("$\\bar h_L=<<hb:.2f>>$ W/m²K")],
        hint="$\\bar h=2h_x$ at the end of the plate is a laminar-only shortcut because $h_x\\sim x^{-1/2}$."),
        xc=xc, ReL=ReL, Rex=Rex, d=delta * 1000, dt=delta_t * 1000, cf=cfx, tau=tau_s, Nu=Nux, hx=hx, hL=hL, hb=hbar)]
    # Reynolds/Colburn analogy
    Pr2, U2, tau_meas = 0.707, 20.0, 0.95
    Cf2 = tau_meas / (rho_a * U2 ** 2 / 2)
    St = Cf2 / 2 / Pr2 ** (2 / 3)
    h_an = St * rho_a * U2 * cp_a
    P["u11"].append(fill(problem(
        "11b", "Heat transfer from a drag measurement (Reynolds–Colburn analogy)", "exam", 10,
        "Air at 300 K ($\\rho=1.161$ kg/m³, $c_p=1007$ J/kg·K, $Pr=0.707$) flows at $20$ m/s over a plate. A balance measurement gives an average wall shear stress of $0.95$ N/m². "
        "Use the Reynolds–Colburn analogy $St\\,Pr^{2/3}=Cf/2$ to estimate the average convection coefficient. Where is the analogy valid?",
        ["$\\rho=1.161$, $c_p=1007$, $Pr=0.707$", "$U_\\infty=20$ m/s", "$\\bar\\tau_s=0.95$ N/m²"],
        ["$\\overline{Cf}$", "$\\overline{St}$", "$\\bar h$"],
        [T("$\\overline{Cf}=\\dfrac{\\tau_s}{\\rho U_\\infty^2/2}=\\dfrac{0.95}{<<dyn:.1f>>}=<<cf:.5f>>$."),
         T("$St=\\dfrac{Cf/2}{Pr^{2/3}}=<<St:.5f>>$. Since $St=\\dfrac{h}{\\rho U_\\infty c_p}$: $\\bar h=St\\,\\rho U_\\infty c_p=<<h:.1f>>$ W/m²K."),
         "Valid for $0.6<Pr<60$ and when $dp/dx\\approx0$ (flat-plate-like flow); it fails with large form drag (bluff bodies)."],
        [T("$\\bar h\\approx<<h:.0f>>$ W/m²K")],
        hint="Convert $\\tau_s$ to $Cf$ using the dynamic pressure $\\rho U^2/2$."),
        dyn=rho_a * U2 ** 2 / 2, cf=Cf2, St=St, h=h_an))
    return P


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    for u, ps in build().items():
        for p in ps:
            print(u, p["id"], "|", " || ".join(p["solution"]["answers"]))
            assert "<<" not in " ".join(p["solution"]["steps"] + p["solution"]["answers"]), p["id"]
