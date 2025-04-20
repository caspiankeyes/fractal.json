"""
fractal_json/decoder.py
Recursive Pattern Reconstruction and Fractal Decoding Engine
"""

import json
from typing import Any, Dict, List, Optional, Union

class FractalDecoder:
    """
    Decodes fractal.json format back to standard JSON while preserving recursive patterns.
    """
    
    SYMBOLIC_MARKERS = {
        '🜏': 'root',
        '∴': 'seed',
        '⇌': 'bidirectional',
        '⧖': 'compression',
        '☍': 'anchor'
    }
    
    def __init__(self):
        self.pattern_registry = {}
        self.expansion_cache = {}
        self.recursion_depth = 0
        self.max_recursion = 100
        
    def decode(self, fractal_data: Union[Dict, List, Any]) -> Any:
        """
        Main decoding function that converts fractal format to standard JSON.
        """
        # Handle primitive types
        if not isinstance(fractal_data, (dict, list)):
            return fractal_data
            
        # Extract metadata if present
        if isinstance(fractal_data, dict) and "$fractal" in fractal_data:
            self._process_metadata(fractal_data["$fractal"])
            fractal_data = fractal_data.get("content", {})
        
        # Recurse through structure
        return self._decode_recursive(fractal_data)
    
    def _decode_recursive(self, data: Any) -> Any:
        """
        Recursively decode fractal structures.
        """
        # Check recursion limit
        self.recursion_depth += 1
        if self.recursion_depth > self.max_recursion:
            raise RecursionError("Maximum recursion depth exceeded in fractal decoding")
        
        try:
            if isinstance(data, dict):
                return self._decode_dict(data)
            elif isinstance(data, list):
                return self._decode_list(data)
            else:
                return data
        finally:
            self.recursion_depth -= 1
    
    def _decode_dict(self, data: Dict) -> Union[Dict, Any]:
        """
        Decode fractal dictionary structure.
        """
        # Check if this is a fractal node
        if self._is_fractal_node(data):
            # Check for anchor reference
            anchor_key = f"{self._get_marker('anchor')}anchor"
            if anchor_key in data:
                return self._resolve_anchor(data[anchor_key], data)
            
            # Extract pattern and seed
            pattern_key = f"{self._get_marker('root')}pattern"
            seed_key = f"{self._get_marker('seed')}seed"
            
            pattern_id = data.get(pattern_key)
            seed = data.get(seed_key)
            
            if pattern_id and seed:
                # Expand from seed
                expanded = self._expand_from_seed(pattern_id, seed, data)
                if expanded is not None:
                    return expanded
        
        # Decode children recursively
        decoded = {}
        for key, value in data.items():
            # Remove symbolic markers from keys
            clean_key = self._clean_key(key)
            
            # Skip metadata fields
            if not self._is_metadata_key(key):
                decoded[clean_key] = self._decode_recursive(value)
        
        return decoded
    
    def _decode_list(self, data: List) -> List:
        """
        Decode list structure.
        """
        # If list contains fractal patterns, decode them
        decoded = []
        for item in data:
            decoded.append(self._decode_recursive(item))
        return decoded
    
    def _is_fractal_node(self, data: Dict) -> bool:
        """
        Check if dictionary represents a fractal node.
        """
        if not isinstance(data, dict):
            return False
            
        # Check for fractal markers
        has_depth = any(key.startswith(self._get_marker('compression')) for key in data.keys())
        has_pattern = any(key.startswith(self._get_marker('root')) for key in data.keys())
        
        return has_depth and has_pattern
    
    def _get_marker(self, marker_name: str) -> str:
        """
        Get symbolic marker by name.
        """
        for symbol, name in self.SYMBOLIC_MARKERS.items():
            if name == marker_name:
                return symbol
        return ''
    
    def _clean_key(self, key: str) -> str:
        """
        Remove symbolic markers from keys.
        """
        for marker in self.SYMBOLIC_MARKERS.keys():
            if key.startswith(marker):
                return key[len(marker):]
        return key
    
    def _is_metadata_key(self, key: str) -> bool:
        """
        Check if key represents metadata.
        """
        metadata_prefixes = ['depth', 'pattern', 'anchor']
        clean_key = self._clean_key(key)
        return clean_key in metadata_prefixes
    
    def _resolve_anchor(self, anchor: str, context: Dict) -> Any:
        """
        Resolve anchor reference to actual data.
        """
        if anchor in self.expansion_cache:
            return self.expansion_cache[anchor]
        
        # Extract pattern from anchor
        if anchor.startswith("#/patterns/"):
            pattern_id = anchor.split("/")[-1]
            if pattern_id in self.pattern_registry:
                # Expand pattern with context
                expanded = self._expand_pattern(self.pattern_registry[pattern_id], context)
                self.expansion_cache[anchor] = expanded
                return expanded
        
        # Cannot resolve - return as is
        return context
    
    def _expand_from_seed(self, pattern_id: str, seed: Any, context: Dict) -> Optional[Any]:
        """
        Expand full structure from seed pattern.
        """
        if not isinstance(seed, dict):
            return None
            
        expanded = {}
        for key, value in seed.items():
            if isinstance(value, str) and value.endswith("expand"):
                # Replace with full expansion if available in context
                children_key = f"{self._get_marker('bidirectional')}children"
                if children_key in context:
                    children = context[children_key]
                    expanded_key = f"{self._get_marker('bidirectional')}{key}"
                    if expanded_key in children:
                        expanded[key] = self._decode_recursive(children[expanded_key])
                    else:
                        expanded[key] = None
            else:
                expanded[key] = value
        
        return expanded
    
    def _expand_pattern(self, pattern: Dict, context: Dict) -> Any:
        """
        Expand pattern with context-specific values.
        """
        # Simple pattern expansion for now
        # This could be made more sophisticated based on pattern type
        return pattern
    
    def _process_metadata(self, metadata: Dict) -> None:
        """
        Process fractal metadata for decoding context.
        """
        if "interpretability_map" in metadata:
            # Store interpretability patterns for reference
            self.pattern_registry.update(metadata["interpretability_map"])
    
    def get_decoding_stats(self) -> Dict:
        """
        Return decoding statistics.
        """
        return {
            "patterns_resolved": len(self.expansion_cache),
            "max_recursion_depth": self.recursion_depth,
            "pattern_registry_size": len(self.pattern_registry)
        }
