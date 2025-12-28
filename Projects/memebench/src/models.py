"""
MemeBench Model Interface
Abstracts model interactions for benchmark evaluation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import random


@dataclass
class EvaluationResult:
    """Result from model evaluation of a meme question."""
    question_id: str
    model_response: str
    scores: dict[str, float]  # dimension_id -> score (1-5)
    metadata: dict = None


class ModelInterface(ABC):
    """Abstract base class for model implementations."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Model identifier."""
        pass
    
    @abstractmethod
    def evaluate(self, question: dict) -> EvaluationResult:
        """
        Evaluate a meme question.
        
        Args:
            question: Dict with id, category, description, question, expected_signals
            
        Returns:
            EvaluationResult with model's response and scores
        """
        pass


class MockModel(ModelInterface):
    """Mock model for testing the evaluation harness."""
    
    @property
    def name(self) -> str:
        return "mock"
    
    def evaluate(self, question: dict) -> EvaluationResult:
        """Returns random scores for testing purposes."""
        dimensions = [
            "cultural_reference",
            "irony_detection", 
            "temporal_context",
            "sociological_subtext",
            "format_appropriateness"
        ]
        
        scores = {dim: random.uniform(1, 5) for dim in dimensions}
        
        return EvaluationResult(
            question_id=question.get("id", "unknown"),
            model_response="[Mock response - evaluation harness test]",
            scores=scores,
            metadata={"model": self.name, "mock": True}
        )


# Model registry - add new models here
_MODELS = {
    "mock": MockModel,
}


def get_model(name: str) -> ModelInterface:
    """
    Get a model instance by name.
    
    Args:
        name: Model identifier (e.g., "mock", "gpt-4", "claude")
        
    Returns:
        ModelInterface instance
        
    Raises:
        ValueError: If model name not recognized
    """
    if name not in _MODELS:
        available = ", ".join(_MODELS.keys())
        raise ValueError(f"Unknown model '{name}'. Available: {available}")
    
    return _MODELS[name]()


def list_models() -> list[str]:
    """Return list of available model names."""
    return list(_MODELS.keys())

