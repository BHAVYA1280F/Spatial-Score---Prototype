"""Compatibility layer for environments with Windows Application Control or missing Numba DLLs.

Bypasses the 'DLL load failed while importing _dynfunc: An Application Control policy has blocked this file'
by providing a pure-NumPy JIT, ufunc, and stencil shim for Librosa.
"""
import sys
import types
import numpy as np


def ensure_audio_compat():
    """Ensure librosa can import and run even when numba C-extensions are blocked."""
    if "numba" in sys.modules and getattr(sys.modules["numba"], "_is_compat_shim", False):
        return

    try:
        import numba
        from numba import _dynfunc  # Test if C-extension is allowed by Application Control
        return  # Native Numba is working fine
    except Exception:
        pass

    m = types.ModuleType("numba")
    m._is_compat_shim = True

    def _jit(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return lambda fn: fn

    def _guvectorize(*gargs, **gkwargs):
        def dec(fn):
            name = getattr(fn, "__name__", "")
            if name == "__beat_track_dp":
                def wrapper(localscore, frames_per_beat, tightness, *extra):
                    if extra:
                        backlink, cumscore = extra[0], extra[1]
                    else:
                        t = len(localscore)
                        backlink = np.empty(t, dtype=np.int32)
                        cumscore = np.empty(t, dtype=localscore.dtype)
                    fn(localscore, frames_per_beat, tightness, backlink, cumscore)
                    return backlink, cumscore
                return wrapper
            elif name == "__last_beat_selector":
                def wrapper(cumscore, mask, threshold, *extra):
                    n = len(cumscore) - 1
                    res = n
                    while n >= 0:
                        if not mask[n] and cumscore[n] >= threshold:
                            res = n
                            break
                        n -= 1
                    if extra:
                        out = extra[0]
                        if out.ndim == 0:
                            out[...] = res
                        else:
                            out[0] = res
                        return out
                    return res
                return wrapper
            elif name == "_pi_wrapper":
                def wrapper(x, y):
                    out = np.zeros_like(x, dtype=float)
                    if x.shape[-1] >= 3:
                        x_prev = x[..., :-2]
                        x_curr = x[..., 1:-1]
                        x_next = x[..., 2:]
                        a = x_next + x_prev - 2 * x_curr
                        b = (x_next - x_prev) / 2.0
                        valid = (np.abs(b) < np.abs(a)) & (a != 0)
                        res = np.zeros_like(a)
                        np.divide(-b, a, out=res, where=valid)
                        out[..., 1:-1] = res
                    y[:] = out
                return wrapper
            elif name == "_zc_wrapper":
                def wrapper(x, threshold, zero_pos, y):
                    out = np.zeros_like(x, dtype=bool)
                    if x.shape[-1] >= 2:
                        x0 = x[..., 1:]
                        x1 = x[..., :-1]
                        if threshold > 0:
                            x0 = np.where(np.abs(x0) <= threshold, 0, x0)
                            x1 = np.where(np.abs(x1) <= threshold, 0, x1)
                        if zero_pos:
                            out[..., 1:] = np.signbit(x0) != np.signbit(x1)
                        else:
                            out[..., 1:] = np.sign(x0) != np.sign(x1)
                    y[:] = out
                return wrapper
            return fn
        return dec

    def _vectorize(*args, **kwargs):
        def dec(fn):
            def wrapper(x, out=None):
                x = np.asarray(x)
                res = fn(x)
                if out is not None:
                    out[...] = res
                    return out
                return res
            return wrapper
        if len(args) == 1 and callable(args[0]):
            return dec(args[0])
        return dec

    def _stencil(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return lambda fn: fn

    m.jit = _jit
    m.njit = _jit
    m.vectorize = _vectorize
    m.guvectorize = _guvectorize
    m.stencil = _stencil
    m.prange = range
    sys.modules["numba"] = m
