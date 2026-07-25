# Verification Summary

Verdict: `correct` for the stated local and fixed-initial scopes.

The exact audit closes four independent mathematical gates:

1. the affine branch matrices are re-derived from the original four ADMM updates;
2. endpoint Sylvester minors plus an exact chord identity certify one common
   Lyapunov matrix on \([49/100,51/100]\);
3. a 232-step rational sensitivity enclosure certifies a nonempty closed tau
   interval for the original period-66 initial point;
4. Schur recursion and Sturm root counting identify the strict `01` branch
   boundary as the unique root of an explicit integer cubic.

The accepted statement is not an arbitrary-initial global convergence theorem.
The finite-prefix interval is a conservative sufficient interval and is not
claimed to be maximal.

Provenance: internal fresh Codex verifier-style review, not external independent
review and not Lean/Coq/Isabelle checking.
