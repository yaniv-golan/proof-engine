# Proof Narrative: Computers had a hidden "math glitch" preventing division by zero until it was patched in 2026.

## Verdict

**Verdict: DISPROVED (with unverified citations)**

This claim is false in every meaningful way — computers have handled division by zero intentionally and predictably for decades, and no patch of any kind was issued in 2026.

## What was claimed?

The claim says that computers contained a hidden, unintentional flaw in how they dealt with dividing numbers by zero, and that this flaw was quietly fixed by some kind of software or hardware patch in 2026. It's the kind of claim that spreads easily because division by zero sounds mysterious — schoolchildren are taught it's "undefined" or "impossible" — so a story about computers secretly struggling with it has intuitive appeal.

## What did we find?

Computers have never had a hidden glitch around division by zero. The behavior is, and has long been, entirely intentional.

The x86 processor — the chip architecture inside most personal computers — has included a dedicated "Division Error" exception since the Intel 8086 in 1978. When a program tries to divide by zero, the CPU deliberately raises this exception (#DE), exactly as designed. This is documented in Intel's official programmer's manual. There is nothing hidden about it.

The IEEE 754 standard, which governs floating-point arithmetic across virtually all modern hardware and programming languages, was ratified in 1985 and explicitly defines five exception types. Division by zero is one of them. For floating-point numbers, dividing a nonzero number by zero produces positive or negative infinity; dividing zero by zero produces NaN (Not a Number). Both outcomes are fully specified. The standard describes this behavior as producing a "well-defined result" — the direct opposite of a glitch.

This intentional design goes back even further than 1978. The IBM System/360, introduced in 1964, already handled division by zero as a defined trap condition. There is no era of computing history in which this behavior was accidental or hidden.

As for the alleged 2026 patch: a systematic search of CPU errata databases, OS security bulletins, and IEEE standards revision history found nothing. Microsoft's March 2026 Patch Tuesday covered 79 vulnerabilities — SQL Server, Windows, .NET — none touching arithmetic behavior. No Intel, AMD, or ARM microcode update in 2026 addressed division by zero. The IEEE 754 standard was not revised in 2026. The "patch" does not exist.

## What should you keep in mind?

Division by zero genuinely does cause programs to crash or produce errors — that part isn't a myth. But this happens *because the hardware raises a defined exception*, not because of a bug. The confusion likely arises from mixing up "this causes an error" with "this is a glitch." They are not the same thing. A designed alarm is not a hidden flaw.

It's also worth noting that the famous 1994 Pentium FDIV bug is sometimes misremembered in this context. That bug caused tiny inaccuracies in floating-point division for specific rare operand pairs — it had nothing to do with division by zero, and it was fixed in 1994, not 2026.

Two of the three sources cited in the underlying proof were only partially verified due to technical matching limitations during quote retrieval. This doesn't affect the conclusion — the third source was fully verified, and all three agree — but it explains the "with unverified citations" qualifier in the verdict.

## How was this verified?

The proof checked two sub-claims independently: whether division-by-zero handling was ever an unintentional glitch, and whether any 2026 patch exists. Three independent sources were evaluated against the claim, and adversarial searches were conducted specifically to find any evidence supporting the "2026 patch" story. Full details are in [the structured proof report](proof.md) and [the full verification audit](proof_audit.md), and you can [re-run the proof yourself](proof.py).