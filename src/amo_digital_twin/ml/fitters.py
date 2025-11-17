from __future__ import annotations

from typing import Callable, Dict, Any

import numpy as np


def fit_single_param_least_squares(
    x: np.ndarray,
    y_meas: np.ndarray,
    model_fn: Callable[[np.ndarray, Dict[str, Any]], np.ndarray],
    params: Dict[str, Any],
    key: str,
    lr: float = 1e-3,
    iters: int = 2000,
    eps: float = 1e-4,
) -> Dict[str, Any]:
    """
    Crude 1D least-squares fitter on params[key].

    Minimizes mean (y_pred - y_meas)^2 via gradient descent.
    """
    p = float(params.get(key, 0.0))

    for _ in range(iters):
        params[key] = p
        y = model_fn(x, params)

        params[key] = p + eps
        y_up = model_fn(x, params)

        # numerical derivative d/dp of loss
        grad = np.mean(2.0 * (y - y_meas) * (y_up - y) / eps)
        p -= lr * grad

    params[key] = p
    return params
