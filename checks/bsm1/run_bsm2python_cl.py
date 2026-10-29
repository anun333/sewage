#!/usr/bin/env python3
"""run_bsm2python_cl.py: BSM1 closed loop in bsm2-python (BSM1CL), for bsm1clkpi.py and bsm1cmp.py.

  run_bsm2python_cl.py CONFIG INPUTS WEATHER OUT.csv [OWN.csv] [STEP_MIN] [STAB_DAYS] [--src DIR]
      The report's closed-loop protocol (Appendix 5): STAB_DAYS (default 150) days
      at constant influent (Table 5, 15 degC), 14 days of dry weather, 14 days of
      WEATHER (dry, rain or storm; rain and storm with SI = 30*Qdry/Q, see README),
      STEP_MIN-minute steps (default 1, upstream's recommendation). INPUTS is the
      folder with the IWA files Inf_{dry,rain,strm}_2006.txt and sennoise.asc.
      CONFIG:
        report   the report's closed loop, as class ReportCL below: KLa3 = KLa4 =
                 240 1/d; nitrate sensor range 0-20 g N/m3 (Table 14; noise 0.5);
                 noise columns 1 (DO) and 2 (nitrate) of sennoise.asc, interpolated
                 linearly, off during stabilization and restarted with each 14-day
                 file; influent interpolated linearly to every step. Everything
                 else is BSM1CL's own: its sensor, PID and actuator classes, gains,
                 limits and order of operations.
        shipped  BSM1CL unmodified: KLa3 = KLa4 = 201.30 (its KLA3_INIT,
                 KLA4_INIT); nitrate sensor range 0-10; the package's
                 sensornoise.csv, one column for both sensors, looked up at the
                 simulation time; each influent sample held until the next (its
                 own behaviour). sennoise.asc is not read.
      Writes 15-minute samples of the last 28 days as t = 0..28: the columns of
      run_bsm2python.py, then Qa, KLa3, KLa4, KLa5 (the values applied from that
      sample to the next step), SO5_true, SO5_meas, SNO2_true, SNO2_meas (tank 5's
      oxygen and tank 2's nitrate, and the sensor signals the controllers saw at
      that sample), u_kla5, u_qintr (the PID outputs) and I_kla5, I_qintr (the PID
      integral states). OWN.csv ('-' for none) gets bsm2-python's own IQ, EQ, AE,
      PE and ME over the last 7 days.
      --src DIR imports bsm2-python from DIR, a checkout's src/ (main, or a pull
      request's head), ahead of any installed copy.
"""
import csv, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = sys.argv[1:]
if '--src' in ARGS:
    _k = ARGS.index('--src')
    sys.path.insert(0, os.path.abspath(ARGS[_k + 1]))
    del ARGS[_k:_k + 2]
sys.path.append(HERE)                                   # run_bsm2python.py's influent helpers

import numpy as np                                                   # noqa: E402
import bsm2_python.bsm2.init.asm1init_bsm1 as asm1init               # noqa: E402
from bsm2_python.bsm1_base import BSM1Base                           # noqa: E402
from bsm2_python.bsm1_cl import BSM1CL                               # noqa: E402
from bsm2_python.bsm2.aerationcontrol import Sensor                  # noqa: E402
from bsm2_python.bsm2.init import aerationcontrolinit_bsm1 as ac     # noqa: E402
from run_bsm2python import CONST, IQ_, ITSS, ST, influent, row21     # noqa: E402

ISO, ISNO = 7, 8                                         # bsm2-python indices of SO and SNO


class ReportCL(BSM1CL):
    """BSM1CL with the report's KLa3/KLa4, nitrate sensor range and noise columns."""

    def setup(self, noise_path, t0):
        sen = np.loadtxt(noise_path)                     # t, then 25 noise columns, 1-minute samples, 14 days
        self.sen_t, self.sen_do, self.sen_no = sen[:, 0], sen[:, 1], sen[:, 2]
        self.t0 = t0
        T = ac.T_SNO2
        den = [T ** 8, 8 * T ** 7, 28 * T ** 6, 56 * T ** 5, 70 * T ** 4, 56 * T ** 3, 28 * T ** 2, 8 * T, 1]
        self.sno2_sensor = Sensor(1, den, 0, 20, ac.STD_SNO2)       # Table 14: 0-20 g N/m3, 0.025*20 = 0.5
        self.kla3_a = self.kla4_a = 240.0

    def step(self, i, so4ref=None, sno2ref=None):
        """BSM1CL.step with the noise columns above; the rest as upstream's."""
        self.kla5_pid.setpoint = ac.SO4REF if so4ref is None else so4ref
        sno2ref = ac.SNO2REF if sno2ref is None else sno2ref
        self.qintr_pid.setpoint = sno2ref
        t, h = self.simtime[i], self.timesteps[i]
        if t < self.t0 - 1e-9:                           # stabilization: no noise
            n_do = n_no = 0.0
        else:                                            # the noise file restarts with each 14-day file
            tau = (t - self.t0) if t < self.t0 + 14 - 1e-9 else (t - self.t0 - 14)
            n_do = float(np.interp(tau, self.sen_t, self.sen_do))
            n_no = float(np.interp(tau, self.sen_t, self.sen_no))
        self.sno2_signal = self.sno2_sensor.output(self.y_out2[ISNO], h, n_no)
        inject = ac.KFEEDFORWARD * (sno2ref / (sno2ref + 1)) * (asm1init.QIN * ac.QFFREF - self.qintr)
        self.qintr_pid_signal = self.qintr_pid.output(self.sno2_signal, h, inject)
        self.qintr = self.qintr_actuator.output(self.qintr_pid_signal, h)
        self.so5_signal = self.so5_sensor.output(self.y_out5[ISO], h, n_do)
        self.kla5_pid_signal = self.kla5_pid.output(self.so5_signal, h)
        self.kla5_a = self.kla5_actuator.output(self.kla5_pid_signal, h)
        self.klas = np.array([0, 0, self.kla3_a, self.kla4_a, self.kla5_a])
        BSM1Base.step(self, i)


