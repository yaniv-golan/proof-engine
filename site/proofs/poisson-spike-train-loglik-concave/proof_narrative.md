# Proof Narrative: Concavity of the Poisson Spike-Train Log-Likelihood

## Verdict

**Verdict: PROVED**

The mathematical claim holds: the Poisson spike-train log-likelihood is concave under the stated conditions, making maximum-likelihood fitting a clean convex optimization problem with no local-optima traps.

## What Was Claimed?

In computational neuroscience, a common model for neural spike trains uses an inhomogeneous Poisson process whose firing rate depends on stimulus and spike-history covariates through a link function. The claim states that if this link function is positive, convex, and log-concave, then the log-likelihood of the observed spikes is a concave function of the model parameters. This matters because concavity means any optimization algorithm that finds a peak has found *the* peak — there are no deceptive local maxima. The claim extends to MAP estimation with log-concave priors, covering the regularized case commonly used in practice.

## What Did We Find?

The proof proceeds through the elementary building blocks of convex analysis. The log-likelihood of a Poisson process decomposes into a sum over time bins, each contributing two terms: a spike-count-weighted log-intensity term and a negative intensity term.

The log-intensity term inherits concavity from the log-concavity of the link function. Since the log of a log-concave function is concave by definition, and composing a concave function with the affine linear predictor preserves concavity, each log-intensity term is concave in the parameters. Multiplying by the non-negative spike count (zero or one) preserves this concavity.

The negative intensity term inherits concavity from the convexity of the link function. A convex function composed with an affine map is convex, and negating it produces a concave function. Since the time-bin width is positive, this scaling also preserves concavity.

Summing concave functions yields a concave function, completing the analytic argument. Numerical verification with the exponential link function — which satisfies all three hypotheses — confirmed this at multiple levels. The Hessian matrix was negative semidefinite at every tested point, with the largest eigenvalue at −0.067. An independent analytical derivation showed the Hessian takes the form of a negated positive semidefinite matrix, providing a structural guarantee. Ten random-start optimizations all converged to the same maximum within a spread of less than three millionths.

For the MAP extension, adding a log-concave prior contributes an additional concave term to the objective, preserving overall concavity. A Gaussian prior test confirmed unique convergence with a spread below one billionth.

## What Should You Keep In Mind?

Concavity guarantees that any local maximum is the global maximum, but it does not guarantee that a maximum exists. For unbounded parameter spaces, existence of the MLE may require additional conditions (such as the coercivity provided by the exponential link). The claim as stated addresses concavity and the local-equals-global property, not existence.

The numerical checks use one specific link function (the exponential). The analytic argument covers all link functions satisfying the three hypotheses, but the numerical evidence is illustrative rather than exhaustive. Common functions that satisfy all three conditions include the exponential, the identity on positive reals, and the softplus.

The claim does not assert uniqueness of the maximum — only that every local maximum is global. Strict concavity would additionally give uniqueness, but the claim does not require it.

## How Was This Verified?

This claim was verified through a formal proof-engine workflow combining analytic reasoning with computational confirmation. The analytic argument applies standard convex analysis composition rules, while numerical checks independently verify the Hessian structure and optimization landscape. For full details, see [the structured proof report](proof.md), [the full verification audit](proof_audit.md), or [re-run the proof yourself](proof.py).
