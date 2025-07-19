import ReactMarkdown from 'react-markdown';
import { ReactNode } from 'react';

interface ChatBubbleProps {
    role: 'user' | 'assistant';
    content: string;
  }
  
  export default function ChatBubble({ role, content }: ChatBubbleProps) {
    const isUser = role === 'user';
  
    return (
      <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
        <div
          className={`max-w-[75%] px-4 py-2 rounded-2xl shadow text-sm whitespace-pre-wrap
            ${isUser ? 'bg-blue-600 text-white' : 'bg-zinc-700 text-white'}`}
        >
          {isUser ? (
            content
          ) : (
            <div className="prose prose-invert prose-sm break-words">
              <ReactMarkdown
                components={{
                  code(props: any) {
                    const {inline, children, ...rest} = props;
                    return inline ? (
                      <code className="bg-zinc-800 px-1 py-0.5 rounded text-pink-400 font-mono" {...rest}>{children}</code>
                    ) : (
                      <pre className="bg-zinc-800 p-3 rounded-lg overflow-x-auto my-2"><code className="font-mono text-pink-400" {...rest}>{children}</code></pre>
                    );
                  },
                  ul: ({children}) => <ul className="list-disc ml-6 my-2">{children}</ul>,
                  ol: ({children}) => <ol className="list-decimal ml-6 my-2">{children}</ol>,
                  li: ({children}) => <li className="my-1">{children}</li>,
                  blockquote: ({children}) => <blockquote className="border-l-4 border-blue-400 pl-4 italic text-zinc-300 my-2">{children}</blockquote>,
                  a: ({href, children}) => <a href={href} className="text-blue-400 underline" target="_blank" rel="noopener noreferrer">{children}</a>,
                }}
              >
                {content}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    );
  }
  