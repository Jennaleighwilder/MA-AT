# Truth Engine → MAAT Adapter Notes

The uploaded Truth_Engine uses terms like 'bias', 'score', and 'Outcome Prediction Engine'.
Those semantics are *litigation bait* in an enterprise jury product.

MAAT-safe renames (same computation, safer framing):
- bias_patterns / bias_vector → distortion_indicators / signal_indicators
- scores → indices
- ConsequenceSimulator / Outcome Prediction → Scenario Sensitivity Simulator (aggregate risk conditions, not individuals)
- 'predict' → 'estimate risk conditions' or 'simulate sensitivity' (venue-level / process-level)

Additionally:
- Remove any content-specific personal advice generation.
- Keep only: text feature extraction + pattern density + uncertainty / over-certainty markers.
- Enforce OutputLanguageFirewall on any generated narrative.
