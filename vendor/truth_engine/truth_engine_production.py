#!/usr/bin/env python3
"""
Truth Engine v2.0 - Production Architecture
Reality Calibration System with Five Mirror Array

Built for Jennifer Leigh West's cognitive forensics specifications.
This system delivers unfiltered truth analysis without therapeutic buffering.
"""

import re
import json
import sqlite3
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import math

@dataclass
class Statement:
    """Core data structure for truth analysis"""
    raw_text: str
    tokens: List[str] = None
    propositions: List[str] = None
    affective_waveform: Dict = None
    bias_vector: Dict[str, float] = None
    scores: Dict[str, float] = None
    timestamp: datetime = None

@dataclass
class MirrorResult:
    """Individual mirror analysis result"""
    name: str
    value: float  # 0-1 scale
    notes: str
    confidence: float = 0.8

class BiasClassifier:
    """The Bestiary of Self-Deception - Taxonomy Implementation"""
    
    def __init__(self):
        self.bias_patterns = {
            # PRESERVATION BIASES - To Keep the Self Intact
            'self_soothing': {
                'patterns': [r'not that bad', r'basically', r'pretty good', r'fine', r'okay'],
                'weight': 0.7,
                'description': 'Reduces threat salience to avoid panic'
            },
            'continuity_illusion': {
                'patterns': [r'always been', r'never changed', r'same as always'],
                'weight': 0.6,
                'description': 'Maintains narrative stability'
            },
            'moral_compression': {
                'patterns': [r'good person', r'trying my best', r'mean well'],
                'weight': 0.5,
                'description': 'Overestimates virtue to avoid guilt'
            },
            'comparative_cushioning': {
                'patterns': [r'at least', r'not like them', r'could be worse'],
                'weight': 0.8,
                'description': 'Minimizes dissonance via downward contrast'
            },
            
            # CONTROL BIASES - To Feel Powerful
            'predictive_inflation': {
                'patterns': [r'will work', r'going to', r'should improve'],
                'weight': 0.6,
                'description': 'Treats intent as guarantee'
            },
            'competence_halo': {
                'patterns': [r'good at', r'skilled', r'talented', r'capable'],
                'weight': 0.7,
                'description': 'Projects mastery to shield from humiliation'
            },
            'causal_fantasy': {
                'patterns': [r'because of me', r'my doing', r'made it happen'],
                'weight': 0.5,
                'description': 'Ascribes outcomes to self even when random'
            },
            
            # BELONGING BIASES - To Remain Loved
            'social_camouflage': {
                'patterns': [r'everyone', r'normal', r'usual', r'typical'],
                'weight': 0.6,
                'description': 'Adopts herd language to evade rejection'
            },
            'relational_deflection': {
                'patterns': [r'they\'re just', r'too sensitive', r'overreacting'],
                'weight': 0.8,
                'description': 'Blames others to protect harmony'
            },
            
            # TRAUMA ECHOES - Adaptive Lies
            'safety_projection': {
                'patterns': [r'i\'m fine', r'over it', r'past that', r'moved on'],
                'weight': 0.9,
                'description': 'Nervous system denial'
            },
            'abuse_normalization': {
                'patterns': [r'not abuse', r'normal relationship', r'how relationships work'],
                'weight': 0.9,
                'description': 'Mistakes familiarity for love'
            },
            'fragmented_agency': {
                'patterns': [r'no choice', r'had to', r'couldn\'t help'],
                'weight': 0.7,
                'description': 'Often half-true; used to justify paralysis'
            },
            'hyper_competence_mask': {
                'patterns': [r'handle everything', r'don\'t need help', r'got this'],
                'weight': 0.8,
                'description': 'Overfunctioning as proof of worth'
            }
        }
    
    def classify(self, statement: Statement) -> Dict[str, float]:
        """Detect self-deception patterns in statement"""
        text = statement.raw_text.lower()
        bias_scores = {}
        
        for bias_name, bias_data in self.bias_patterns.items():
            score = 0.0
            pattern_matches = 0
            
            for pattern in bias_data['patterns']:
                matches = len(re.findall(pattern, text))
                if matches > 0:
                    pattern_matches += 1
                    score += matches * bias_data['weight']
            
            # Normalize score based on text length and pattern density
            if pattern_matches > 0:
                text_length_factor = len(text.split()) / 100  # Normalize for text length
                bias_scores[bias_name] = min(1.0, score * text_length_factor)
        
        return bias_scores

