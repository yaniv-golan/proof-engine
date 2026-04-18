# Proof Narrative: Discrete-Time Rescaling via R_m = A_m - log(1 - U_m p_{tau_m}) Yields Exact Exp(1)

## Verdict

**Verdict: PROVED**

The proposed discrete-time rescaling formula produces exact exponential residuals for any correctly specified spike train model, enabling valid goodness-of-fit testing.

## What Was Claimed?

When neuroscientists fit statistical models to neural spike data recorded in discrete time bins, they need a rigorous way to check whether their model is correct. This claim proposes a specific recipe: for each interspike interval, accumulate the negative log-survival probabilities over the silent bins, then add a particular randomized correction at the spike bin using \(-\log(1 - U \cdot p)\) where \(U\) is a uniform random draw and \(p\) is the spike probability. The claim is that the resulting numbers are exactly independent standard exponential random variables — which would make standard statistical tests like KS and Q-Q plots directly applicable.

## What Did We Find?

The claim is true, and the proof rests on a well-established result in probability theory: the randomized probability integral transform (PIT). For any discrete random variable with a known CDF, randomizing within the CDF's jumps produces exact uniform random variables. The interspike interval in a discrete-time spike model is exactly such a discrete random variable, and the formula in the claim turns out to be precisely the PIT applied to the survival function of that interval.

We verified this in two independent ways. First, we showed analytically that the claimed formula \(Z_m = 1 - \exp(-R_m)\) is algebraically identical to the PIT formula \(F(\tau^-) + U \cdot [F(\tau) - F(\tau^-)]\). The two expressions agree to machine precision — exactly zero difference across all test cases. We then computed the CDF of the resulting random variable by summing over geometric probabilities: \(P(Z \leq z) = z\) for every tested value, with errors of order \(10^{-16}\).

Second, we ran Monte Carlo simulations with 100,000 interspike intervals under three different models: constant spike probability 0.3, constant probability 0.5, and a sinusoidally time-varying probability. In all three cases, the Kolmogorov-Smirnov test for exponentiality passed comfortably, with test statistics roughly 0.003 against a critical threshold of 0.004. The sample means were all within 0.4% of 1.0, and variances within 1.1% of 1.0 — exactly what one would expect from an exponential distribution.

We also tested whether the rescaled intervals are truly independent (not just individually exponential). The lag-1 and lag-2 serial correlations were both indistinguishable from zero. The theoretical argument for independence is elegant: since each rescaled interval's conditional distribution given the past is Uniform(0,1) — and this distribution doesn't depend on what that past was — the intervals must be unconditionally independent as well.

## What Should You Keep In Mind?

This result applies only when the model is correctly specified — meaning the conditional spike probabilities \(p_k\) truly match the data-generating process. If the model is wrong, the residuals will deviate from Exp(1), which is the whole point of using them as diagnostics. The formula requires \(p_k \in (0,1)\); the degenerate cases \(p_k = 0\) (impossible spike) and \(p_k = 1\) (certain spike) are excluded. This formula differs crucially from a simpler-looking variant that uses linear interpolation in the hazard domain (\(A_m + U \cdot h_{\tau_m}\)), which was previously shown to be only an approximation, not exact.

## How Was This Verified?

This claim was evaluated using a formal proof engine combining analytical computation with Monte Carlo simulation, validated by independent cross-checks and adversarial analysis. For the complete evidence, see [the structured proof report](proof.md), [the full verification audit](proof_audit.md), or [re-run the proof yourself](proof.py).
