from abc import ABC, abstractmethod

from ..ir import ModelIR


class BackendAdapter(ABC):
    """Adapter interface for backends that render/execute a normalized model IR."""

    @abstractmethod
    def render_model(self, model_ir: ModelIR) -> str:
        raise NotImplementedError()
