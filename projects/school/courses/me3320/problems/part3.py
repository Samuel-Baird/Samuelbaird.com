"""Original practice problems, units 12-18 (Ch 7-9, 11-13). All answers computed."""
import math
from common import T, SIGMA, G, bisect, planck_fraction, problem, fill


def build():
    P = {}

    # ---------------------------------------------------------------- Unit 12 (Ch 7.1-7.3)
    # air at film temperature 315 K (interpolated between 300 K and 350 K table values)
    k, nu, Pr = 0.0263 + 0.3 * (0.030 - 0.0263), (15.89 + 0.3 * (20.92 - 15.89)) * 1e-6, 0.707 - 0.3 * 0.007
    U, Lp, W, Ts, Tinf = 20.0, 1.5, 0.8, 330.0, 300.0
    ReL = U * Lp / nu
    xc = 5e5 * nu / U
    Nu_mix = (0.037 * ReL ** 0.8 - 871) * Pr ** (1 / 3)
    Nu_turb = 0.037 * ReL ** 0.8 * Pr ** (1 / 3)
    hbar = Nu_mix * k / Lp
    q = hbar * Lp * W * (Ts - Tinf)
    Nu_lam_only = 0.664 * math.sqrt(ReL) * Pr ** (1 / 3)
    P["u12"] = [fill(problem(
        "12a", "Mixed laminar–turbulent flat plate", "exam", 15,
        "Air at $T_\\infty=300$ K flows at $U_\\infty=20$ m/s over a flat plate $L=1.5$ m long and $W=0.8$ m wide held at $T_s=330$ K. "
        f"Evaluate properties at the film temperature (315 K): $k={k:.4f}$ W/m·K, $\\nu={nu*1e6:.2f}\\times10^{{-6}}$ m²/s, $Pr={Pr:.3f}$. Take $Re_{{x,c}}=5\\times10^5$. "
        "(a) Where does transition occur? (b) Find the average Nusselt number and $\\bar h_L$ for the combined laminar–turbulent boundary layer. (c) Find the total heat rate from the plate.",
        ["$U_\\infty=20$ m/s, $L=1.5$ m, $W=0.8$ m", "$T_s=330$ K, $T_\\infty=300$ K", "air properties at 315 K above"],
        ["$x_c$", "$\\bar{Nu}_L$, $\\bar h_L$", "$q$"],
        [T("$Re_L=U_\\infty L/\\nu=<<ReL:sci3>>$ and $x_c=Re_{x,c}\\nu/U_\\infty=<<xc:.3f>>$ m: only the first <<pct:.0f>>% of the plate is laminar, so use the mixed correlation."),
         T("$\\overline{Nu}_L=(0.037Re_L^{4/5}-871)Pr^{1/3}=<<Nu:.0f>>$ (all-turbulent would give <<Nut:.0f>>, <<ov:.0f>>% too high; all-laminar <<Nul:.0f>>, far too low)."),
         T("$\\bar h_L=\\overline{Nu}_Lk/L=<<h:.2f>>$ W/m²K."),
         T("$q=\\bar h_L(LW)(T_s-T_\\infty)=<<h:.2f>>(1.2)(30)=<<q:.0f>>$ W.")],
        [T("$x_c=<<xc:.3f>>$ m"), T("$\\bar h_L=<<h:.1f>>$ W/m²K"), T("$q=<<q:.0f>>$ W")],
        hint="Check $Re_L$ against $5\\times10^5$ first; it decides which correlation applies."),
        ReL=ReL, xc=xc, pct=100 * xc / Lp, Nu=Nu_mix, Nut=Nu_turb, ov=100 * (Nu_turb / Nu_mix - 1), Nul=Nu_lam_only, h=hbar, q=q)]
    # water laminar plate
    kw, nuw, Prw, Uw, Lw, Ww, Tsw, Tiw = 0.613, 0.858e-6, 5.83, 0.15, 0.5, 0.3, 40.0, 20.0
    ReLw = Uw * Lw / nuw
    Nuw = 0.664 * math.sqrt(ReLw) * Prw ** (1 / 3)
    hw = Nuw * kw / Lw
    qw = hw * Lw * Ww * (Tsw - Tiw)
    dlt = 5 * Lw / math.sqrt(ReLw)
    P["u12"].append(fill(problem(
        "12b", "Laminar flat plate in water", "exam", 10,
        "Water at 20 °C ($k=0.613$ W/m·K, $\\nu=0.858\\times10^{-6}$ m²/s, $Pr=5.83$) flows at $0.15$ m/s over a $0.5\\times0.3$ m heated plate (flow along the $0.5$ m side) at $40^\\circ$C. "
        "Verify the flow regime, then find $\\bar h$, the heat rate, and the boundary-layer thickness at the trailing edge.",
        ["$U_\\infty=0.15$ m/s", "$L=0.5$, $W=0.3$ m", "$T_s=40^\\circ$C, $T_\\infty=20^\\circ$C", "water properties above"],
        ["$Re_L$", "$\\bar h$, $q$", "$\\delta(L)$"],
        [T("$Re_L=<<ReL:sci3>><5\\times10^5$ — laminar over the whole plate."),
         T("$\\overline{Nu}_L=0.664Re_L^{1/2}Pr^{1/3}=<<Nu:.0f>>$ ($Pr>0.6$ ✓); $\\bar h=\\overline{Nu}_Lk/L=<<h:.0f>>$ W/m²K."),
         T("$q=\\bar h(LW)(T_s-T_\\infty)=<<q:.0f>>$ W. Thickness: $\\delta(L)=5L/\\sqrt{Re_L}=<<d:.1f>>$ mm.")],
        [T("$\\bar h=<<h:.0f>>$ W/m²K; $q=<<q:.0f>>$ W"), T("$\\delta(L)=<<d:.1f>>$ mm")],
        hint="High $Pr$ fluid: the thermal boundary layer is much thinner than the velocity layer."),
        ReL=ReLw, Nu=Nuw, h=hw, q=qw, d=dlt * 1000))

    # ---------------------------------------------------------------- Unit 13 (Ch 7.4-7.6)
    # cylinder in crossflow, air film 350 K
    k13, nu13, Pr13, D13, V13, Ts13, Ti13 = 0.030, 20.92e-6, 0.700, 0.020, 10.0, 400.0, 300.0
    Re13 = V13 * D13 / nu13
    CB = 0.3 + (0.62 * Re13 ** 0.5 * Pr13 ** (1 / 3)) / (1 + (0.4 / Pr13) ** (2 / 3)) ** 0.25 * (1 + (Re13 / 282000) ** (5 / 8)) ** (4 / 5)
    h13 = CB * k13 / D13
    qp13 = h13 * math.pi * D13 * (Ts13 - Ti13)
    P["u13"] = [fill(problem(
        "13a", "Heated cylinder in cross flow (Churchill–Bernstein)", "exam", 12,
        "Air at 300 K and 10 m/s crosses a long cylinder of diameter $D=20$ mm whose surface is at 400 K. Use film properties at 350 K: $k=0.030$ W/m·K, $\\nu=20.92\\times10^{-6}$ m²/s, $Pr=0.700$. "
        "Find $Re_D$, the average Nusselt number from the Churchill–Bernstein correlation, $\\bar h$, and the heat loss per meter. "
        "$\\overline{Nu}_D=0.3+\\dfrac{0.62Re_D^{1/2}Pr^{1/3}}{[1+(0.4/Pr)^{2/3}]^{1/4}}\\left[1+\\left(\\dfrac{Re_D}{282{,}000}\\right)^{5/8}\\right]^{4/5}$ ($Re_DPr>0.2$).",
        ["$V=10$ m/s, $D=0.020$ m", "$T_s=400$ K, $T_\\infty=300$ K", "air at 350 K properties"],
        ["$Re_D$", "$\\overline{Nu}_D$, $\\bar h$", "$q'$"],
        [T("$Re_D=VD/\\nu=<<Re:.0f>>$; $Re_DPr=<<RP:.0f>>>0.2$ ✓."),
         T("$\\overline{Nu}_D=<<Nu:.1f>>$, so $\\bar h=\\overline{Nu}_Dk/D=<<h:.1f>>$ W/m²K."),
         T("$q'=\\bar h\\pi D(T_s-T_\\infty)=<<h:.1f>>\\pi(0.020)(100)=<<qp:.0f>>$ W/m.")],
        [T("$\\overline{Nu}_D=<<Nu:.1f>>$, $\\bar h=<<h:.1f>>$ W/m²K"), T("$q'=<<qp:.0f>>$ W/m")],
        hint="Characteristic length for a cylinder in cross flow is the diameter, and properties are at the film temperature."),
        Re=Re13, RP=Re13 * Pr13, Nu=CB, h=h13, qp=qp13)]
    # sphere + lumped capacitance
    D14, V14, Tinf14, Ti14, Tf14 = 0.012, 5.0, 300.0, 350.0, 310.0
    nu14, k14, Pr14, mu, mus = 15.89e-6, 0.0263, 0.707, 184.6e-7, 208.2e-7
    Re14 = V14 * D14 / nu14
    Nu14 = 2 + (0.4 * Re14 ** 0.5 + 0.06 * Re14 ** (2 / 3)) * Pr14 ** 0.4 * (mu / mus) ** 0.25
    h14 = Nu14 * k14 / D14
    rho_c, c_c, k_c = 8933.0, 385.0, 401.0
    Lc14 = D14 / 6
    Bi14 = h14 * Lc14 / k_c
    tau14 = rho_c * c_c * Lc14 / h14
    t14 = tau14 * math.log((Ti14 - Tinf14) / (Tf14 - Tinf14))
    P["u13"].append(fill(problem(
        "14b", "Sphere in air flow, then lumped cooling (two-topic problem)", "exam", 18,
        "A copper sphere ($D=12$ mm; $\\rho=8933$ kg/m³, $c=385$ J/kg·K, $k=401$ W/m·K) at 350 K is suspended in air at 300 K flowing at 5 m/s. "
        "Air properties at 300 K: $k=0.0263$, $\\nu=15.89\\times10^{-6}$, $Pr=0.707$, $\\mu_\\infty=184.6\\times10^{-7}$ N·s/m²; viscosity at the surface $\\mu_s=208.2\\times10^{-7}$ N·s/m². "
        "(a) Find $\\bar h$ with the Whitaker sphere correlation $\\overline{Nu}_D=2+(0.4Re_D^{1/2}+0.06Re_D^{2/3})Pr^{0.4}(\\mu/\\mu_s)^{1/4}$. "
        "(b) Show lumped capacitance applies and find the time for the sphere to cool to 310 K.",
        ["$D=12$ mm, copper", "$V=5$ m/s", "$T_i=350$ K, $T_\\infty=300$ K", "properties above"],
        ["$\\bar h$", "$Bi$", "$t$ to 310 K"],
        [T("$Re_D=VD/\\nu=<<Re:.0f>>$. $\\overline{Nu}_D=2+(0.4\\sqrt{Re}+0.06Re^{2/3})Pr^{0.4}(\\mu/\\mu_s)^{1/4}=<<Nu:.1f>>$, so $\\bar h=<<h:.1f>>$ W/m²K."),
         T("$L_c=D/6=<<Lc:.4f>>$ m; $Bi=\\bar hL_c/k=<<Bi:sci2>>\\ll0.1$ ✓."),
         T("$\\tau_t=\\rho cL_c/\\bar h=<<tau:.0f>>$ s; $t=\\tau_t\\ln\\dfrac{50}{10}=<<t:.0f>>$ s (≈ <<tm:.1f>> min).")],
        [T("$\\bar h=<<h:.1f>>$ W/m²K"), T("$Bi=<<Bi:sci2>>$"), T("$t=<<t:.0f>>$ s")],
        hint="Chapter 7 gives $h$, Chapter 5 turns it into a time. Exams love this chain."),
        Re=Re14, Nu=Nu14, h=h14, Lc=Lc14, Bi=Bi14, tau=tau14, t=t14, tm=t14 / 60))
    P["u13"][1]["id"] = "13b"

    # ---------------------------------------------------------------- Unit 14 (Ch 8)
    cpw, muw, kw8, Prw8 = 4178.0, 695e-6, 0.628, 4.5
    D8, m8, Ts8, Tmi, L8 = 0.025, 0.20, 100.0, 20.0, 3.0
    Re8 = 4 * m8 / (math.pi * D8 * muw)
    Nu8 = 0.023 * Re8 ** 0.8 * Prw8 ** 0.4
    h8 = Nu8 * kw8 / D8
    As = math.pi * D8 * L8
    Tmo = Ts8 - (Ts8 - Tmi) * math.exp(-h8 * As / (m8 * cpw))
    q8 = m8 * cpw * (Tmo - Tmi)
    dTlm = ((Ts8 - Tmi) - (Ts8 - Tmo)) / math.log((Ts8 - Tmi) / (Ts8 - Tmo))
    q8b = h8 * As * dTlm
    P["u14"] = [fill(problem(
        "14a", "Water heated in a tube at constant wall temperature", "exam", 15,
        "Water flows at $\\dot m=0.20$ kg/s through a $D=25$ mm tube, $L=3$ m long, whose wall is held at $100^\\circ$C (condensing steam). The inlet temperature is $20^\\circ$C. "
        "Evaluate properties at 310 K: $c_p=4178$ J/kg·K, $\\mu=695\\times10^{-6}$ N·s/m², $k=0.628$ W/m·K, $Pr=4.5$. "
        "(a) Determine the flow regime. (b) Use Dittus–Boelter to find $\\bar h$. (c) Find the outlet temperature and the heat rate; verify with the log-mean temperature difference.",
        ["$\\dot m=0.20$ kg/s, $D=0.025$ m, $L=3$ m", "$T_s=100^\\circ$C, $T_{m,i}=20^\\circ$C", "properties above"],
        ["$Re_D$", "$\\bar h$", "$T_{m,o}$, $q$"],
        [T("$Re_D=\\dfrac{4\\dot m}{\\pi D\\mu}=<<Re:.0f>>>10^4$ — turbulent. Heating, $n=0.4$."),
         T("$Nu_D=0.023Re_D^{4/5}Pr^{0.4}=<<Nu:.1f>>$ (valid for $L/D=120>10$ ✓), $\\bar h=Nu_Dk/D=<<h:.0f>>$ W/m²K."),
         T("Constant $T_s$: $\\dfrac{T_s-T_{m,o}}{T_s-T_{m,i}}=\\exp\\!\\left(-\\dfrac{\\pi DL\\bar h}{\\dot mc_p}\\right)=\\exp(-<<ntu:.3f>>)$, so $T_{m,o}=<<Tmo:.1f>>^\\circ$C."),
         T("$q=\\dot mc_p(T_{m,o}-T_{m,i})=<<q:.0f>>$ W. Check: $\\Delta T_{lm}=<<dlm:.1f>>$ K, $q=\\bar hA_s\\Delta T_{lm}=<<q2:.0f>>$ W ✓.")],
        [T("$Re_D=<<Re:.0f>>$ (turbulent), $\\bar h=<<h:.0f>>$ W/m²K"), T("$T_{m,o}=<<Tmo:.1f>>^\\circ$C, $q=<<q:.0f>>$ W")],
        hint="The exponential form with $T_s-T_m$ is the constant-surface-temperature result; do not average the temperatures arithmetically."),
        Re=Re8, Nu=Nu8, h=h8, ntu=h8 * As / (m8 * cpw), Tmo=Tmo, q=q8, dlm=dTlm, q2=q8b)]
    # laminar constant heat flux
    m8b, D8b, qpp8, L8b, Tmi8b = 0.003, 0.008, 5000.0, 1.5, 20.0
    Re8b = 4 * m8b / (math.pi * D8b * muw)
    h8b = 4.36 * kw8 / D8b
    q8c = qpp8 * math.pi * D8b * L8b
    dTm = q8c / (m8b * cpw)
    Tmo8b = Tmi8b + dTm
    Ts_o = Tmo8b + qpp8 / h8b
    xfd_h = 0.05 * Re8b * D8b
    xfd_t = 0.05 * Re8b * Prw8 * D8b
    P["u14"].append(fill(problem(
        "14b", "Laminar flow with constant heat flux", "exam", 15,
        "Water at $\\dot m=0.003$ kg/s enters a $D=8$ mm tube at $20^\\circ$C; a heater supplies a uniform flux $q''_s=5000$ W/m² over $L=1.5$ m (same properties as the previous problem). "
        "(a) Determine the regime. (b) Find the outlet mean temperature. (c) Find the surface temperature at the outlet assuming fully developed flow ($Nu_D=4.36$). (d) Compare the entry lengths with $L$.",
        ["$\\dot m=0.003$ kg/s, $D=8$ mm, $L=1.5$ m", "$q''_s=5000$ W/m²", "$T_{m,i}=20^\\circ$C", "properties as 14a"],
        ["$Re_D$", "$T_{m,o}$", "$T_{s,o}$", "entry lengths"],
        [T("$Re_D=4\\dot m/(\\pi D\\mu)=<<Re:.0f>>$ — laminar."),
         T("Constant flux: $q=q''_s\\pi DL=<<q:.1f>>$ W and $T_{m,o}=T_{m,i}+q/(\\dot mc_p)=<<Tmo:.1f>>^\\circ$C ($T_m$ rises linearly with $x$)."),
         T("$h=Nu_Dk/D=4.36(0.628)/0.008=<<h:.0f>>$ W/m²K and $T_{s,o}=T_{m,o}+q''_s/h=<<Tso:.1f>>^\\circ$C."),
         T("Hydrodynamic entry $\\approx0.05Re_DD=<<xh:.2f>>$ m; thermal entry $\\approx0.05Re_DPrD=<<xt:.2f>>$ m vs. $L=1.5$ m — the thermal layer is nearly developed by the exit, so $Nu=4.36$ is reasonable near the outlet but optimistic upstream.")],
        [T("$T_{m,o}=<<Tmo:.1f>>^\\circ$C"), T("$T_{s,o}=<<Tso:.1f>>^\\circ$C")],
        hint="For constant flux the wall–fluid difference $q''_s/h$ is constant once developed."),
        Re=Re8b, q=q8c, Tmo=Tmo8b, h=h8b, Tso=Ts_o, xh=xfd_h, xt=xfd_t))

    # ---------------------------------------------------------------- Unit 15 (Ch 11)
    mo, cpo, Thi, Tho = 2.0, 2100.0, 120.0, 80.0
    q15 = mo * cpo * (Thi - Tho)
    Tci, Tco, cpw15 = 20.0, 50.0, 4180.0
    mc = q15 / (cpw15 * (Tco - Tci))
    dT1, dT2 = Thi - Tco, Tho - Tci
    LM_c = (dT1 - dT2) / math.log(dT1 / dT2)
    U15 = 500.0
    A_c = q15 / (U15 * LM_c)
    dT1p, dT2p = Thi - Tci, Tho - Tco
    LM_p = (dT1p - dT2p) / math.log(dT1p / dT2p)
    A_p = q15 / (U15 * LM_p)
    P["u15"] = [fill(problem(
        "15a", "Oil cooler design with LMTD (counter vs parallel)", "exam", 15,
        "Oil ($\\dot m=2$ kg/s, $c_p=2100$ J/kg·K) is cooled from $120^\\circ$C to $80^\\circ$C by water entering at $20^\\circ$C and leaving at $50^\\circ$C ($c_p=4180$). The overall coefficient is $U=500$ W/m²K. "
        "Find (a) the heat rate, (b) the water flow rate, (c) the area required for a counterflow exchanger, and (d) the area if it were parallel flow.",
        ["oil 2 kg/s, 120→80 °C", "water 20→50 °C", "$U=500$ W/m²K"],
        ["$q$", "$\\dot m_c$", "$A_{counter}$", "$A_{parallel}$"],
        [T("$q=\\dot m_hc_{p,h}(T_{h,i}-T_{h,o})=2(2100)(40)=<<q:.0f>>$ W; $\\dot m_c=q/[c_{p,c}(T_{c,o}-T_{c,i})]=<<mc:.3f>>$ kg/s."),
         T("Counterflow: $\\Delta T_1=T_{h,i}-T_{c,o}=<<d1:.0f>>$ K, $\\Delta T_2=T_{h,o}-T_{c,i}=<<d2:.0f>>$ K; $\\Delta T_{lm}=\\dfrac{\\Delta T_1-\\Delta T_2}{\\ln(\\Delta T_1/\\Delta T_2)}=<<lm:.2f>>$ K."),
         T("$A=\\dfrac{q}{U\\Delta T_{lm}}=<<A:.2f>>$ m²."),
         T("Parallel flow: $\\Delta T_1=T_{h,i}-T_{c,i}=<<d1p:.0f>>$, $\\Delta T_2=T_{h,o}-T_{c,o}=<<d2p:.0f>>$; $\\Delta T_{lm}=<<lmp:.2f>>$ K, so $A=<<Ap:.2f>>$ m² — about <<more:.0f>>% more area.")],
        [T("$q=<<qk:.0f>>$ kW; $\\dot m_c=<<mc:.2f>>$ kg/s"), T("$A_{counter}=<<A:.2f>>$ m²; $A_{parallel}=<<Ap:.2f>>$ m²")],
        hint="Label which temperature difference sits at which end before taking the log."),
        q=q15, qk=q15 / 1000, mc=mc, d1=dT1, d2=dT2, lm=LM_c, A=A_c, d1p=dT1p, d2p=dT2p, lmp=LM_p, Ap=A_p, more=100 * (A_p / A_c - 1))]
    # eps-NTU
    mh, mcold, cp15, Thi2, Tci2, UA = 0.8, 1.2, 4180.0, 90.0, 20.0, 400.0 * 8.0
    Ch, Cc = mh * cp15, mcold * cp15
    Cmin, Cmax = min(Ch, Cc), max(Ch, Cc)
    Cr = Cmin / Cmax
    NTU = UA / Cmin
    eps_c = (1 - math.exp(-NTU * (1 - Cr))) / (1 - Cr * math.exp(-NTU * (1 - Cr)))
    eps_p = (1 - math.exp(-NTU * (1 + Cr))) / (1 + Cr)
    qmax = Cmin * (Thi2 - Tci2)
    qc = eps_c * qmax
    Tho2 = Thi2 - qc / Ch
    Tco2 = Tci2 + qc / Cc
    qp = eps_p * qmax
    P["u15"].append(fill(problem(
        "15b", "Rating an exchanger with the effectiveness–NTU method", "exam", 15,
        "A counterflow water–water exchanger has $UA=400\\times8=3200$ W/K. Hot water enters at $90^\\circ$C at $0.8$ kg/s; cold water enters at $20^\\circ$C at $1.2$ kg/s ($c_p=4180$ J/kg·K for both). "
        "Find the effectiveness, the heat rate, and both outlet temperatures. How would a parallel-flow arrangement with the same $UA$ compare? "
        "(Counterflow: $\\varepsilon=\\dfrac{1-e^{-NTU(1-C_r)}}{1-C_re^{-NTU(1-C_r)}}$; parallel: $\\varepsilon=\\dfrac{1-e^{-NTU(1+C_r)}}{1+C_r}$.)",
        ["hot 0.8 kg/s at 90 °C", "cold 1.2 kg/s at 20 °C", "$UA=3200$ W/K", "counterflow"],
        ["$C_{min}$, $C_r$, NTU", "$\\varepsilon$, $q$", "$T_{h,o}$, $T_{c,o}$", "parallel comparison"],
        [T("$C_h=<<Ch:.0f>>$ W/K, $C_c=<<Cc:.0f>>$ W/K: $C_{min}=C_h$, $C_r=C_{min}/C_{max}=<<Cr:.3f>>$, $NTU=UA/C_{min}=<<NTU:.3f>>$."),
         T("$\\varepsilon=<<ec:.4f>>$. $q_{max}=C_{min}(T_{h,i}-T_{c,i})=<<qm:.0f>>$ W, so $q=\\varepsilon q_{max}=<<q:.0f>>$ W."),
         T("$T_{h,o}=T_{h,i}-q/C_h=<<Tho:.1f>>^\\circ$C; $T_{c,o}=T_{c,i}+q/C_c=<<Tco:.1f>>^\\circ$C."),
         T("Parallel: $\\varepsilon=<<ep:.4f>>$, $q=<<qp:.0f>>$ W — about <<less:.0f>>% less heat for the same $UA$.")],
        [T("$\\varepsilon=<<ec:.3f>>$, $q=<<q:.0f>>$ W"), T("$T_{h,o}=<<Tho:.1f>>^\\circ$C; $T_{c,o}=<<Tco:.1f>>^\\circ$C")],
        hint="NTU uses $C_{min}$, not the cold stream, unless they happen to be the same."),
        Ch=Ch, Cc=Cc, Cr=Cr, NTU=NTU, ec=eps_c, qm=qmax, q=qc, Tho=Tho2, Tco=Tco2, ep=eps_p, qp=qp, less=100 * (1 - qp / qc)))

    # ---------------------------------------------------------------- Unit 16 (Ch 9)
    kf, nuf, alf, Prf = 0.02815, 18.405e-6, 26.2e-6, 0.7035
    Tsf, Tif = 370.0, 280.0
    Tf = (Tsf + Tif) / 2
    beta = 1 / Tf
    dT = Tsf - Tif
    Lv = 0.6
    Ra_L = G * beta * dT * Lv ** 3 / (nuf * alf)
    Nu_v = (0.825 + 0.387 * Ra_L ** (1 / 6) / (1 + (0.492 / Prf) ** (9 / 16)) ** (8 / 27)) ** 2
    h_v = Nu_v * kf / Lv
    Wv = 0.8
    q_v = h_v * Lv * Wv * dT
    Nu_v_lam = 0.68 + 0.670 * Ra_L ** 0.25 / (1 + (0.492 / Prf) ** (9 / 16)) ** (4 / 9)
    P["u16"] = [fill(problem(
        "16a", "Vertical heated plate in still air", "exam", 12,
        "A vertical plate $0.6$ m tall and $0.8$ m wide is at $370$ K in quiescent air at $280$ K. Film properties (325 K): $k=0.02815$ W/m·K, $\\nu=18.4\\times10^{-6}$ m²/s, $\\alpha=26.2\\times10^{-6}$ m²/s, $Pr=0.7035$, $\\beta=1/T_f$. "
        "Find $Ra_L$, decide the regime, and compute $\\bar h$ and the convective heat rate using the Churchill–Chu full-range correlation $\\overline{Nu}_L=\\left\\{0.825+\\dfrac{0.387Ra_L^{1/6}}{[1+(0.492/Pr)^{9/16}]^{8/27}}\\right\\}^2$.",
        ["$L=0.6$ m, $W=0.8$ m", "$T_s=370$ K, $T_\\infty=280$ K", "air at 325 K properties"],
        ["$Ra_L$", "$\\overline{Nu}_L$, $\\bar h$", "$q$"],
        [T("$Ra_L=\\dfrac{g\\beta\\Delta TL^3}{\\nu\\alpha}=<<Ra:sci3>>$. Transition for a vertical plate is near $10^9$, so this is turbulent."),
         T("Churchill–Chu: $\\overline{Nu}_L=<<Nu:.1f>>$ (the laminar-only form would give <<Nul:.1f>>, which is not valid here)."),
         T("$\\bar h=\\overline{Nu}_Lk/L=<<h:.2f>>$ W/m²K; $q=\\bar hA\\Delta T=<<q:.0f>>$ W.")],
        [T("$Ra_L=<<Ra:sci3>>$ (turbulent)"), T("$\\bar h=<<h:.2f>>$ W/m²K; $q=<<q:.0f>>$ W")],
        hint="$\\beta=1/T_f$ for an ideal gas, with $T_f$ in kelvin. Compute $Ra$ first to choose the correlation."),
        Ra=Ra_L, Nu=Nu_v, Nul=Nu_v_lam, h=h_v, q=q_v)]
    # horizontal cylinder with radiation
    Dc = 0.05
    Ra_D = G * beta * dT * Dc ** 3 / (nuf * alf)
    Nu_c = (0.6 + 0.387 * Ra_D ** (1 / 6) / (1 + (0.559 / Prf) ** (9 / 16)) ** (8 / 27)) ** 2
    h_c = Nu_c * kf / Dc
    epsc = 0.9
    hr = epsc * SIGMA * (Tsf + Tif) * (Tsf ** 2 + Tif ** 2)
    qc_ = h_c * math.pi * Dc * dT
    qr_ = hr * math.pi * Dc * dT
    P["u16"].append(fill(problem(
        "16b", "Hot pipe in a room: free convection plus radiation", "exam", 12,
        "A horizontal pipe of diameter $D=50$ mm at 370 K sits in still air at 280 K (same film properties as 16a); the pipe surface emissivity is $\\varepsilon=0.9$ and the room surfaces are at 280 K. "
        "Find $Ra_D$, $\\bar h$ from the Churchill–Chu horizontal-cylinder correlation $\\overline{Nu}_D=\\left\\{0.6+\\dfrac{0.387Ra_D^{1/6}}{[1+(0.559/Pr)^{9/16}]^{8/27}}\\right\\}^2$, and the convective, radiative and total heat loss per meter.",
        ["$D=0.05$ m", "$T_s=370$ K, $T_\\infty=T_{sur}=280$ K", "$\\varepsilon=0.9$"],
        ["$Ra_D$", "$\\bar h$", "$q'_{conv}$, $q'_{rad}$, total"],
        [T("$Ra_D=<<Ra:sci3>>$ (well within the $Ra_D\\le10^{12}$ range)."),
         T("$\\overline{Nu}_D=<<Nu:.2f>>$, $\\bar h=<<h:.2f>>$ W/m²K."),
         T("$h_r=\\varepsilon\\sigma(T_s+T_{sur})(T_s^2+T_{sur}^2)=<<hr:.2f>>$ W/m²K — almost the same as $\\bar h$, so radiation carries about half of the total loss."),
         T("$q'_{conv}=\\bar h\\pi D\\Delta T=<<qc:.1f>>$ W/m; $q'_{rad}=h_r\\pi D\\Delta T=<<qr:.1f>>$ W/m; total $=<<qt:.1f>>$ W/m.")],
        [T("$\\bar h=<<h:.2f>>$ W/m²K"), T("$q'_{conv}=<<qc:.1f>>$, $q'_{rad}=<<qr:.1f>>$, total $<<qt:.1f>>$ W/m")],
        hint="In natural convection in air, $h$ and $h_r$ are often the same order of magnitude. Add both."),
        Ra=Ra_D, Nu=Nu_c, h=h_c, hr=hr, qc=qc_, qr=qr_, qt=qc_ + qr_))

    # ---------------------------------------------------------------- Unit 17 (Ch 12)
    T17 = 1000.0
    F2, F5 = planck_fraction(2000.0), planck_fraction(5000.0)
    Eb = SIGMA * T17 ** 4
    band = (F5 - F2) * Eb
    lam_max = 2898.0 / T17
    eps_g = 0.6
    P["u17"] = [fill(problem(
        "17a", "Blackbody band emission and Wien's law", "exam", 10,
        "A surface at 1000 K emits as a blackbody. Find (a) its total emissive power, (b) the wavelength of peak emission, (c) the fraction and the power of emission between $\\lambda_1=2\\ \\mu$m and $\\lambda_2=5\\ \\mu$m "
        "(use the blackbody fraction $F_{(0\\to\\lambda)}$ vs. $\\lambda T$, Table 12.2), (d) the emissive power if the surface were gray with $\\varepsilon=0.6$.",
        ["$T=1000$ K", "$\\lambda_1=2\\ \\mu$m, $\\lambda_2=5\\ \\mu$m", "$\\sigma=5.67\\times10^{-8}$"],
        ["$E_b$", "$\\lambda_{max}$", "band fraction and power", "gray $E$"],
        [T("$E_b=\\sigma T^4=<<Eb:.0f>>$ W/m²."),
         T("Wien: $\\lambda_{max}T=2898\\ \\mu$m·K, so $\\lambda_{max}=<<lm:.3f>>\\ \\mu$m (near-infrared)."),
         T("$\\lambda_1T=2000$ and $\\lambda_2T=5000\\ \\mu$m·K give $F_{(0\\to2000)}=<<f2:.4f>>$ and $F_{(0\\to5000)}=<<f5:.4f>>$ (Table 12.2: 0.0667, 0.6337). Band fraction $=F_{(\\lambda_1\\to\\lambda_2)}=<<df:.4f>>$, power $=<<band:.0f>>$ W/m²."),
         T("Gray: $E=\\varepsilon\\sigma T^4=<<Eg:.0f>>$ W/m² (the same spectral shape, scaled by 0.6).")],
        [T("$E_b=<<Eb:.0f>>$ W/m²; $\\lambda_{max}=<<lm:.2f>>\\ \\mu$m"), T("band fraction $<<df:.3f>>$ → $<<band:.0f>>$ W/m²; gray: $<<Eg:.0f>>$ W/m²")],
        hint="Convert wavelengths to $\\lambda T$ in $\\mu$m·K before using the table."),
        Eb=Eb, lm=lam_max, f2=F2, f5=F5, df=F5 - F2, band=band, Eg=eps_g * Eb)]
    # selective surface equilibrium
    Gs, Tsun = 1000.0, 5800.0
    Fs = planck_fraction(2.0 * Tsun)
    alpha_s = 0.9 * Fs + 0.2 * (1 - Fs)

    def eps_T(Tk):
        f = planck_fraction(2.0 * Tk)
        return 0.9 * f + 0.2 * (1 - f)
    Teq = bisect(lambda Tk: eps_T(Tk) * SIGMA * Tk ** 4 - alpha_s * Gs, 50, 1500)
    P["u17"].append(fill(problem(
        "17b", "Selective surface in sunlight (Kirchhoff + band properties)", "exam", 18,
        "An opaque, diffuse plate facing the sun has $\\alpha_\\lambda=0.9$ for $\\lambda<2\\ \\mu$m and $\\alpha_\\lambda=0.2$ for $\\lambda>2\\ \\mu$m. Solar irradiation is $G_S=1000$ W/m² with spectral distribution of a 5800 K blackbody. "
        "The back is insulated and the plate radiates to cold space (no convection). "
        "(a) Find the solar absorptivity $\\alpha_S$. (b) Using Kirchhoff's law ($\\varepsilon_\\lambda=\\alpha_\\lambda$ for a diffuse surface), find the total emissivity at the equilibrium temperature and the equilibrium temperature itself.",
        ["$\\alpha_\\lambda=0.9\\ (\\lambda<2\\ \\mu$m$)$, $0.2\\ (\\lambda>2\\ \\mu$m$)$", "$G_S=1000$ W/m², sun ≈ 5800 K blackbody", "insulated back, radiates to 0 K"],
        ["$\\alpha_S$", "$\\varepsilon$, $T_{eq}$"],
        [T("Absorptivity is a solar-weighted average: $\\lambda T_{sun}=2\\times5800=11{,}600\\ \\mu$m·K gives $F_{(0\\to2\\mu m)}=<<Fs:.4f>>$. $\\alpha_S=0.9F+0.2(1-F)=<<al:.4f>>$."),
         T("Equilibrium: $\\alpha_SG_S=\\varepsilon(T)\\sigma T^4$ with $\\varepsilon(T)=0.9F_{(0\\to2T)}+0.2[1-F_{(0\\to2T)}]$. At the plate temperature $\\lambda T=2T\\approx<<lt:.0f>>\\ \\mu$m·K is tiny, so $F\\approx0$ and $\\varepsilon\\approx<<eps:.4f>>$."),
         T("Iterating: $T_{eq}=<<Teq:.0f>>$ K ($\\approx<<TC:.0f>>^\\circ$C). A black surface would reach only $(G_S/\\sigma)^{1/4}=<<Tb:.0f>>$ K; the selective coating runs much hotter.")],
        [T("$\\alpha_S=<<al:.3f>>$"), T("$\\varepsilon\\approx<<eps:.3f>>$, $T_{eq}\\approx<<Teq:.0f>>$ K")],
        hint="$\\alpha$ is averaged with the **source** spectrum, $\\varepsilon$ with the **surface** spectrum (set by its own temperature)."),
        Fs=Fs, al=alpha_s, lt=2 * Teq, eps=eps_T(Teq), Teq=Teq, TC=Teq - 273.15, Tb=(Gs / SIGMA) ** 0.25))

    # ---------------------------------------------------------------- Unit 18 (Ch 13)
    w1, w2, w3 = 0.3, 0.4, 0.5
    F12 = (w1 + w2 - w3) / (2 * w1)
    F13 = (w1 + w3 - w2) / (2 * w1)
    F21 = w1 * F12 / w2
    F23 = (w2 + w3 - w1) / (2 * w2)
    F31 = w1 * F13 / w3
    F32 = w2 * F23 / w3
    T1, T2 = 500.0, 300.0
    q12 = w1 * F12 * SIGMA * (T1 ** 4 - T2 ** 4)
    P["u18"] = [fill(problem(
        "18a", "View factors in a long triangular duct", "exam", 12,
        "A long duct has a right-triangle cross-section with sides $w_1=0.3$ m, $w_2=0.4$ m and $w_3=0.5$ m (flat surfaces, no self-view). (a) Find all nine view factors using the summation rule, reciprocity and (for a triangle) the crossed-strings form $F_{12}=(w_1+w_2-w_3)/(2w_1)$. "
        "(b) If surfaces 1 and 2 are black at 500 K and 300 K, find the net radiation from 1 to 2 per unit length.",
        ["$w_1=0.3$, $w_2=0.4$, $w_3=0.5$ m", "$T_1=500$ K, $T_2=300$ K (black)"],
        ["$F_{ij}$", "$q'_{1\\to2}$"],
        [T("No self-view, so $F_{11}=F_{22}=F_{33}=0$. $F_{12}=\\dfrac{w_1+w_2-w_3}{2w_1}=<<F12:.4f>>$, $F_{13}=1-F_{12}=<<F13:.4f>>$ (check: $\\dfrac{w_1+w_3-w_2}{2w_1}=<<F13:.4f>>$)."),
         T("Reciprocity $A_iF_{ij}=A_jF_{ji}$ (per unit length $A=w$): $F_{21}=w_1F_{12}/w_2=<<F21:.4f>>$, $F_{31}=w_1F_{13}/w_3=<<F31:.4f>>$."),
         T("Summation: $F_{23}=1-F_{21}=<<F23:.4f>>$ and $F_{32}=1-F_{31}=<<F32:.4f>>$; check reciprocity $w_2F_{23}=<<c1:.4f>>=w_3F_{32}=<<c2:.4f>>$ ✓."),
         T("$q'_{1\\to2}=A_1'F_{12}\\sigma(T_1^4-T_2^4)=0.3(<<F12:.4f>>)(5.67\\times10^{-8})(500^4-300^4)=<<q:.1f>>$ W/m.")],
        [T("$F_{12}=<<F12:.3f>>$, $F_{13}=<<F13:.3f>>$, $F_{21}=<<F21:.3f>>$, $F_{23}=<<F23:.3f>>$, $F_{31}=<<F31:.3f>>$, $F_{32}=<<F32:.3f>>$"), T("$q'_{1\\to2}=<<q:.1f>>$ W/m")],
        hint="Use reciprocity to get the 'backwards' factors, summation to finish each row."),
        F12=F12, F13=F13, F21=F21, F23=F23, F31=F31, F32=F32, c1=w2 * F23, c2=w3 * F32, q=q12)]
    # parallel plates + shield
    e1, e2, e3, Tp1, Tp2 = 0.7, 0.5, 0.1, 600.0, 300.0
    qpp0 = SIGMA * (Tp1 ** 4 - Tp2 ** 4) / (1 / e1 + 1 / e2 - 1)
    R13 = 1 / e1 + 1 / e3 - 1
    R32 = 1 / e3 + 1 / e2 - 1
    qpp1 = SIGMA * (Tp1 ** 4 - Tp2 ** 4) / (R13 + R32)
    T3 = (Tp1 ** 4 - qpp1 * R13 / SIGMA) ** 0.25
    P["u18"].append(fill(problem(
        "18b", "Radiation shield between large parallel plates", "exam", 12,
        "Two large parallel gray plates have $T_1=600$ K, $\\varepsilon_1=0.7$ and $T_2=300$ K, $\\varepsilon_2=0.5$. (a) Find the net radiation flux between them. "
        "(b) A thin shield with $\\varepsilon_3=0.1$ on both sides is placed midway. Find the new flux and the shield temperature. By what percentage does the shield cut the exchange?",
        ["$T_1=600$ K, $\\varepsilon_1=0.7$", "$T_2=300$ K, $\\varepsilon_2=0.5$", "shield $\\varepsilon_3=0.1$ (both sides)"],
        ["$q''_{12}$", "$q''$ with shield, $T_3$", "reduction"],
        [T("No shield: $q''_{12}=\\dfrac{\\sigma(T_1^4-T_2^4)}{1/\\varepsilon_1+1/\\varepsilon_2-1}=<<q0:.0f>>$ W/m²."),
         T("With shield, two gaps in series: $R_{13}=1/\\varepsilon_1+1/\\varepsilon_3-1=<<R13:.2f>>$, $R_{32}=1/\\varepsilon_3+1/\\varepsilon_2-1=<<R32:.2f>>$, so $q''=\\dfrac{\\sigma(T_1^4-T_2^4)}{R_{13}+R_{32}}=<<q1:.0f>>$ W/m²."),
         T("Shield temperature from the first gap: $\\sigma(T_1^4-T_3^4)=q''R_{13}\\Rightarrow T_3=<<T3:.0f>>$ K."),
         T("Reduction: $1-q''_{shield}/q''_{12}=<<red:.0f>>$% — a low-emissivity shield is very effective.")],
        [T("$q''_{12}=<<q0:.0f>>$ W/m²"), T("with shield: $<<q1:.0f>>$ W/m², $T_3=<<T3:.0f>>$ K ($<<red:.0f>>$% reduction)")],
        hint="Treat each gap as a two-plate exchange and add the resistances in series."),
        q0=qpp0, R13=R13, R32=R32, q1=qpp1, T3=T3, red=100 * (1 - qpp1 / qpp0)))
    return P


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    for u, ps in build().items():
        for p in ps:
            print(u, p["id"], "|", " || ".join(p["solution"]["answers"]))
            assert "<<" not in " ".join(p["solution"]["steps"] + p["solution"]["answers"]), p["id"]
    print("F(0-2000)", planck_fraction(2000), "F(0-5000)", planck_fraction(5000))
