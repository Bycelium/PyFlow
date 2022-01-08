# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for badges colors."""

from colorsys import hsv_to_rgb


def interpolate(weight, x, y):
    """Linear interpolation between x and y, given a weight."""
    return x * weight + (1 - weight) * y


def score_to_rgb_color(score, score_min, score_max):
    """Convert a score to a color."""
    normalized_score = max(0, (score - score_min) / (score_max - score_min))
    hsv_color = (interpolate(normalized_score, 0.33, 0), 1, 1)
    rgb_color = hsv_to_rgb(*hsv_color)
    rgb_color = tuple(int(255 * value) for value in rgb_color)
    return f"rgb{rgb_color}"
