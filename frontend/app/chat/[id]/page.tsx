'use client';

import { useParams } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import ChatBubble from '../components/ChatBubble';
import { ArrowPathIcon } from '@heroicons/react/24/outline';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

const PROMPT_SUGGESTIONS = [
  'Tell me a fun fact',
  "What's the weather like?",
  'Summarize our conversation',
];

export default function ChatPage() {
  const { id } = useParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [sessionTitle, setSessionTitle] = useState<string>('Chat with AI');
  const chatRef = useRef<HTMLDivElement>(null);

  // Fetch session title on mount
  useEffect(() => {
    const fetchTitle = async () => {
      try {
        const res = await fetch(`http://localhost:8000/meta/${id}`);
        if (!res.ok) throw new Error('No meta');
        const data = await res.json();
        if (data.title) setSessionTitle(data.title);
      } catch {
        setSessionTitle('Chat with AI');
      }
    };
    if (id) fetchTitle();
  }, [id]);

  // Fetch chat history
  const fetchHistory = async () => {
    setHistoryLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/memory/${id}`);
      if (!res.ok) throw new Error('Failed to fetch chat history');
      const data = await res.json();
      setMessages(data.filter((msg: any) => msg.role === 'user' || msg.role === 'assistant'));
    } catch (err) {
      setMessages([{ role: 'assistant', content: '⚠️ Failed to load chat history.' }]);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    if (id) fetchHistory();
    // eslint-disable-next-line
  }, [id]);

  // Refresh button handler
  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchHistory();
    setRefreshing(false);
  };

  // Auto-scroll on new message
  useEffect(() => {
    chatRef.current?.scrollTo(0, chatRef.current.scrollHeight);
  }, [messages, isLoading]);

  const sendMessage = async (msgOverride?: string) => {
    const userInput = typeof msgOverride === 'string' ? msgOverride : input;
    if (!userInput.trim() || isLoading) return;
    const userMsg: Message = { role: 'user', content: userInput };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);
    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.content, session_id: id }),
      });
      if (!res.ok) throw new Error('Failed to get AI response');
      const data = await res.json();
      const aiMsg: Message = { role: 'assistant', content: data.reply };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      const errMsg: Message = { role: 'assistant', content: '⚠️ Error contacting server.' };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-zinc-900 text-white dark:bg-zinc-900">
      {/* Top bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-950">
        <div className="text-lg font-semibold truncate max-w-[70vw]">{sessionTitle}</div>
        <button
          onClick={handleRefresh}
          className="ml-2 p-2 rounded hover:bg-zinc-800 transition flex items-center"
          aria-label="Refresh chat"
          disabled={refreshing || historyLoading}
        >
          {refreshing || historyLoading ? (
            <svg className="animate-spin h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
          ) : (
            <ArrowPathIcon className="h-5 w-5 text-blue-400" />
          )}
        </button>
      </div>
      {/* Chat area */}
      <div
        ref={chatRef}
        className="flex-1 overflow-y-auto p-4 space-y-4"
        style={{ scrollBehavior: 'smooth' }}
      >
        {historyLoading ? (
          <div className="text-zinc-400">Loading chat history...</div>
        ) : messages.length === 0 ? (
          <div className="text-zinc-400">No messages yet. Start the conversation!</div>
        ) : (
          messages.map((msg, idx) => (
            <ChatBubble key={idx} role={msg.role} content={msg.content} />
          ))
        )}
        {/* Typing indicator */}
        {isLoading && !historyLoading && (
          <div className="flex items-center gap-2 mt-2 animate-pulse">
            <div className="h-3 w-3 rounded-full bg-blue-400 animate-bounce" style={{animationDelay: '0ms'}}></div>
            <div className="h-3 w-3 rounded-full bg-blue-400 animate-bounce" style={{animationDelay: '150ms'}}></div>
            <div className="h-3 w-3 rounded-full bg-blue-400 animate-bounce" style={{animationDelay: '300ms'}}></div>
            <span className="ml-2 text-zinc-400 text-sm">Assistant is typing…</span>
          </div>
        )}
      </div>
      {/* Input bar */}
      <form
        className="border-t border-zinc-700 p-4 bg-zinc-950 dark:bg-zinc-950 flex gap-2"
        onSubmit={e => {
          e.preventDefault();
          sendMessage();
        }}
      >
        <textarea
          rows={1}
          className="flex-1 resize-none p-3 rounded-lg bg-zinc-800 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-zinc-800"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold shadow hover:bg-blue-700 transition disabled:opacity-60 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </form>
      {/* Prompt suggestions */}
      <div className="flex gap-2 px-4 py-2 bg-zinc-950 border-t border-zinc-800">
        {PROMPT_SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            className="px-3 py-1 rounded-full bg-zinc-800 text-zinc-200 hover:bg-blue-600 hover:text-white transition text-sm border border-zinc-700"
            onClick={() => sendMessage(suggestion)}
            disabled={isLoading}
            type="button"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}
