// src/agents/tools/document_analysis.ts

export interface DocumentAnalysis {
  summary: string;
  keywords: string[];
  sentiment: 'positive' | 'negative' | 'neutral';
}

export const analyzeDocument = (text: string): DocumentAnalysis => {
  // Simple mock implementation
  const words = text.split(/\s+/).filter(word => word.length > 0);
  
  // Extract some basic keywords (first few words)
  const keywords = words.slice(0, Math.min(5, words.length));
  
  // Simple sentiment analysis (mock)
  let sentiment: 'positive' | 'negative' | 'neutral' = 'neutral';
  if (text.toLowerCase().includes('good') || text.toLowerCase().includes('great')) {
    sentiment = 'positive';
  } else if (text.toLowerCase().includes('bad') || text.toLowerCase().includes('terrible')) {
    sentiment = 'negative';
  }
  
  return {
    summary: `Document analysis of ${words.length} words`,
    keywords,
    sentiment
  };
};

export const extractKeywords = (text: string, numKeywords: number = 5): string[] => {
  // Simple keyword extraction (first few words)
  const words = text.split(/\s+/).filter(word => word.length > 0);
  return words.slice(0, Math.min(numKeywords, words.length));
};