class AffectiveMapper:
    """Emotional Resonance Detection System"""
    
    def __init__(self):
        self.emotion_lexicon = {
            'anxiety': ['worried', 'nervous', 'scared', 'afraid', 'anxious'],
            'confidence': ['sure', 'certain', 'confident', 'positive'],
            'doubt': ['maybe', 'perhaps', 'might', 'could be', 'possibly'],
            'defensiveness': ['but', 'however', 'actually', 'really'],
            'minimization': ['just', 'only', 'simply', 'merely']
        }
    
    def map_emotion(self, statement: Statement) -> Dict[str, float]:
        """Build emotional waveform from text"""
        text = statement.raw_text.lower()
        emotional_profile = {}
        
        for emotion, words in self.emotion_lexicon.items():
            count = sum(1 for word in words if word in text)
            emotional_profile[emotion] = count / len(text.split())
        
        # Calculate coherence - do emotions match semantic claims?
        coherence = self._calculate_coherence(text, emotional_profile)
        emotional_profile['coherence'] = coherence
        
        return emotional_profile
    
    def _calculate_coherence(self, text: str, emotions: Dict[str, float]) -> float:
        """Measure alignment between linguistic intent and emotional frequency"""
        # High confidence words + high doubt emotions = low coherence
        confidence_claims = emotions.get('confidence', 0)
        doubt_markers = emotions.get('doubt', 0)
        
        if confidence_claims > 0 and doubt_markers > 0:
            return max(0.0, 1.0 - (doubt_markers / confidence_claims))
        
        return 0.7  # Default moderate coherence

class EvidenceCore:
    """Reality Anchoring System"""
    
    def __init__(self):
        self.baseline_stats = {
            'job_performance': {
                'average_percentile': 50,
                'self_assessment_inflation': 28  # Average overestimation
            },
            'relationship_health': {
                'conflict_avoidance_rate': 73,  # % who avoid difficult conversations
                'satisfaction_decline_prediction': 35  # % likely to decline
            },
            'personal_uniqueness': {
                'normal_distribution': 68,  # % actually in normal range
                'uniqueness_denial_rate': 84  # % who minimize differences
            }
        }
    
    def evaluate_evidence(self, statement: Statement) -> float:
        """Anchor claims to statistical reality"""
        text = statement.raw_text.lower()
        
        # Job performance claims
        if any(phrase in text for phrase in ['good at job', 'work performance', 'job skills']):
            return self._evaluate_job_claims(text)
        
        # Relationship claims
        elif any(phrase in text for phrase in ['relationship', 'partner', 'marriage']):
            return self._evaluate_relationship_claims(text)
        
        # Normalcy claims
        elif any(phrase in text for phrase in ['normal', 'usual', 'not unusual', 'typical']):
            return self._evaluate_normalcy_claims(text)
        
        # Default - no specific evidence available
        return 0.3
    
    def _evaluate_job_claims(self, text: str) -> float:
        """Evaluate job performance claims against statistics"""
        if 'good' in text or 'skilled' in text:
            # Most people think they're above average (impossible)
            return 0.35  # Low evidence strength for unsupported claims
        return 0.5
    
    def _evaluate_relationship_claims(self, text: str) -> float:
        """Evaluate relationship claims"""
        if 'healthy' in text or 'fine' in text or 'good' in text:
            return 0.25  # Very low - these are often defensive
        return 0.4
    
    def _evaluate_normalcy_claims(self, text: str) -> float:
        """Evaluate claims about being normal/typical"""
        if 'not unusual' in text or 'normal' in text:
            return 0.15  # Very low - questioning normalcy indicates unusualness
        return 0.5

class ConsequenceSimulator:
    """Outcome Prediction Engine"""
    
    def simulate_outcomes(self, statement: Statement, bias_scores: Dict[str, float]) -> float:
        """Project probable real-world consequences"""
        text = statement.raw_text.lower()
        
        # High bias density = poor outcomes if acted upon
        total_bias = sum(bias_scores.values())
        bias_penalty = min(0.8, total_bias)
        
        # Specific outcome predictions
        outcome_score = 0.5  # Neutral baseline
        
        if 'relationship' in text and any(bias in bias_scores for bias in ['safety_projection', 'abuse_normalization']):
            outcome_score = 0.2  # Poor prognosis
        
        elif 'job' in text and 'competence_halo' in bias_scores:
            outcome_score = 0.3  # Stagnation likely
        
        elif 'fine' in text and 'safety_projection' in bias_scores:
            outcome_score = 0.1  # Crisis likely
        
        # Apply bias penalty
        final_score = outcome_score * (1 - bias_penalty * 0.5)
        return max(0.0, min(1.0, final_score))

