'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

type Session = {
  id: string;
  title: string;
  created_at: string;
};

export default function Home() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const res = await fetch('http://localhost:8000/sessions');
        const data = await res.json();
        setSessions(data.reverse()); // recent first
      } catch (error) {
        console.error('Failed to fetch sessions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, []);

  return (
    <main className="min-h-screen bg-zinc-900 text-white p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-3xl font-bold">🧠 My AI Chats</h1>
        <button
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold shadow hover:from-green-600 hover:to-blue-600 transition disabled:opacity-60 disabled:cursor-not-allowed"
          onClick={async () => {
            setCreating(true);
            try {
              const res = await fetch('http://localhost:8000/sessions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
              });
          
              if (!res.ok) {
                const errorText = await res.text();
                console.error('Backend returned error:', errorText);
                throw new Error(`HTTP ${res.status}: ${errorText}`);
              }
          
              const data = await res.json();
              console.log('✅ Created session:', data);
              router.push(`/chat/${data.id}`);
            } catch (err: any) {
              console.error('❌ Failed to create session:', err.message);
              alert(`❌ Failed to create new chat session.\n\n${err.message}`);
            } finally {
              setCreating(false);
            }
          }}
          
          disabled={creating}
        >
          <span className="text-xl">＋</span>
          <span>New Chat</span>
        </button>
      </div>

      {loading ? (
        <p className="text-zinc-400">Loading...</p>
      ) : sessions.length === 0 ? (
        <p className="text-zinc-400">No sessions yet. Start chatting!</p>
      ) : (
        <ul className="space-y-3">
          {sessions.map((session) => (
            <li key={session.id}>
              <Link
                href={`/chat/${session.id}`}
                className="block p-4 rounded-lg bg-zinc-800 hover:bg-zinc-700 transition"
              >
                <div className="text-lg font-medium">{session.title}</div>
                <div className="text-sm text-zinc-400">{new Date(session.created_at).toLocaleString()}</div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
