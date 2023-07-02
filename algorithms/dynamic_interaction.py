from pprint import pprint

# Example Weights for Interactions
weights = {
    "buy": 1.0,
    "download": 0.86,
    "like": 0.7,
    "listen": 0.6,
}


# Update a rating based on an interaction
def handle_interactive_dynamics(
    interaction_weight: float,
    curr_rating: float,
    scalar: float,
    shift=1.5,
) -> float:
    max_pos = scalar * interaction_weight
    delta = max_pos * interaction_weight

    get_new_rating = (
        lambda curr_rating, delta, shift: curr_rating + delta
        if curr_rating > 0
        else (curr_rating + delta + shift)
    )

    new_rating = max(0.0, min(get_new_rating(curr_rating, delta, shift), 5.0))

    return new_rating


# example scalar, tunable
scalar = 3.5
ratings = [float(i) for i in range(0, 5)]

for rating in ratings:
    for key, value in weights.items():
        print(f"running {key} on curr_rating {rating}")
        interaction = value
        new_rating = round(
            handle_interactive_dynamics(
                interaction,
                rating,
                scalar,
            ),
            2,
        )
        print(f"outputted new rating: {new_rating}")
