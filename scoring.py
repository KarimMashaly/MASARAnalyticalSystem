def score_tracks(traits):
    scores = {}

    scores["AI"] = (
        0.28 * traits["analytical"] +
        0.22 * traits["ambiguity"] +
        0.18 * traits["ai_signal"] +
        0.12 * traits["trial"] +
        0.10 * (1 - traits["structure"]) +
        0.10 * traits["frustration"]
    )

    scores["Backend"] = (
        0.28 * traits["analytical"] +
        0.22 * traits["structure"] +
        0.18 * traits["execution"] +
        0.14 * traits["backend_signal"] +
        0.10 * traits["frustration"] +
        0.08 * (1 - traits["ambiguity"])
    )

    scores["Frontend"] = (
        0.28 * traits["execution"] +
        0.22 * traits["trial"] +
        0.18 * traits["frontend_signal"] +
        0.12 * traits["ambiguity"] +
        0.10 * (1 - traits["analytical"]) +
        0.10 * (1 - traits["structure"])
    )

    return scores