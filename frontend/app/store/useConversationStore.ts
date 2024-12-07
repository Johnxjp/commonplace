import { create } from 'zustand';

interface ConversationState {
  query: string;  // Handling a new query
  conversationId: string | null;
  setConversation: (query: string, id: string) => void;
  clearConversation: () => void;
}

export const useConversationStore = create<ConversationState>((set) => ({
  query: '',
  conversationId: null,
  setConversation: (query, id) => set({ 
    query, 
    conversationId: id, 
  }),
  clearConversation: () => set({ 
    query: '', 
    conversationId: null, 
  }),
}));