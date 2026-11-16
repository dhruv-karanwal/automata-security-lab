/**
 * Text tokenization and normalization utilities for formal automata processing
 */

/**
 * Tokenizes raw text into clean uppercase word tokens for sequence processing
 * @param {string} text
 * @returns {string[]} array of uppercase tokens
 */
export function tokenizeText(text) {
  if (!text || typeof text !== 'string') return [];
  // Split on whitespace and strip extraneous punctuation while preserving words
  const rawWords = text.trim().split(/\s+/);
  return rawWords
    .map(w => w.replace(/^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$/g, '').toUpperCase())
    .filter(w => w.length > 0);
}

/**
 * Formats a list of tokens as a string sequence
 * @param {string[]} tokens
 * @returns {string} e.g. "[WIN, PRIZE, NOW]"
 */
export function formatTokenSequence(tokens) {
  if (!tokens || tokens.length === 0) return '[] (empty input)';
  return `[${tokens.join(', ')}]`;
}
