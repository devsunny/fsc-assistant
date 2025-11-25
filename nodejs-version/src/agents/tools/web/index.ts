// src/agents/tools/web/index.ts

import fetch from 'node-fetch';

export const fetchWebPage = async (url: string): Promise<string> => {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.text();
  } catch (error) {
    console.error('Web page fetch failed:', error);
    throw error;
  }
};

export const scrapeTextContent = async (url: string): Promise<string> => {
  try {
    const html = await fetchWebPage(url);
    // Simple HTML text extraction - in reality this would use a proper parser
    return html.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
  } catch (error) {
    console.error('Web scraping failed:', error);
    throw error;
  }
};

export default {
  fetchWebPage,
  scrapeTextContent
};