# Module Y5 (Julia): Behavioral Psychology & Cognitive Scripting Engine
# Scientific evaluation of cognitive distortion metrics (3 Ps) and Seligman toughness

module BehavioralPsychologyEngine

export evaluate_3p_resilience, classify_villain

function classify_villain(trigger::String, emotional_state::String, is_blowout::Bool, is_near_goal::Bool)
    if is_blowout
        return "FUCK_IT_FATIMA"
    elseif is_near_goal
        return "SABOTAGE_SAM"
    elseif occursin("fatal", lowercase(trigger))
        return "WHATS_THE_POINT_WANDA"
    elseif occursin("later", lowercase(trigger))
        return "FIX_IT_LATER_FRAN"
    elseif occursin("identity", lowercase(emotional_state))
        return "MAKEOVER_MARGARET"
    elseif occursin("transform", lowercase(trigger))
        return "CHANGE_YOUR_LIFE_CHARLIE"
    else
        return "NONE"
    end
end

function evaluate_3p_resilience(permanence::Float64, pervasiveness::Float64, personalisation::Float64)
    p1 = clamp(permanence, 0.0, 1.0)
    p2 = clamp(pervasiveness, 0.0, 1.0)
    p3 = clamp(personalisation, 0.0, 1.0)
    avg_distortion = (p1 + p2 + p3) / 3.0
    toughness = 1.0 - avg_distortion
    return (
        permanence = p1,
        pervasiveness = p2,
        personalisation = p3,
        composite_mental_toughness = round(toughness, digits=4)
    )
end

end # module
