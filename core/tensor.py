"""Tensor wraps numpy ndarray with some stuffs for pytorch-like autograd."""

import numpy as np
import core.ops as ops


def as_tensor(obj):
    if not isinstance(obj, Tensor):
        obj = Tensor(obj)
    return obj


class Tensor(object):

    def __init__(self,
                 values,
                 requires_grad=False,
                 dependency=None,
                 dtype=None):
        self._values = np.asarray(values, dtype)

        self.grad = None
        self.requires_grad = requires_grad
        if self.requires_grad:
            self.zero_grad()

        self.dependency = dependency
        if self.dependency is None:
            self.dependency = []

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, new_values):
        self._values = np.asarray(new_values)
        self.grad = None

    @property
    def shape(self):
        return self._values.shape

    def __repr__(self):
        return "Tensor(shape=%s, requires_grad=%s)" % (
            self.shape, self.requires_grad)

    def __gt__(self, other):
        return self.values > as_tensor(other).values

    def __lt__(self, other):
        return self.values < as_tensor(other).values

    def __ge__(self, other):
        return self.values >= as_tensor(other).values

    def __le__(self, other):
        return self.values <= as_tensor(other).values

    def __add__(self, other):
        return ops.add_(self, as_tensor(other))

    def __radd__(self, other):
        return ops.add_(as_tensor(other), self)

    def __iadd__(self, other):
        self.values = self.values + as_tensor(other).values
        return self

    def __sub__(self, other):
        return ops.sub_(self, as_tensor(other))

    def __rsub__(self, other):
        return ops.sub_(as_tensor(other), self)

    def __isub__(self, other):
        self.values = self.values - as_tensor(other).values
        return self

    def __mul__(self, other):
        return ops.mul_(self, as_tensor(other))

    def __rmul__(self, other):
        return ops.mul_(as_tensor(other), self)

    def __imul__(self, other):
        self.values = self.values * as_tensor(other).values
        return self

    def __truediv__(self, other):
        return ops.div_(self, as_tensor(other))

    def __rtruediv__(self, other):
        return ops.div_(as_tensor(other), self)

    def __itruediv__(self, other):
        self.values = self.values / as_tensor(other).values
        return self

    def __neg__(self):
        return ops.neg_(self)

    def __getitem__(self, key):
        return ops.getitem_(self, key)

    def __pow__(self, other):
        return ops.pow_(self, as_tensor(other))

    def __rpow__(self, other):
        return ops.pow_(as_tensor(other), self)

    def __ipow__(self, other):
        self.values = self.values ** as_tensor(other).values
        return self

    def __matmul__(self, other):
        return ops.dot_(self, as_tensor(other))

    def __rmatmul__(self, other):
        return ops.dot_(as_tensor(other), self)

    def __imatmul__(self, other):
        self.values = self.values @ as_tensor(other).values
        return self

    def __len__(self):
        return len(self.values)

    def sum(self, axis=None):
        return ops.sum_(self, axis=axis)

    def max(self, axis=None):
        return ops.max_(self, axis=axis)

    def min(self, axis=None):
        return ops.min_(self, axis=axis)

    def transpose(self, axes=None):
        return ops.transpose_(self, axes=axes)

    def log(self):
        return ops.log_(self)

    def reshape(self, newshape):
        return ops.reshape_(self, newshape)

    def flatten(self):
        return ops.flatten_(self)

    def clip(self, min=None, max=None):
        return ops.clip_(self, min, max)

    @property
    def T(self):
        return ops.transpose_(self, axes=None)

    def backward(self, grad=None):
        assert self.requires_grad, "Call backward() on a non-requires-grad tensor."
        grad = 1.0 if grad is None else grad
        grad = np.array(grad)

        # accumulate gradient
        self.grad += grad

        # propagate the gradient to its dependencies
        for dep in self.dependency:
            grad_for_dep = dep["grad_fn"](grad)
            dep["tensor"].backward(grad_for_dep)

    def zero_grad(self):
        self.grad = np.zeros(self.shape)