def run(config, inputs, weather, out, own=None, step_min=1.0, stab=150.0):
    step_min, T0 = float(step_min), float(stab)
    spm = int(round(15 / step_min))                      # steps per 15-minute sample
    dt = step_min / 1440
    inf = np.array(influent(inputs, weather, 'hosted' if weather == 'dry' else 'diluted'))   # (2689, 14)
    T1 = T0 + (len(inf) - 1) / 96
    grid = np.arange(0, T1 + dt / 2, dt)                 # the same floats BSMBase's arange gives
    k0 = int(round(T0 / dt))
    if config == 'shipped':                              # each sample held until the next
        samp = grid[k0::spm][:len(inf)]
        rows = [np.r_[0.0, row21(CONST)]] + [np.r_[t, row21(c)] for t, c in zip(samp, inf)]
    else:                                                # linear between samples, at every step
        tt = grid[k0:] - T0
        lin = np.column_stack([np.interp(tt, np.arange(len(inf)) / 96, inf[:, j]) for j in range(14)])
        rows = [np.r_[0.0, row21(CONST)]] + [np.r_[t, row21(c)] for t, c in zip(grid[k0:], lin)]
    rows.append(np.r_[T1 + 1.0, rows[-1][1:]])           # BSMBase needs data past the end time
    data = np.array(rows)
    last = np.arange(0, T1 + 1.0, dt)
    last = last[last <= T1][-1]                          # BSMBase's last simtime
    kw = dict(data_in=data, timestep=dt, endtime=T1, evaltime=np.array([T1 - 7.0, last]),
              tempmodel=False, activate=False)
    if config == 'shipped':
        m = BSM1CL(use_noise=1, **kw)
    else:
        m = ReportCL(use_noise=0, **kw)
        m.setup(os.path.join(inputs, 'sennoise.asc'), T0)
    n = len(m.simtime)
    head = ['t', 'Qin'] + [v + '_in' for v in ST] + ['Qe'] + [v + '_e' for v in ST] + ['Qw'] + \
        [v + '_u' for v in ST] + [f'TSS_r{k}' for k in range(1, 6)] + [f'TSS_s{j}' for j in range(1, 11)] + \
        ['Qa', 'KLa3', 'KLa4', 'KLa5', 'SO5_true', 'SO5_meas', 'SNO2_true', 'SNO2_meas', 'u_kla5', 'u_qintr',
         'I_kla5', 'I_qintr']
    plant, ctrl = {}, {}
    t0 = time.time()
    for i in range(n):
        so5, sno2 = m.y_out5[ISO], m.y_out2[ISNO]        # states at grid[i], what the sensors read
        m.step(i)
        if i >= k0 and (i - k0) % spm == 0:              # controller signals at grid[i]
            ctrl[i - k0] = [m.qintr, m.kla3_a, m.kla4_a, m.kla5_a, so5, m.so5_signal, sno2, m.sno2_signal,
                            m.kla5_pid_signal, m.qintr_pid_signal, m.kla5_pid.integral, m.qintr_pid.integral]
        j = i + 1                                        # plant states now at grid[j]
        if j >= k0 and (j - k0) % spm == 0 and j < len(grid):
            yin = data[np.where(m.data_time <= grid[j])[0][-1], 1:]
            qw = min(385.0, m.ys_in[IQ_] - 18446.0)
            plant[j - k0] = [yin[IQ_], *yin[:13], m.ys_eff[IQ_], *m.ys_eff[:13], qw, *m.ys_out[:13],
                             m.y_out1[ITSS], m.y_out2[ITSS], m.y_out3[ITSS], m.y_out4[ITSS], m.y_out5[ITSS],
                             *m.ys_tss_internal]
    with open(out, 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(head)
        for k in sorted(set(plant) & set(ctrl)):
            w.writerow([repr(k / (96 * spm))] + [repr(float(x)) for x in plant[k] + ctrl[k]])
    iqi, eqi, me, pe, ae = m.get_final_performance()
    if own and own != '-':
        with open(own, 'w', newline='') as g:
            ww = csv.writer(g, lineterminator='\n'); ww.writerow(['case', 'block', 'var', 'value'])
            for k, v in (('IQ', iqi), ('EQ', eqi), ('ME', me), ('PE', pe), ('AE', ae)):
                ww.writerow([f'cl_{weather}', 'own', k, repr(float(v))])
    print(f'bsm2-python BSM1CL {config} {weather}: {n} steps of {step_min:g} min, {time.time() - t0:.0f} s; '
          f'own IQ {iqi:.4f} EQ {eqi:.4f} AE {ae:.2f}; final integrals KLa5 {m.kla5_pid.integral:.4g} '
          f'Qintr {m.qintr_pid.integral:.6g}')


if __name__ == '__main__':
    if len(ARGS) in (4, 5, 6, 7) and ARGS[0] in ('report', 'shipped') and ARGS[2] in ('dry', 'rain', 'storm'):
        run(*ARGS)
    else:
        print(__doc__); sys.exit(2)
