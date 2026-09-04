"""
Behavioral Psychology & Cognitive Scripting Engine (Module Y1 - Python)
Synthesizes the financial psychology methodologies of Emma Edwards (Good With Money):
- Inner Villains & Sabotage Classifier (9 Archetypes)
- Cognitive ABC-DE Reconditioning Model (Ellis & Seligman)
- 4-Zone Decision Architecture (Activation, Decision, Reflection, Empowerment)
- RICA Framework (Recall, Identify, Call Out, Argue)
- 3 Ps Cognitive Distortion & Resilience Metrics (Permanence, Pervasiveness, Personalisation)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class InnerVillain(Enum):
    NONE = "none"
    CHANGE_YOUR_LIFE_CHARLIE = "change_your_life_charlie"   # Reactive impulse spending on false transformations
    MAKEOVER_MARGARET = "makeover_margaret"                 # Outsourcing identity/self-worth to material purchases
    WHATS_THE_POINT_WANDA = "whats_the_point_wanda"         # Disenfranchised fatalistic overspending
    KEEP_UP_KARA_CONNIE = "keep_up_kara_connie"             # Social media / reference group comparison bias
    HAMSTER_WHEEL_HARRIET = "hamster_wheel_harriet"         # Chasing joy exclusively through consumption
    FIX_IT_LATER_FRAN = "fix_it_later_fran"                 # Procrastinated budgeting & status-quo complacency
    FUCK_IT_FATIMA = "fuck_it_fatima"                       # Post-blowout reckless borrowing & credit reliance
    SABOTAGE_SAM = "sabotage_sam"                           # Scarcity thinking & goal abandonment when near success
    TIGHT_HOLD_TINA = "tight_hold_tina"                     # Hyper-restrictive hoarding preventing rational deployment


class DecisionZone(Enum):
    ACTIVATION = "activation"     # Day-to-day routine, weakness meets external triggers
    DECISION = "decision"         # Short intense moment where yes/no is chosen (3 Bs applied)
    REFLECTION = "reflection"     # Post-purchase evaluation, dopamine crash or satisfaction
    EMPOWERMENT = "empowerment"   # Closed-loop ownership, circuit breaker for compulsive loops


@dataclass
class ABCDEState:
    activating_event: str
    subconscious_belief: str
    emotional_consequence: str
    dispute_evidence: str
    energising_solution: str


@dataclass
class PsychologicalResilienceScore:
    permanence_score: float    # 0.0 (Isolated temporary) to 1.0 (Permanent doom)
    pervasiveness_score: float # 0.0 (Domain specific) to 1.0 (Universal catastrophe)
    personalisation_score: float # 0.0 (Balanced attribution) to 1.0 (Toxic self-blame)
    composite_mental_toughness: float


class BehavioralPsychologyScriptingEngine:
    """
    Module Y1: Behavioral Psychology & Cognitive Scripting Engine.
    Intercepts trader emotional impulses, audits cognitive biases, and enforces psychological discipline.
    """

    def __init__(self):
        self.active_villain: InnerVillain = InnerVillain.NONE
        self.current_zone: DecisionZone = DecisionZone.ACTIVATION
        self.sabotage_history: List[Dict[str, Any]] = []

    def classify_sabotage_archetype(
        self,
        trigger_context: str,
        emotional_state: str,
        is_impulsive: bool,
        is_post_blowout: bool,
        is_near_goal: bool,
        is_social_prompted: bool
    ) -> InnerVillain:
        """
        Identifies active inner villain derailment archetype.
        """
        if is_post_blowout:
            self.active_villain = InnerVillain.FUCK_IT_FATIMA
        elif is_near_goal and is_impulsive:
            self.active_villain = InnerVillain.SABOTAGE_SAM
        elif is_social_prompted:
            self.active_villain = InnerVillain.KEEP_UP_KARA_CONNIE
        elif "fatal" in trigger_context.lower() or "pointless" in trigger_context.lower():
            self.active_villain = InnerVillain.WHATS_THE_POINT_WANDA
        elif "fix_later" in trigger_context.lower() or "procrastinate" in emotional_state.lower():
            self.active_villain = InnerVillain.FIX_IT_LATER_FRAN
        elif "identity" in emotional_state.lower() or "not_enough" in emotional_state.lower():
            self.active_villain = InnerVillain.MAKEOVER_MARGARET
        elif "new_start" in trigger_context.lower() or "transformation" in trigger_context.lower():
            self.active_villain = InnerVillain.CHANGE_YOUR_LIFE_CHARLIE
        elif "bored" in emotional_state.lower() or "treat" in trigger_context.lower():
            self.active_villain = InnerVillain.HAMSTER_WHEEL_HARRIET
        elif "fear_spending" in emotional_state.lower():
            self.active_villain = InnerVillain.TIGHT_HOLD_TINA
        else:
            self.active_villain = InnerVillain.NONE

        return self.active_villain

    def execute_abcde_reframe(
        self,
        event: str,
        belief: str,
        consequence: str
    ) -> ABCDEState:
        """
        Reconstructs cognitive narrative using Ellis ABC model + Seligman Dispute/Energise factors.
        """
        # Dispute 4 factors: Factual evidence, Alternative explanation, Implications, Utility
        dispute = (
            f"Dispute: The belief '{belief}' is factually unsupported by historical win/loss ratios. "
            f"The event '{event}' is a routine variance event, not an existential threat. "
            f"Maintaining this belief promotes destructive trading behavior."
        )
        energise = (
            f"Energise: Reframe '{event}' into a systematic learning feedback point. "
            f"Follow calibrated risk protocol without emotional escalation."
        )
        return ABCDEState(
            activating_event=event,
            subconscious_belief=belief,
            emotional_consequence=consequence,
            dispute_evidence=dispute,
            energising_solution=energise
        )

    def evaluate_rica_protocol(
        self,
        long_term_lighthouse: str,
        current_gap: str,
        justification_filter: str,
        future_self_impact: str
    ) -> Dict[str, Any]:
        """
        Applies RICA Framework: Recall -> Identify -> Call out -> Argue.
        """
        approved = len(justification_filter.strip()) > 10 and "excuse" not in justification_filter.lower()
        decision = "PROCEED_INTENTIONAL" if approved else "CIRCUIT_BREAKER_ABORT"
        return {
            "recall_lighthouse": long_term_lighthouse,
            "identify_gap": current_gap,
            "call_out_bs": justification_filter,
            "argue_future_self": future_self_impact,
            "action_decision": decision,
            "zone_transition": DecisionZone.EMPOWERMENT if approved else DecisionZone.REFLECTION
        }

    def compute_3p_resilience(
        self,
        permanence_rating: float,
        pervasiveness_rating: float,
        personalisation_rating: float
    ) -> PsychologicalResilienceScore:
        """
        Evaluates Martin Seligman's 3 Ps of cognitive distortion.
        Lower distortion ratings = higher mental toughness.
        """
        p1 = max(0.0, min(1.0, permanence_rating))
        p2 = max(0.0, min(1.0, pervasiveness_rating))
        p3 = max(0.0, min(1.0, personalisation_rating))
        
        # Toughness is inverted average distortion
        avg_distortion = (p1 + p2 + p3) / 3.0
        toughness = 1.0 - avg_distortion
        
        return PsychologicalResilienceScore(
            permanence_score=p1,
            pervasiveness_score=p2,
            personalisation_score=p3,
            composite_mental_toughness=round(toughness, 4)
        )
