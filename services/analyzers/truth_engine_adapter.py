from __future__ import annotations
from typing import Dict, Any, List
import re

from vendor.truth_engine import TruthEngine

"""
TRUTH ENGINE ADAPTER - Court-Safe Output Layer
==============================================
Maps TruthEngine's internal analysis to court-survivable language.

TruthEngine returns:
    - truth_gradient (0-100 percentage)
    - evidence_strength (0-100)
    - emotional_coherence (0-100)
    - bias_density (0-100)
    - pragmatic_reality (0-100)
    - bias_breakdown (dict of detected patterns)
    - assessment (dict with gradient_assessment, brutal_truth, etc.)
    - emotional_profile (dict)

This adapter sanitizes to:
    - coherence_score (0-1 scale)
    - truth_gradient (0-1 scale)
    - consistency_flags (list of observed patterns, neutral language)
    - contradiction_count (integer)
    - evidence_gaps (list of missing corroboration points)
    - recommended_followups (list of suggested clarifications)

NO psycho-diagnostic language. NO "reading" jurors. NO archetype labels.
"""

# Forbidden terms that must never appear in output
FORBIDDEN_TERMS = [
    "delusion", "delusional", "lying", "liar", "manipulat",
    "psycho", "narcissi", "borderline", "trauma", "abuse",
    "diagnos", "disorder", "patholog", "predict verdict",
    "will vote", "likely to convict", "archetype"
]

def _sanitize_text(text: str) -> str:
    """Remove any forbidden diagnostic language."""
    result = text
    for term in FORBIDDEN_TERMS:
        result = re.sub(term, "[REDACTED]", result, flags=re.IGNORECASE)
    return result

def _extract_consistency_flags(bias_breakdown: Dict[str, float], threshold: float = 10.0) -> List[str]:
    """
    Convert bias detections to neutral consistency flags.
    Uses court-safe language: "observed pattern" not "bias detected".
    """
    flags = []
    
    # Map internal bias names to neutral observation language
    NEUTRAL_MAPPING = {
        "self_soothing": "Observed minimization language pattern",
        "continuity_illusion": "Observed continuity assertion without temporal markers",
        "moral_compression": "Observed value-claim without supporting specifics",
        "comparative_cushioning": "Observed comparative framing",
        "predictive_inflation": "Observed future-certainty language",
        "competence_halo": "Observed self-assessment without external corroboration",
        "causal_fantasy": "Observed causal attribution without mechanism",
        "social_camouflage": "Observed normalization language",
        "relational_deflection": "Observed external attribution pattern",
        "safety_projection": "Observed closure-assertion language",
        "abuse_normalization": "Observed acceptance framing",
        "fragmented_agency": "Observed constraint language",
        "hyper_competence_mask": "Observed self-sufficiency assertion",
    }
    
    for bias_name, score in bias_breakdown.items():
        if score >= threshold:
            neutral_label = NEUTRAL_MAPPING.get(bias_name, f"Observed pattern: {bias_name.replace('_', ' ')}")
            flags.append(neutral_label)
    
    return flags

def _generate_evidence_gaps(evidence_strength: float, text: str) -> List[str]:
    """Generate list of missing corroboration points based on evidence score."""
    gaps = []
    
    if evidence_strength < 50:
        gaps.append("No external data points referenced to support claims")
    if evidence_strength < 30:
        gaps.append("Statements lack temporal specificity")
    
    # Check for common unsupported claim patterns
    text_lower = text.lower()
    if "always" in text_lower or "never" in text_lower:
        gaps.append("Absolute terms used without documented frequency data")
    if "everyone" in text_lower or "nobody" in text_lower:
        gaps.append("Universal quantifiers used without sample verification")
    if re.search(r"\bi know\b|\bi believe\b|\bi think\b", text_lower):
        gaps.append("Subjective certainty expressed without corroborating source")
    
    return gaps[:10]  # Cap at 10

def _generate_followups(bias_breakdown: Dict[str, float], evidence_strength: float) -> List[str]:
    """Generate recommended clarification questions."""
    followups = []
    
    if evidence_strength < 40:
        followups.append("Request specific dates, times, or documented instances")
    
    if bias_breakdown.get("predictive_inflation", 0) > 10:
        followups.append("Clarify basis for future-outcome statements")
    
    if bias_breakdown.get("comparative_cushioning", 0) > 10:
        followups.append("Request direct description without comparative framing")
    
    if bias_breakdown.get("social_camouflage", 0) > 10:
        followups.append("Ask for specific personal experience rather than generalized norms")
    
    if not followups:
        followups.append("No additional clarification recommended at this time")
    
    return followups[:10]  # Cap at 10

def truth_engine_safe_summary(text: str) -> Dict[str, Any]:
    """
    Runs TruthEngine internally but returns court-safe, non-diagnostic language.

    IMPORTANT:
    - This is NOT a psychological profile.
    - Outputs describe internal consistency of statements and evidence linkage.
    - All language is observational, not diagnostic or predictive.
    """
    engine = TruthEngine()
    raw = engine.analyze(text)

    # Extract and normalize scores (TruthEngine returns 0-100, we normalize to 0-1)
    truth_gradient = float(raw.get("truth_gradient", 0.0) or 0.0) / 100.0
    evidence_strength = float(raw.get("evidence_strength", 0.0) or 0.0)
    emotional_coherence = float(raw.get("emotional_coherence", 0.0) or 0.0) / 100.0
    bias_density = float(raw.get("bias_density", 0.0) or 0.0)
    
    # Get bias breakdown for pattern extraction
    bias_breakdown = raw.get("bias_breakdown", {}) or {}
    
    # Generate court-safe outputs
    consistency_flags = _extract_consistency_flags(bias_breakdown)
    evidence_gaps = _generate_evidence_gaps(evidence_strength, text)
    followups = _generate_followups(bias_breakdown, evidence_strength)
    
    # Count contradictions: high bias density + low coherence = internal inconsistency
    contradiction_count = len([f for f in consistency_flags if "without" in f.lower() or "assertion" in f.lower()])
    if bias_density > 50 and emotional_coherence < 0.5:
        contradiction_count += 1

    return {
        "coherence_score": round(emotional_coherence, 4),
        "truth_gradient": round(truth_gradient, 4),
        "consistency_flags": consistency_flags[:20],
        "contradiction_count": contradiction_count,
        "evidence_gaps": evidence_gaps[:20],
        "recommended_followups": followups[:20],
        # Additional court-safe metrics
        "evidence_strength_pct": round(evidence_strength, 1),
        "statement_density_flags": len(consistency_flags),
    }
