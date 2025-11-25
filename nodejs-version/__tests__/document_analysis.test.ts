import { analyzeText, extractKeywords } from '../src/agents/tools/document_analysis';

describe('Document Analysis Tools', () => {
  it('should analyze empty text correctly', () => {
    const result = analyzeText('');
    expect(result.wordCount).toBe(0);
    expect(result.characterCount).toBe(0);
    expect(result.sentenceCount).toBe(0);
    expect(result.paragraphCount).toBe(0);
    expect(result.readingTime).toBe(0);
  });

  it('should analyze simple text correctly', () => {
    const text = 'Hello world. This is a test.';
    const result = analyzeText(text);
    
    expect(result.wordCount).toBe(6);
    expect(result.characterCount).toBe(27);
    expect(result.sentenceCount).toBe(2);
    expect(result.paragraphCount).toBe(1);
    expect(result.readingTime).toBeGreaterThan(0);
  });

  it('should extract keywords correctly', () => {
    const text = 'The quick brown fox jumps over the lazy dog. The fox is quick and brown.';
    const keywords = extractKeywords(text, 3);
    
    expect(keywords).toHaveLength(3);
    expect(keywords).toContain('quick');
    expect(keywords).toContain('brown');
    expect(keywords).toContain('fox');
  });

  it('should handle text with no meaningful words', () => {
    const text = 'a b c d e f g h i j k l m n o p q r s t u v w x y z';
    const keywords = extractKeywords(text);
    
    // Should return empty or minimal results for very short words
    expect(keywords).toBeDefined();
  });
});