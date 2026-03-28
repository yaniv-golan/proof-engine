import re

TAG_KEYWORDS = {
    "economics": ["gdp", "inflation", "cpi", "monetary", "fiscal", "currency",
                   "purchasing power", "federal reserve", "interest rate", "debt",
                   "deficit", "trade", "tariff", "recession", "unemployment"],
    "neuroscience": ["neuron", "brain", "cortex", "synapse", "hippocampus",
                     "neurogenesis", "neural", "cognitive", "dopamine",
                     "serotonin", "amygdala", "prefrontal"],
    "history": ["founded", "war", "treaty", "revolution", "empire", "dynasty",
                "colonial", "independence", "assassination", "ancient"],
    "physics": ["quantum", "relativity", "photon", "entropy", "thermodynamic",
                "electromagnetic", "gravitational", "particle", "wavelength"],
    "mathematics": ["prime", "theorem", "conjecture", "proof", "fibonacci",
                    "factorial", "integral", "polynomial", "algebra"],
    "politics": ["election", "parliament", "congress", "senate", "legislation",
                 "diplomatic", "sanctions", "referendum", "sovereignty"],
    "health": ["vaccine", "mortality", "disease", "therapy", "clinical",
               "diagnosis", "epidemi", "pathogen", "symptom"],
    "climate": ["carbon", "greenhouse", "temperature", "emissions", "fossil",
                "renewable", "sea level", "deforestation"],
}


def canonicalize_tag(tag: str) -> str:
    slug = tag.strip().lower()
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    slug = slug.strip("-")

    if not slug:
        raise ValueError(f"Tag canonicalizes to empty string: {tag!r}")
    if not re.match(r"^[a-z0-9-]+$", slug):
        raise ValueError(f"Tag contains invalid characters: {tag!r} -> {slug!r}")

    return slug


def auto_tag(claim_text: str) -> list[str]:
    text_lower = claim_text.lower()
    matched = set()
    for tag, keywords in TAG_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                matched.add(tag)
                break
    return sorted(matched)
