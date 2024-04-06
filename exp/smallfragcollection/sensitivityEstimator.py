import numpy as np
import dataclasses
import typing
from utilref import *

np.seterr(all="raise")

eps = 1e-10


@dataclasses.dataclass
class System:
    value: float
    sensitivity: float
    shake: typing.Callable

    def ctrl(self, ctrlval: float):
        self.value += ctrlval * (self.sensitivity + self.shake())


mu = 0
sigma = 0.1
system = System(0, 0.5, lambda: np.random.normal(mu, sigma))
estimator = BayesEstimator(
    np.linspace(0, 1, 10),
    lambda x, s: 1
    / np.sqrt(2 * np.pi)
    * SafeExp(-((s - x) ** 2) / (2 * (2 * sigma) ** 2)),
)

possibility = [estimator.getPossibility()]
for i in range(10 - 1):
    ctrlval = (1 if np.random.rand() > 0.5 else -1) * (
        np.abs(np.random.uniform(-1, 1)) + eps
    )
    prev = system.value
    system.ctrl(ctrlval)
    after = system.value
    measuredSensitivity = (after - prev) / ctrlval
    estimator.update(measuredValue=[measuredSensitivity])
    possibility.append(estimator.getPossibility())
data = np.array(possibility)

import matplotlib.pyplot as plt

# Assuming your 2D array is called 'data'

distributionPlot = plt.subplot2grid([1, 2], [0, 0], rowspan=1, colspan=1)
contour = distributionPlot.contourf(estimator.xspace, np.arange(data.shape[0]), data)
plt.colorbar(contour)

E_sens = np.sum(estimator.xspace.reshape((1, -1)) * data, axis=1)
expectedPlot = plt.subplot2grid([1, 2], [0, 1], rowspan=1, colspan=1)
expectedPlot.plot(E_sens)
expectedPlot.set_ylim(0, 1)
plt.show()
