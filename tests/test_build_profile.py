from onboarding.build_profile import answers_to_profile


def test_answers_flatten_into_unique_lowercase_keywords():
    answers = {
        "retail": "Amazon, Target , amazon",
        "banks": "Chase",
        "subscriptions": "",
        "tech_social": "Meta",
    }
    profile = answers_to_profile(answers)
    assert profile == {"keywords": ["amazon", "target", "chase", "meta"]}
