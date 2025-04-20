"""
fractal_json/encoder.py
Recursive Pattern Detection and Fractal Encoding Engine
"""

import json
import numpy as np
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

class FractalEncoder:
    """
    Encodes standard JSON into fractal.json format using recursive pattern detection.
    """
    
    SYMBOLIC_MARKERS = {
        'root': '🜏',
        'seed': '∴',
        'bidirectional': '⇌',
        'compression': '⧖',
        'anchor': '☍'
    }
    
    def __init__(self, compression_threshold: float = 0.8):
        self.compression_threshold = compression_threshold
        self.pattern_cache = defaultdict(lambda: defaultdict(int))
        self.symbolic_residue = {}
        self.compression_ratio = 1.0
        
    def encode(self, data: Any, depth: int = 0) -> Dict:
        """
        Main encoding function that converts standard JSON to fractal format.
        """
        # Base case for primitives
        if isinstance(data, (str, int, float, bool)) or data is None:
            return data
            
        # Detect patterns and apply fractal encoding
        if isinstance(data, dict):
            return self._encode_dict(data, depth)
        elif isinstance(data, list):
            return self._encode_list(data, depth)
        else:
            return data
            
    def _encode_dict(self, data: Dict, depth: int) -> Dict:
        """
        Encode dictionary with fractal pattern detection.
        """
        # Analyze structure for self-similarity
        pattern_id = self._detect_pattern(data)
        fractal_node = {
            f"{self.SYMBOLIC_MARKERS['compression']}depth": depth,
            f"{self.SYMBOLIC_MARKERS['root']}pattern": pattern_id
        }
        
        # Check if we can compress via reference
        if pattern_id in self.pattern_cache:
            similar_patterns = self.pattern_cache[pattern_id]
            if self._can_compress(data, similar_patterns):
                # Create anchor reference for compression
                fractal_node[f"{self.SYMBOLIC_MARKERS['anchor']}anchor"] = self._create_anchor(pattern_id)
                fractal_node[f"{self.SYMBOLIC_MARKERS['seed']}seed"] = self._extract_seed(data)
                self.compression_ratio *= 0.85  # Update compression metric
                return fractal_node
        
        # Recursively encode children
        children = {}
        for key, value in data.items():
            encoded_key = f"{self.SYMBOLIC_MARKERS['bidirectional']}{key}"
            children[encoded_key] = self.encode(value, depth + 1)
        
        if children:
            fractal_node[f"{self.SYMBOLIC_MARKERS['bidirectional']}children"] = children
        
        # Cache pattern for future compression
        self.pattern_cache[pattern_id][json.dumps(data, sort_keys=True)] += 1
        
        return fractal_node
    
    def _encode_list(self, data: List, depth: int) -> Dict:
        """
        Encode list with fractal pattern detection.
        """
        # Check for repeating patterns in list
        pattern_groups = self._detect_list_patterns(data)
        
        if pattern_groups:
            # List has repeating patterns - encode as fractal
            return {
                f"{self.SYMBOLIC_MARKERS['compression']}depth": depth,
                f"{self.SYMBOLIC_MARKERS['root']}pattern": "list_fractal",
                f"{self.SYMBOLIC_MARKERS['seed']}seed": self._extract_list_seed(pattern_groups),
                f"{self.SYMBOLIC_MARKERS['bidirectional']}expansions": [
                    self.encode(item, depth + 1) for item in data
                ]
            }
        else:
            # Encode normally
            return [self.encode(item, depth + 1) for item in data]
    
    def _detect_pattern(self, data: Dict) -> str:
        """
        Detect structural patterns in dictionaries using recursive hashing.
        """
        # Create structural signature
        structure = {k: type(v).__name__ for k, v in data.items()}
        structure_hash = hash(frozenset(structure.items()))
        
        # Check for nested self-similarity
        similarity_score = self._calculate_self_similarity(data)
        
        if similarity_score > self.compression_threshold:
            return f"fractal_{structure_hash}"
        else:
            return f"standard_{structure_hash}"
    
    def _calculate_self_similarity(self, data: Any, parent_structure: Optional[Dict] = None) -> float:
        """
        Calculate self-similarity score recursively.
        """
        if not isinstance(data, dict):
            return 0.0
        
        current_structure = {k: type(v).__name__ for k, v in data.items()}
        
        if parent_structure is None:
            # First call - check children
            child_scores = []
            for value in data.values():
                if isinstance(value, dict):
                    child_scores.append(self._calculate_self_similarity(value, current_structure))
            
            if child_scores:
                return np.mean(child_scores)
            else:
                return 0.0
        else:
            # Calculate similarity to parent
            common_keys = set(current_structure.keys()) & set(parent_structure.keys())
            if not common_keys:
                return 0.0
            
            matching_types = sum(1 for k in common_keys if current_structure[k] == parent_structure[k])
            return matching_types / len(common_keys)
    
    def _detect_list_patterns(self, data: List) -> List[List[Any]]:
        """
        Detect repeating patterns in lists.
        """
        if len(data) < 2:
            return []
        
        # Find repeating subsequences using suffix arrays
        patterns = []
        for pattern_length in range(1, len(data) // 2 + 1):
            for i in range(len(data) - pattern_length + 1):
                pattern = data[i:i + pattern_length]
                # Check if pattern repeats
                occurrences = 0
                for j in range(i, len(data) - pattern_length + 1, pattern_length):
                    if data[j:j + pattern_length] == pattern:
                        occurrences += 1
                
                if occurrences >= 2:
                    patterns.append((pattern, occurrences))
        
        # Sort by coverage and return best patterns
        if patterns:
            patterns.sort(key=lambda x: len(x[0]) * x[1], reverse=True)
            return [p[0] for p in patterns[:3]]  # Return top 3 patterns
        
        return []
    
    def _can_compress(self, data: Dict, similar_patterns: Dict) -> bool:
        """
        Determine if data can be compressed using existing patterns.
        """
        data_str = json.dumps(data, sort_keys=True)
        # Check if pattern appears frequently enough
        return similar_patterns.get(data_str, 0) >= 2
    
    def _create_anchor(self, pattern_id: str) -> str:
        """
        Create anchor reference for pattern compression.
        """
        return f"#/patterns/{pattern_id}"
    
    def _extract_seed(self, data: Dict) -> Dict:
        """
        Extract minimal seed pattern from data.
        """
        # Identify core structure
        seed = {}
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                seed[key] = value
            else:
                # Replace complex structures with placeholders
                seed[key] = f"{self.SYMBOLIC_MARKERS['bidirectional']}expand"
        
        return seed
    
    def _extract_list_seed(self, pattern_groups: List[List[Any]]) -> Dict:
        """
        Extract seed pattern from repeating list elements.
        """
        return {
            "pattern": pattern_groups[0],
            "repetitions": len(pattern_groups)
        }
    
    def get_compression_stats(self) -> Dict:
        """
        Return compression statistics.
        """
        return {
            "compression_ratio": self.compression_ratio,
            "pattern_count": len(self.pattern_cache),
            "symbolic_residue": self.symbolic_residue
        }