class TruthEngine:
    """Main orchestration system - The Five Mirror Array"""
    
    def __init__(self):
        self.bias_classifier = BiasClassifier()
        self.affective_mapper = AffectiveMapper()
        self.evidence_core = EvidenceCore()
        self.consequence_simulator = ConsequenceSimulator()
        
        # Initialize database for learning
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for storing analyses and feedback"""
        self.conn = sqlite3.connect('truth_engine.db')
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY,
                statement TEXT,
                truth_gradient REAL,
                evidence_score REAL,
                emotion_score REAL,
                bias_density REAL,
                pragmatic_score REAL,
                user_feedback TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def analyze(self, text: str) -> Dict:
        """Main analysis pipeline - The Five Mirror Process"""
        statement = Statement(
            raw_text=text,
            timestamp=datetime.now()
        )
        
        # Mirror 1: Evidence Analysis
        evidence_score = self.evidence_core.evaluate_evidence(statement)
        
        # Mirror 2: Emotional Coherence
        emotional_profile = self.affective_mapper.map_emotion(statement)
        emotion_coherence = emotional_profile.get('coherence', 0.5)
        
        # Mirror 3: Bias Detection
        bias_vector = self.bias_classifier.classify(statement)
        bias_density = sum(bias_vector.values()) / max(1, len(bias_vector))
        
        # Mirror 4: Consequence Prediction
        pragmatic_score = self.consequence_simulator.simulate_outcomes(statement, bias_vector)
        
        # Mirror 5: Truth Integration (The Forge)
        truth_gradient = self._calculate_truth_gradient(
            evidence_score, emotion_coherence, bias_density, pragmatic_score
        )
        
        # Generate brutal assessment
        assessment = self._generate_brutal_assessment(
            text, truth_gradient, evidence_score, emotion_coherence, 
            bias_density, pragmatic_score, bias_vector
        )
        
        # Store analysis
        self._store_analysis(statement, truth_gradient, evidence_score, 
                           emotion_coherence, bias_density, pragmatic_score)
        
        return {
            'truth_gradient': round(truth_gradient * 100, 1),
            'evidence_strength': round(evidence_score * 100, 1),
            'emotional_coherence': round(emotion_coherence * 100, 1),
            'bias_density': round(bias_density * 100, 1),
            'pragmatic_reality': round(pragmatic_score * 100, 1),
            'bias_breakdown': {k: round(v * 100, 1) for k, v in bias_vector.items() if v > 0.1},
            'assessment': assessment,
            'emotional_profile': {k: round(v * 100, 1) for k, v in emotional_profile.items()}
        }
    
    def _calculate_truth_gradient(self, evidence: float, emotion: float, 
                                 bias_density: float, pragmatic: float) -> float:
        """The Compression Reactor - Forge truth from components"""
        # Formula from specs: (ES + ECS + (1-BDI) + PRS) / 4
        truth_gradient = (evidence + emotion + (1 - bias_density) + pragmatic) / 4
        return max(0.0, min(1.0, truth_gradient))
    
    def _generate_brutal_assessment(self, text: str, truth_gradient: float,
                                   evidence: float, emotion: float, bias_density: float,
                                   pragmatic: float, bias_vector: Dict[str, float]) -> Dict[str, str]:
        """Generate unfiltered truth assessment"""
        
        # Determine primary bias
        primary_bias = max(bias_vector.items(), key=lambda x: x[1])[0] if bias_vector else None
        
        # Truth gradient interpretation
        if truth_gradient < 0.25:
            gradient_assessment = "DELUSION ZONE - Major reality distortion detected"
        elif truth_gradient < 0.5:
            gradient_assessment = "COMFORT ZONE - Significant self-deception present"
        elif truth_gradient < 0.75:
            gradient_assessment = "PARTIAL COHERENCE - Some reality anchoring"
        else:
            gradient_assessment = "REALITY ALIGNMENT - High truth coherence"
        
        # Generate specific feedback based on content
        brutal_truth = self._generate_content_specific_feedback(text, bias_vector)
        
        # Required corrections
        correction = self._generate_corrections(text, evidence, bias_density, primary_bias)
        
        return {
            'gradient_assessment': gradient_assessment,
            'brutal_truth': brutal_truth,
            'primary_bias': primary_bias.replace('_', ' ').title() if primary_bias else "None detected",
            'correction': correction,
            'reality_gap': f"{round((1 - truth_gradient) * 100, 1)}% divergence from objective truth"
        }
    
    def _generate_content_specific_feedback(self, text: str, bias_vector: Dict[str, float]) -> str:
        """Generate specific brutal feedback based on statement content"""
        text_lower = text.lower()
        
        if 'good at' in text_lower and 'job' in text_lower:
            return "You're probably mediocre and don't know it. 'Pretty good' is often code for 'adequate enough to not get fired.' Without specific metrics, you're guessing."
        
        elif 'relationship' in text_lower and any(word in text_lower for word in ['healthy', 'fine', 'good']):
            return "This is likely a convenience arrangement, not a partnership. You're both settling because change is terrifying. The 'health' you perceive is mutual enablement."
        
        elif 'not unusual' in text_lower or ('normal' in text_lower and 'i' in text_lower):
            return "You're lying to yourself. Normal people don't question their normalcy. You're unusual and afraid to own it because being different feels dangerous."
        
        elif 'fine' in text_lower and 'i' in text_lower:
            return "You're not fine. You're performing fine-ness. Actually fine people don't need to convince others of their fine-ness."
        
        elif 'work harder' in text_lower or 'try harder' in text_lower:
            return "You're probably working hard on the wrong things. More effort in a broken system just produces efficient failure."
        
        else:
            return "Your statement lacks empirical foundation. You're probably believing what you want to believe rather than what the evidence supports."
    
    def _generate_corrections(self, text: str, evidence: float, bias_density: float, primary_bias: str) -> str:
        """Generate specific action requirements"""
        text_lower = text.lower()
        
        if evidence < 0.3:
            return "Gather objective data before making claims. Test your assumptions against external feedback."
        
        elif bias_density > 0.6:
            return f"Address {primary_bias.replace('_', ' ')} pattern. Stop using feelings as evidence. Demand empirical validation."
        
        elif 'job' in text_lower:
            return "Demand specific performance data. Ask for brutal feedback from 3 colleagues. Set measurable improvement targets."
        
        elif 'relationship' in text_lower:
            return "Audit fundamental compatibility. List 3 major compromises each of you makes. Address core issues or accept mediocrity."
        
        else:
            return "Stop performing wellness narratives. Identify 3 specific areas where you're struggling. Act on one immediately."
    
    def _store_analysis(self, statement: Statement, truth_gradient: float,
                       evidence: float, emotion: float, bias_density: float, pragmatic: float):
        """Store analysis for learning and improvement"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO analyses 
            (statement, truth_gradient, evidence_score, emotion_score, bias_density, pragmatic_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (statement.raw_text, truth_gradient, evidence, emotion, bias_density, pragmatic))
        self.conn.commit()
    
    def record_feedback(self, analysis_id: int, feedback: str):
        """Record user feedback for model improvement"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE analyses SET user_feedback = ? WHERE id = ?
        ''', (feedback, analysis_id))
        self.conn.commit()
    
    def get_analysis_stats(self) -> Dict:
        """Get aggregated statistics for system improvement"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                AVG(truth_gradient) as avg_truth,
                COUNT(*) as total_analyses,
                AVG(bias_density) as avg_bias_density
            FROM analyses
        ''')
        stats = cursor.fetchone()
        return {
            'average_truth_gradient': round(stats[0] * 100, 1) if stats[0] else 0,
            'total_analyses': stats[1],
            'average_bias_density': round(stats[2] * 100, 1) if stats[2] else 0
        }

# CLI Interface for testing
def main():
    """Command line interface for Truth Engine testing"""
    engine = TruthEngine()
    
    print("=" * 60)
    print("TRUTH ENGINE v2.0 - REALITY CALIBRATION SYSTEM")
    print("=" * 60)
    print("Enter statements for brutal truth analysis.")
    print("Type 'quit' to exit, 'stats' for system statistics.")
    print()
    
    while True:
        statement = input("Enter statement: ").strip()
        
        if statement.lower() == 'quit':
            break
        elif statement.lower() == 'stats':
            stats = engine.get_analysis_stats()
            print(f"\nSystem Statistics:")
            print(f"Total Analyses: {stats['total_analyses']}")
            print(f"Average Truth Gradient: {stats['average_truth_gradient']}%")
            print(f"Average Bias Density: {stats['average_bias_density']}%")
            print()
            continue
        elif not statement:
            continue
        
        result = engine.analyze(statement)
        
        print(f"\n{'='*50}")
        print(f"TRUTH GRADIENT: {result['truth_gradient']}%")
        print(f"{'='*50}")
        print(f"Evidence Strength: {result['evidence_strength']}%")
        print(f"Emotional Coherence: {result['emotional_coherence']}%")
        print(f"Bias Density: {result['bias_density']}%")
        print(f"Pragmatic Reality: {result['pragmatic_reality']}%")
        print()
        
        if result['bias_breakdown']:
            print("DETECTED BIASES:")
            for bias, score in result['bias_breakdown'].items():
                print(f"  {bias.replace('_', ' ').title()}: {score}%")
            print()
        
        print("BRUTAL ASSESSMENT:")
        print(f"  Grade: {result['assessment']['gradient_assessment']}")
        print(f"  Reality Gap: {result['assessment']['reality_gap']}")
        print(f"  Primary Bias: {result['assessment']['primary_bias']}")
        print()
        print(f"TRUTH: {result['assessment']['brutal_truth']}")
        print()
        print(f"CORRECTION REQUIRED: {result['assessment']['correction']}")
        print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
