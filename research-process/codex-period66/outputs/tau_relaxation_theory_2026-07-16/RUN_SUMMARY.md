# Multiplier-Relaxation Interval Certificate

- exact certificate valid: `True`
- theorem scope: fixed rational QP; local result for nearby states and a finite-prefix result for the original period-66 initial point

## Common Lyapunov Interval

- tau interval: `49/100 <= tau <= 51/100`
- common contraction-factor upper bound: `0.99985082128383873917`
- projection-safe ellipsoid alpha: `164.12642634841359579494`
- proof: exact endpoint Sylvester minors plus Loewner concavity of the residual matrix

## Uniform Finite-Prefix Capture

- tau interval: `0.49999999990000 <= tau <= 0.50000000010000`
- strict word: `00, 00, then 01 through step 232`
- minimum uniform sign lower bound: `0.00075690253479337201`
- ellipsoid ratio upper bound at step 232: `0.97537998816016382196`
- interpretation: the small width is a conservative sufficient enclosure, not a claimed stability limit

## Exact Local-Stability Boundary

- factorization: `det(zI-T_01(tau)) = z*(z+tau-1)*Q_tau(z)/405010000000000000`
- unique root bracket: `0.9366061114 < tau_c < 0.9366061115`
- exact conclusion on 0<tau<1: the strict 01 branch is Schur stable iff tau<tau_c

## Boundary of the Result

This artifact proves local stability and one explicit finite-prefix capture interval. It does not prove arbitrary-initial-point global convergence.
