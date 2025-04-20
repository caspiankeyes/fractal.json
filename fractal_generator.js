/**
 * fractal_generator.js
 * Generates fractal.json structures with visualization
 */

class FractalGenerator {
    constructor(config = {}) {
        this.maxDepth = config.maxDepth || 5;
        this.compressionThreshold = config.compressionThreshold || 0.8;
        this.symbolicMarkers = {
            root: '🜏',
            seed: '∴',
            bidirectional: '⇌',
            compression: '⧖',
            anchor: '☍'
        };
        this.patternRegistry = new Map();
        this.compressionStats = {
            ratio: 1.0,
            residueNodes: 0,
            anchorReferences: 0
        };
    }

    /**
     * Generate fractal structure from input data
     */
    generate(data, pattern = 'auto') {
        const rootPattern = pattern === 'auto' ? this.detectPattern(data) : pattern;
        
        const fractalStructure = {
            "$fractal": {
                version: "1.0.0",
                root_pattern: rootPattern,
                compression: {
                    ratio: 1.0,
                    symbolic_residue: {},
                    attention_efficiency: 1.0
                },
                interpretability_map: {
                    scale_invariance: "high",
                    pattern_visibility: "recursive"
                }
            },
            content: this._generateRecursive(data, 0, rootPattern)
        };

        // Update compression statistics
        fractalStructure.$fractal.compression.ratio = this.compressionStats.ratio;
        fractalStructure.$fractal.compression.attention_efficiency = 
            this.calculateAttentionEfficiency(data, fractalStructure.content);

        return fractalStructure;
    }

    /**
     * Detect self-similar patterns in data
     */
    detectPattern(data) {
        if (Array.isArray(data)) {
            return this._detectListPattern(data);
        } else if (typeof data === 'object' && data !== null) {
            return this._detectObjectPattern(data);
        }
        return 'primitive';
    }

    _detectObjectPattern(obj) {
        const structure = Object.keys(obj).reduce((acc, key) => {
            acc[key] = typeof obj[key];
            return acc;
        }, {});
        
        const structureHash = JSON.stringify(structure);
        const patternId = `pattern_${this._hashCode(structureHash)}`;
        
        this.patternRegistry.set(patternId, {
            structure,
            instances: [obj]
        });
        
        return patternId;
    }

    _detectListPattern(arr) {
        // Find repeating sequences
        const patterns = new Map();
        
        for (let len = 1; len <= Math.floor(arr.length / 2); len++) {
            for (let i = 0; i <= arr.length - len; i++) {
                const pattern = JSON.stringify(arr.slice(i, i + len));
                const count = patterns.get(pattern) || 0;
                patterns.set(pattern, count + 1);
            }
        }
        
        // Find most frequent pattern
        let maxCount = 0;
        let bestPattern = null;
        
        patterns.forEach((count, pattern) => {
            if (count > maxCount) {
                maxCount = count;
                bestPattern = pattern;
            }
        });
        
        return bestPattern ? `list_pattern_${this._hashCode(bestPattern)}` : 'list';
    }

    /**
     * Recursively generate fractal structure
     */
    _generateRecursive(data, depth, patternId) {
        if (depth >= this.maxDepth || this._isPrimitive(data)) {
            return data;
        }

        const node = {
            [`${this.symbolicMarkers.compression}depth`]: depth,
            [`${this.symbolicMarkers.root}pattern`]: patternId
        };

        // Check for pattern reuse
        const existingPattern = this._findExistingPattern(data);
        if (existingPattern && depth > 0) {
            node[`${this.symbolicMarkers.anchor}anchor`] = `#/patterns/${existingPattern}`;
            node[`${this.symbolicMarkers.seed}seed`] = this._extractSeed(data);
            this.compressionStats.anchorReferences++;
            this.compressionStats.ratio *= 0.85;
            return node;
        }

        // Handle objects
        if (typeof data === 'object' && data !== null && !Array.isArray(data)) {
            const children = {};
            
            for (const [key, value] of Object.entries(data)) {
                const childPattern = this.detectPattern(value);
                const markedKey = `${this.symbolicMarkers.bidirectional}${key}`;
                children[markedKey] = this._generateRecursive(value, depth + 1, childPattern);
            }
            
            if (Object.keys(children).length > 0) {
                node[`${this.symbolicMarkers.bidirectional}children`] = children;
            }
            
            // Extract seed for compression
            node[`${this.symbolicMarkers.seed}seed`] = this._extractSeed(data);
            this.compressionStats.residueNodes++;
        }
        
        // Handle arrays
        else if (Array.isArray(data)) {
            const listPattern = this._detectListRepeats(data);
            if (listPattern) {
                node[`${this.symbolicMarkers.seed}seed`] = {
                    pattern: listPattern.pattern,
                    repetitions: listPattern.count
                };
                node[`${this.symbolicMarkers.bidirectional}expansions`] = 
                    data.map(item => this._generateRecursive(item, depth + 1, 'list_item'));
            } else {
                return data.map(item => 
                    this._generateRecursive(item, depth + 1, 'list_item'));
            }
        }

        return node;
    }

