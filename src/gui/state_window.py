from abc import ABC, abstractmethod

class StateWindow(ABC):
    """
    Abstract base class for window states.
    Each state must implement show() and clear().
    """
    def __init__(self, context):
        self.context = context  # Reference to StartWindow
    @abstractmethod
    def show(self):
        pass
    @abstractmethod
    def clear(self):
        pass
