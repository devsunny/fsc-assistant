export class ChatHistory {
  private messages: { role: string; content: string; timestamp: Date }[] = [];
  
  addMessage(role: string, content: string): void {
    this.messages.push({
      role,
      content,
      timestamp: new Date()
    });
  }
  
  getMessages(): { role: string; content: string; timestamp: Date }[] {
    return [...this.messages];
  }
  
  clear(): void {
    this.messages = [];
  }
  
  getLastMessage(): { role: string; content: string; timestamp: Date } | undefined {
    return this.messages[this.messages.length - 1];
  }
  
  getMessageCount(): number {
    return this.messages.length;
  }
}