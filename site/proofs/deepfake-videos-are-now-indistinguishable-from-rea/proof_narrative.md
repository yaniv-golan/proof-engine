# Proof Narrative: Deepfake videos are now indistinguishable from real footage to the average human eye.

## Verdict

**Verdict: DISPROVED**

The claim sounds plausible — deepfakes have gotten eerily good — but the research tells a different story: average people can still tell fake video from real, more often than not.

## What was claimed?

The claim is that deepfake videos have reached a point where the typical person simply cannot tell them apart from genuine footage. This matters because it underpins a lot of anxiety about AI-generated misinformation: if ordinary viewers are helpless against synthetic video, then deepfakes become a nearly undetectable weapon for fraud, propaganda, and manipulation.

## What did we find?

Two large peer-reviewed studies directly measured how well ordinary people detect deepfake videos — and both found performance clearly above chance. A University of Florida study involving nearly 1,900 participants found that "the ability to discriminate between deepfake and real videos was fairly good in humans," with a detection score (AUC of 0.67) well above the 0.50 that pure guessing would produce. A separate UK-based study with over 1,000 participants confirmed that "people are better than random at determining whether an individual video is genuine or fake." Across studies, human accuracy on video deepfakes ranges from roughly 57% to 67% — modest, but meaningfully above the 50% floor that "indistinguishable" would require.

A leading deepfake researcher, Prof. Siwei Lyu of the University at Buffalo's Media Forensic Lab, offered a telling distinction. He described voice cloning as having crossed "the indistinguishable threshold" — but deliberately used different language for video, saying realism is now high enough to "reliably fool nonexpert viewers." That's a weaker claim than indistinguishable, and the phrasing appears intentional. No expert source reviewed for this proof argued that video deepfakes have crossed that same threshold as of early 2026.

One widely shared statistic deserves closer scrutiny: a study finding that only 0.1% of people could accurately identify all AI-generated content. That figure measures perfect classification across an entire test battery of images and videos — a much harder bar than correctly identifying any single deepfake. It does not mean people are helpless on individual clips.

A meta-analysis covering dozens of studies did find that the pooled average video detection rate (57%) had a confidence interval that dipped below 50%, which some might take as evidence of chance-level performance. But that wide interval reflects variation across studies — different deepfake technologies, different populations, different methodologies — not evidence that humans are truly at chance. The largest, most carefully controlled individual studies consistently show above-chance performance.

## What should you keep in mind?

The disproof is real, but it comes with important caveats. Human detection is modest — 57–67% is not impressive, and it almost certainly varies with deepfake quality. As generation technology improves, that window may close. The claim may become true in the near future even if it isn't yet. Additionally, "above chance" detection in a controlled lab setting may not translate to real-world alertness, where people aren't primed to look for fakes. The research also shows that voice deepfakes have already crossed the indistinguishable threshold, which means the broader concern about AI-generated deception is well-founded — it just applies more acutely to audio than to video right now.

## How was this verified?

This claim was evaluated by searching for peer-reviewed studies and expert assessments measuring human detection of deepfake video, then checking whether at least three independent sources confirmed above-chance performance — the threshold required to disprove the "indistinguishable" characterization. Full details of the evidence and citation checks are in [the structured proof report](proof.md) and [the full verification audit](proof_audit.md); to inspect or re-run the underlying logic, see [re-run the proof yourself](proof.py).