    /**
     * Extract seed pattern for compression
     */
    _extractSeed(data) {
        if (typeof data !== 'object' || data === null) {
            return data;
        }

        const seed = {};
        for (const [key, value] of Object.entries(data)) {
            if (this._isPrimitive(value)) {
                seed[key] = value;
            } else {
                seed[key] = `${this.symbolicMarkers.bidirectional}expand`;
            }
        }
        return seed;
    }

    /**
     * Find existing pattern for reuse
     */
    _findExistingPattern(data) {
        const dataStr = JSON.stringify(data);
        for (const [patternId, pattern] of this.patternRegistry.entries()) {
            if (pattern.instances.some(instance => 
                JSON.stringify(instance) === dataStr)) {
                return patternId;
            }
        }
        return null;
    }

    /**
     * Detect repeating sequences in arrays
     */
    _detectListRepeats(arr) {
        for (let len = 1; len <= Math.floor(arr.length / 2); len++) {
            const pattern = arr.slice(0, len);
            let count = 0;
            
            for (let i = 0; i < arr.length; i += len) {
                const slice = arr.slice(i, i + len);
                if (JSON.stringify(slice) === JSON.stringify(pattern)) {
                    count++;
                } else {
                    break;
                }
            }
            
            if (count > 1 && count * len === arr.length) {
                return { pattern, count };
            }
        }
        return null;
    }

    /**
     * Calculate attention efficiency gain
     */
    calculateAttentionEfficiency(original, fractal) {
        const originalComplexity = this._calculateComplexity(original);
        const fractalComplexity = this._calculateComplexity(fractal);
        
        return originalComplexity / fractalComplexity;
    }

    _calculateComplexity(data, depth = 0) {
        if (this._isPrimitive(data)) {
            return 1;
        }
        
        if (Array.isArray(data)) {
            return data.reduce((sum, item) => 
                sum + this._calculateComplexity(item, depth + 1), 0);
        }
        
        if (typeof data === 'object' && data !== null) {
            let complexity = 0;
            
            // Check for anchor reference
            if (data[`${this.symbolicMarkers.anchor}anchor`]) {
                return 1; // Anchor reference has constant complexity
            }
            
            for (const value of Object.values(data)) {
                complexity += this._calculateComplexity(value, depth + 1);
            }
            
            return complexity;
        }
        
        return 1;
    }

    _isPrimitive(value) {
        return value === null || 
               typeof value === 'string' || 
               typeof value === 'number' || 
               typeof value === 'boolean';
    }

    _hashCode(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return Math.abs(hash).toString(16);
    }

    /**
     * Visualize fractal structure as SVG
     */
    visualize(fractalData, config = {}) {
        const width = config.width || 800;
        const height = config.height || 600;
        const nodeRadius = config.nodeRadius || 20;
        
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("width", width);
        svg.setAttribute("height", height);
        svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
        
        // Recursive visualization
        this._visualizeNode(svg, fractalData.content, width / 2, 50, width / 4, nodeRadius);
        
        return svg;
    }

    _visualizeNode(svg, node, x, y, xOffset, radius) {
        if (!node || typeof node !== 'object') return;
        
        // Create node circle
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", x);
        circle.setAttribute("cy", y);
        circle.setAttribute("r", radius);
        
        // Color based on node type
        if (node[`${this.symbolicMarkers.anchor}anchor`]) {
            circle.setAttribute("fill", "#ff7f7f"); // Red for anchors
        } else if (node[`${this.symbolicMarkers.seed}seed`]) {
            circle.setAttribute("fill", "#7f7fff"); // Blue for seeds
        } else {
            circle.setAttribute("fill", "#7fff7f"); // Green for regular nodes
        }
        
        circle.setAttribute("stroke", "#333");
        circle.setAttribute("stroke-width", "2");
        svg.appendChild(circle);
        
        // Add pattern label
        if (node[`${this.symbolicMarkers.root}pattern`]) {
            const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
            text.setAttribute("x", x);
            text.setAttribute("y", y);
            text.setAttribute("text-anchor", "middle");
            text.setAttribute("dy", "0.3em");
            text.setAttribute("font-size", "10px");
            text.textContent = node[`${this.symbolicMarkers.root}pattern`].substring(0, 8);
            svg.appendChild(text);
        }
        
        // Visualize children
        const children = node[`${this.symbolicMarkers.bidirectional}children`];
        if (children) {
            const childKeys = Object.keys(children);
            childKeys.forEach((key, index) => {
                const childX = x + (index - (childKeys.length - 1) / 2) * xOffset;
                const childY = y + 100;
                
                // Draw connection line
                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", x);
                line.setAttribute("y1", y + radius);
                line.setAttribute("x2", childX);
                line.setAttribute("y2", childY - radius);
                line.setAttribute("stroke", "#666");
                line.setAttribute("stroke-width", "1");
                svg.appendChild(line);
                
                // Recursively visualize child
                this._visualizeNode(svg, children[key], childX, childY, xOffset / 2, radius * 0.8);
            });
        }
    }
}

// Module exports
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FractalGenerator;
}
