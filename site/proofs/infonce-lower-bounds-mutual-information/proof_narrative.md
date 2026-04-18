# Proof Narrative: InfoNCE Loss Lower Bound on Mutual Information

## Verdict

**Verdict: PROVED**

The InfoNCE contrastive loss does indeed provide a valid lower bound on mutual information, with the pointwise mutual information as its optimal score, and the bound gets tighter as you use more negative samples.

## What Was Claimed?

In contrastive learning, a model learns representations by distinguishing a "positive" sample (drawn from the true conditional distribution) from a set of "negative" samples (drawn from the marginal). The InfoNCE loss function, introduced by Oord et al. in 2018, is the workhorse of this approach -- powering methods from SimCLR to CLIP. The claim here is threefold: first, that minimizing InfoNCE is equivalent to maximizing a lower bound on the mutual information between inputs and outputs; second, that the best possible scoring function is the log-ratio of the conditional to marginal densities (the pointwise mutual information); and third, that using more negative samples makes this bound tighter, bringing it closer to the true mutual information.

These properties matter because they provide the theoretical foundation for why contrastive learning works: it implicitly maximizes a mutual information objective.

## What Did We Find?

We tested all three properties numerically using Monte Carlo simulation with 100,000 samples per configuration, across two fundamentally different probability distributions: a continuous bivariate Gaussian (with four different correlation strengths) and a discrete 3x3 joint distribution with asymmetric structure.

For the lower bound property, we computed the InfoNCE bound across 32 combinations of correlation strength and number of negative samples. In every single case, the bound remained below the true mutual information. For instance, with correlation 0.8 and 256 negative samples, the bound reached 0.508 nats against a true mutual information of 0.511 nats -- close but never exceeding the truth.

For optimality, we compared the pointwise mutual information scoring function against a simpler linear score. The PMI score consistently achieved lower loss, winning by margins from 0.076 to 0.313 nats depending on the setting. No configuration showed the linear score matching or beating PMI.

For tightening, we tracked the bound as we increased the number of negative samples from 2 to 512. The bound grew monotonically in every tested case. With strong correlation (0.95), the bound climbed from 0.430 nats at N=2 to 1.163 nats at N=512, closing to within 0.001 nats of the true value of 1.164 nats.

All results were consistent across both the Gaussian and discrete distribution families, providing independent confirmation on structurally different probability spaces.

## What Should You Keep In Mind?

This proof verifies the claim numerically on specific distributions rather than providing a universal analytical derivation. The analytical proof, which relies on Jensen's inequality and properties of the KL divergence, is well-established in the literature but is not what this script produces. The numerical verification found no exceptions across 38+ test configurations on two distribution families, which is strong evidence but not the same as a proof over all possible distributions.

There is also the important caveat, documented by McAllester and Stratos (2020), that the InfoNCE bound is capped at log N for any finite number of negative samples. This means that when the true mutual information is large, you need exponentially many negative samples to get a tight estimate. The claim says the bound "tightens," which is true, but the rate of tightening can be slow for high-MI distributions.

## How Was This Verified?

This claim was verified using the Proof Engine framework, which structures mathematical verification into re-runnable code with adversarial stress-testing. The full details are available in [the structured proof report](proof.md), [the full verification audit](proof_audit.md), and you can [re-run the proof yourself](proof.py) to independently confirm all results.
