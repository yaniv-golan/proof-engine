# Proof Narrative: Quantum entanglement enables the transmission of usable information faster than the speed of light when the distant parties pre-agree on a measurement basis.

## Verdict

**Verdict: DISPROVED**

This claim is false. Quantum mechanics has a theorem that rules it out — and every authoritative source consulted confirms it.

## What was claimed?

The claim is that two people sharing entangled particles could use them as a communication channel faster than light, as long as they agree in advance on how to perform their measurements. This idea circulates widely in popular science discussions, often framed as a clever workaround: if both parties already know the "code," couldn't they exploit the instantaneous correlations of entanglement to send a message without waiting for a light-speed signal?

It's an appealing idea because entanglement genuinely is strange — particles really do become correlated across any distance, and measuring one does instantly affect the quantum state of the other. The leap to "therefore we can send information" is understandable, but it's wrong.

## What did we find?

Quantum mechanics contains a result called the no-communication theorem. It is not a provisional finding or a rule of thumb — it is mathematically proven. The theorem states that measuring one half of an entangled pair cannot transmit any information to the holder of the other half, regardless of how far apart they are or what measurement protocol they use.

Here is the core reason the pre-agreed basis idea fails. When Alice measures her particle, she gets a random outcome — say, spin-up or spin-down, each with 50% probability. When Bob measures his particle, he also gets a random outcome. Individually, neither of them sees anything but noise. The eerie part of entanglement is that their results are *correlated* — when they later compare notes, they find a pattern. But "comparing notes" requires a classical message, which can travel no faster than light. Until that message arrives, Bob has no way to tell whether Alice has measured yet, let alone what she found. A pre-agreed basis gives both parties the same decoder ring, but there is nothing to decode — Bob's local data is pure randomness either way.

Caltech's Science Exchange states directly: "Experiments have shown that this is not true, nor can quantum physics be used to send faster-than-light communications." The EU Quantum Flagship research consortium puts it even more plainly: "The catch is that we are not actually sending any information."

Four independent sources — from Wikipedia's no-communication theorem article, Caltech, Wikipedia's faster-than-light communication article, and the EU Quantum Flagship consortium — were consulted and all confirmed the same conclusion. Additionally, an active search for any credible peer-reviewed physics paper demonstrating FTL communication via entanglement found nothing. Proposed schemes have been put forward over the years and each has been refuted. No experiment has ever achieved superluminal information transfer.

## What should you keep in mind?

The correlations in entanglement are real and genuinely instantaneous across distance — that part is not in dispute. What cannot happen is using those correlations to *carry a message*. The distinction matters: correlation is not communication. Nothing about a pre-agreed protocol changes this, because the bottleneck is not the measurement choice but the randomness of the outcomes themselves.

It is also worth noting that one of the four sources consulted (the EU Quantum Flagship site) comes from a domain that is not automatically classified as a top-tier academic source. However, the disproof does not rest on that source alone. The other three — two Wikipedia articles drawing on peer-reviewed physics literature, and Caltech — independently establish the same conclusion.

Finally, this verdict addresses information transfer specifically. Entanglement does enable other remarkable things, including quantum cryptography and quantum computing. Those applications are real and do not require FTL communication. The disproof here is narrow: the claim that entanglement can be used as a faster-than-light messaging channel is false.

## How was this verified?

This verdict was produced by a structured proof process that formally specified the claim, identified and verified four independent authoritative sources, and ran three adversarial searches designed to find any evidence supporting the claim. You can read the full reasoning in [the structured proof report](proof.md), inspect every citation and computation step in [the full verification audit](proof_audit.md), or [re-run the proof yourself](proof.py).