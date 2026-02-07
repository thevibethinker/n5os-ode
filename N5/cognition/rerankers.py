"""
Reranker interface and implementations for N5 Memory Client.

Provides a unified interface for reranking search results using different
reranking backends (FlashRank, CrossEncoder).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

LOG = logging.getLogger("n5_rerankers")


class Reranker(ABC):
    """Abstract base class for rerankers."""

    @abstractmethod
    def rank(self, query: str, candidates: List[Dict[str, Any]]) -> None:
        """
        Rerank candidates based on query relevance.

        Args:
            query: Search query string
            candidates: List of candidate results with 'content' field

        Returns:
            None - modifies candidates in place
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if reranker is available and initialized."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return name of this reranker."""
        pass


class FlashRankReranker(Reranker):
    """
    FlashRank-based reranker for fast, lightweight reranking.

    FlashRank uses quantized models for efficient reranking with minimal
    performance overhead. Ideal for production use cases.
    """

    def __init__(self, model_name: str = "ms-marco-MiniLM-L-12-v2"):
        """
        Initialize FlashRank reranker.

        Args:
            model_name: Model to use for reranking. Options:
                - "ms-marco-MiniLM-L-12-v2" (default, fast)
                - "ms-marco-MultiBERT-L-12" (more accurate, slower)
                - "rank-T5-flan" (highest accuracy, slowest)
        """
        self._model_name = model_name
        self._ranker = None
        self._init_ranker()

    def _init_ranker(self):
        """Initialize FlashRank ranker."""
        try:
            from flashrank import Ranker, RerankRequest
            self._Ranker = Ranker
            self._RerankRequest = RerankRequest
            self._ranker = Ranker(model_name=self._model_name)
            LOG.info(f"FlashRank reranker initialized: {self._model_name}")
        except ImportError:
            LOG.warning("flashrank package not installed")
            self._ranker = None
        except Exception as e:
            LOG.warning(f"Could not initialize FlashRank: {e}")
            self._ranker = None

    def rank(self, query: str, candidates: List[Dict[str, Any]]) -> None:
        """
        Rerank candidates using FlashRank.

        Args:
            query: Search query string
            candidates: List of candidate results with 'content' field

        Returns:
            None - modifies candidates in place
        """
        if not self.is_available() or not candidates:
            return

        try:
            # Prepare passages for FlashRank
            passages = []
            for idx, candidate in enumerate(candidates):
                content = candidate.get('content', '')
                if content.strip():
                    passages.append({
                        "id": idx,
                        "text": content[:2000],  # Truncate for efficiency
                        "meta": idx  # Track original index
                    })

            if not passages:
                return

            # Rerank
            request = self._RerankRequest(query=query, passages=passages)
            reranked = self._ranker.rerank(request)

            # Create mapping of result index to score
            score_map = {
                r['meta']: float(r['score'])
                for r in reranked[:len(candidates)]
            }

            # Update candidates with rerank scores
            for idx, candidate in enumerate(candidates):
                if idx in score_map:
                    candidate['rerank_score'] = score_map[idx]
                    candidate['score'] = score_map[idx]
                else:
                    candidate['rerank_score'] = 0.0
                    candidate['score'] = 0.0

            # Sort by rerank score (modifies in place)
            candidates.sort(key=lambda x: x.get('score', 0.0), reverse=True)

            LOG.debug(f"Reranked {len(candidates)} candidates with FlashRank")

        except Exception as e:
            LOG.warning(f"FlashRank reranking failed: {e}")

    def is_available(self) -> bool:
        """Check if FlashRank reranker is available."""
        return self._ranker is not None

    @property
    def name(self) -> str:
        """Return the name of this reranker."""
        return f"FlashRank({self._model_name})"


class CrossEncoderReranker(Reranker):
    """
    Cross-encoder based reranker from sentence-transformers.

    Provides high-quality reranking using cross-encoder models.
    Heavier than FlashRank but well-established and battle-tested.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"):
        """
        Initialize CrossEncoder reranker.

        Args:
            model_name: Model to use for reranking. Options:
                - "cross-encoder/ms-marco-MiniLM-L-12-v2" (default)
                - "cross-encoder/ms-marco-TinyBERT-L-2-v2" (faster, lower quality)
                - "cross-encoder/ms-marco-electra-base" (higher quality, slower)
        """
        self._model_name = model_name
        self._cross_encoder = None
        self._init_cross_encoder()

    def _init_cross_encoder(self):
        """Initialize cross-encoder model."""
        try:
            from sentence_transformers import CrossEncoder
            self._cross_encoder = CrossEncoder(self._model_name)
            LOG.info(f"CrossEncoder reranker initialized: {self._model_name}")
        except ImportError:
            LOG.warning("sentence-transformers package not installed")
            self._cross_encoder = None
        except Exception as e:
            LOG.warning(f"Could not initialize CrossEncoder: {e}")
            self._cross_encoder = None

    def rank(self, query: str, candidates: List[Dict[str, Any]]) -> None:
        """
        Rerank candidates using cross-encoder.

        Args:
            query: Search query string
            candidates: List of candidate results with 'content' field

        Returns:
            None - modifies candidates in place
        """
        if not self.is_available() or not candidates:
            return

        try:
            # Prepare (query, document) pairs
            pairs = [(query, candidate.get('content', '')[:1000]) for candidate in candidates]

            # Predict scores
            scores = self._cross_encoder.predict(pairs)

            # Update candidates with scores
            for i, score in enumerate(scores):
                candidates[i]['rerank_score'] = float(score)
                candidates[i]['score'] = float(score)

            # Sort by rerank score (modifies in place)
            candidates.sort(key=lambda x: x.get('score', 0.0), reverse=True)

            LOG.debug(f"Reranked {len(candidates)} candidates with CrossEncoder")

        except Exception as e:
            LOG.warning(f"CrossEncoder reranking failed: {e}")

    def is_available(self) -> bool:
        """Check if CrossEncoder reranker is available."""
        return self._cross_encoder is not None

    @property
    def name(self) -> str:
        """Return the name of this reranker."""
        return f"CrossEncoder({self._model_name})"


def create_reranker(reranker_type: str = "flashrank", **kwargs) -> Optional[Reranker]:
    """
    Factory function to create a reranker by type.

    Args:
        reranker_type: Type of reranker to create ("flashrank" or "cross-encoder")
        **kwargs: Additional arguments passed to reranker constructor

    Returns:
        Reranker instance or None if type is unrecognized
    """
    reranker_type = reranker_type.lower().replace("-", "").replace("_", "")

    if reranker_type == "flashrank":
        return FlashRankReranker(**kwargs)
    elif reranker_type in ("crossencoder", "crossencoder", "cross"):
        return CrossEncoderReranker(**kwargs)
    else:
        LOG.warning(f"Unknown reranker type: {reranker_type}")
        return None
