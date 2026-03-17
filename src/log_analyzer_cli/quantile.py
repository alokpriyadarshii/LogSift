from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class P2Quantile:
    """Streaming quantile estimator using the P² algorithm.

    Good for large logs where storing all latencies is too expensive.

    Reference: Jain, R. and Chlamtac, I. (1985) The P2 algorithm for dynamic
    calculation of quantiles and histograms without storing observations.
    """

    q: float
    _init_samples: list[float] = field(default_factory=list)

    # Marker heights
    _m: list[float] | None = None
    # Marker positions
    _n: list[int] | None = None
    # Desired positions
    _np: list[float] | None = None

    def __post_init__(self) -> None:
        if not (0.0 < self.q < 1.0):
            raise ValueError("q must be between 0 and 1")

    def add(self, x: float) -> None:
        if self._m is None:
            self._init_samples.append(x)
            if len(self._init_samples) == 5:
                self._init_samples.sort()
                self._m = self._init_samples[:]
                self._n = [1, 2, 3, 4, 5]
                self._np = [
                    1.0,
                    1.0 + 2.0 * self.q,
                    1.0 + 4.0 * self.q,
                    3.0 + 2.0 * self.q,
                    5.0,
                ]
            return

        assert self._m is not None and self._n is not None and self._np is not None

        m = self._m
        n = self._n
        np_ = self._np

        # Find k
        if x < m[0]:
            m[0] = x
            k = 0
        elif x >= m[4]:
            m[4] = x
            k = 3
        else:
            k = 0
            for i in range(4):
                if m[i] <= x < m[i + 1]:
                    k = i
                    break

        # Increment positions
        for i in range(k + 1, 5):
            n[i] += 1

        # Desired position increments
        dn = [0.0, self.q / 2.0, self.q, (1.0 + self.q) / 2.0, 1.0]
        for i in range(5):
            np_[i] += dn[i]

        # Adjust heights
        for i in (1, 2, 3):
            d = np_[i] - n[i]
            if (d >= 1.0 and n[i + 1] - n[i] > 1) or (d <= -1.0 and n[i] - n[i - 1] > 1):
                di = 1 if d >= 0 else -1
                # Parabolic prediction
                m_ip1, m_i, m_im1 = m[i + 1], m[i], m[i - 1]
                n_ip1, n_i, n_im1 = n[i + 1], n[i], n[i - 1]

                num = di * (n_i - n_im1 + di) * (m_ip1 - m_i) / (n_ip1 - n_i)
                num += di * (n_ip1 - n_i - di) * (m_i - m_im1) / (n_i - n_im1)
                m_new = m_i + num / (n_ip1 - n_im1)

                # If parabolic goes out of bounds, use linear
                if not (m_im1 <= m_new <= m_ip1):
                    m_new = m_i + di * (m[i + di] - m_i) / (n[i + di] - n_i)

                m[i] = m_new
                n[i] += di

    def value(self) -> float | None:
        """Return the current quantile estimate."""
        if self._m is None:
            if not self._init_samples:
                return None
            s = sorted(self._init_samples)
            idx = int(round((len(s) - 1) * self.q))
            return s[idx]
        return self._m[2]
