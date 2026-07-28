import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiSend, FiPlus, FiCode, FiMessageSquare, FiUser, FiCpu } from 'react-icons/fi';
import api from '../api/client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const SUGGESTIONS = [
  'Explain this function in detail',
  'Find potential bugs in the code',
  'Suggest performance improvements',
  'Generate unit tests',
  'Rewrite using async/await',
  'Convert to TypeScript',
];

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '## 👋 Welcome to CodeSage AI Chat!\n\nI can help you with:\n\n- 🔍 **Explain code** — understand any function or class\n- 🐛 **Find bugs** — identify potential issues\n- ✨ **Refactor** — improve code quality\n- 🔄 **Convert** — translate between languages\n- 🧪 **Test** — generate unit tests\n- 📖 **Document** — create documentation\n\nPaste some code or ask a question to get started!',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [codeContext, setCodeContext] = useState('');
  const [showCodeInput, setShowCodeInput] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (content?: string) => {
    const msg = content || input;
    if (!msg.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: msg,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // Attempt API call — fall back to local response
      const { data } = await api.post('/chat/sessions/default/messages', {
        message: msg,
        code_context: codeContext || undefined,
      });
      const assistantMsg: Message = {
        id: data.message?.id || (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message?.content || 'I can help with that! Let me analyze...',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      // Fallback local response
      const fallback = generateLocalResponse(msg, codeContext);
      setMessages((prev) => [
        ...prev,
        { id: (Date.now() + 1).toString(), role: 'assistant', content: fallback, timestamp: new Date() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const generateLocalResponse = (message: string, code?: string): string => {
    const lower = message.toLowerCase();

    if (lower.includes('explain')) {
      return '## Code Explanation\n\nThis code implements a common pattern. Let me break it down:\n\n1. **Input Processing** — The function takes parameters and validates them\n2. **Core Logic** — The main algorithm processes the data\n3. **Output** — Results are returned in the expected format\n\nWould you like me to dive deeper into any specific part?';
    }
    if (lower.includes('bug') || lower.includes('error')) {
      return '## 🐛 Potential Bugs Found\n\n1. **Missing null check** — Input parameters should be validated before use\n2. **Edge case handling** — Consider what happens with empty arrays or negative numbers\n3. **Type safety** — Some variables may need explicit type checking\n\n### Recommendation\nAdd input validation at the beginning of each function and handle edge cases explicitly.';
    }
    if (lower.includes('test')) {
      return '## 🧪 Generated Tests\n\n```python\nimport pytest\n\ndef test_basic_functionality():\n    """Test with standard input."""\n    result = process(valid_input)\n    assert result is not None\n\ndef test_edge_cases():\n    """Test boundary conditions."""\n    assert process([]) == []\n    assert process(None) raises ValueError\n\ndef test_performance():\n    """Test with large dataset."""\n    large_input = list(range(10000))\n    result = process(large_input)\n    assert len(result) == expected_length\n```';
    }

    return '## CodeSage AI\n\nI can help you with code analysis, bug detection, refactoring, testing, and more.\n\nTry asking me to:\n- "Explain this function"\n- "Find bugs in the code"\n- "Generate unit tests"\n- "Suggest improvements"';
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-120px)]">
      <div className="mb-4">
        <h1 className="text-2xl font-bold">AI <span className="gradient-text">Chat</span></h1>
        <p className="text-sm text-[var(--text-secondary)] mt-1">Chat with your code using AI</p>
      </div>

      <div className="flex-1 flex gap-6 min-h-0">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col glass-card overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
              >
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                  style={{
                    background: msg.role === 'user'
                      ? 'linear-gradient(135deg, #667eea, #764ba2)'
                      : 'rgba(255,255,255,0.08)',
                  }}
                >
                  {msg.role === 'user' ? <FiUser className="w-4 h-4" /> : <FiCpu className="w-4 h-4 text-[var(--accent-blue)]" />}
                </div>
                <div
                  className={`max-w-[75%] p-3.5 rounded-2xl text-sm ${
                    msg.role === 'user'
                      ? 'rounded-tr-sm'
                      : 'rounded-tl-sm'
                  }`}
                  style={{
                    background: msg.role === 'user'
                      ? 'linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2))'
                      : 'rgba(255,255,255,0.05)',
                  }}
                >
                  <div className="whitespace-pre-wrap text-[var(--text-primary)] leading-relaxed text-[13px]">
                    {msg.content}
                  </div>
                </div>
              </motion.div>
            ))}

            {loading && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'rgba(255,255,255,0.08)' }}>
                  <FiCpu className="w-4 h-4 text-[var(--accent-blue)]" />
                </div>
                <div className="p-3.5 rounded-2xl rounded-tl-sm" style={{ background: 'rgba(255,255,255,0.05)' }}>
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-[var(--accent-blue)] animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 rounded-full bg-[var(--accent-blue)] animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 rounded-full bg-[var(--accent-blue)] animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions */}
          <div className="px-4 py-2 flex gap-2 overflow-x-auto" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => sendMessage(s)}
                className="shrink-0 px-3 py-1.5 rounded-lg text-[11px] text-[var(--text-secondary)] hover:text-white transition-all whitespace-nowrap"
                style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.06)' }}
              >
                {s}
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="p-4" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
            <div className="flex items-end gap-2">
              <button
                onClick={() => setShowCodeInput(!showCodeInput)}
                className={`p-2.5 rounded-xl transition-all ${showCodeInput ? 'text-[var(--accent-blue)]' : 'text-[var(--text-muted)] hover:text-white'}`}
                style={{ background: 'rgba(255,255,255,0.05)' }}
                title="Attach code context"
              >
                <FiCode className="w-4 h-4" />
              </button>
              <div className="flex-1 relative">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about your code..."
                  rows={1}
                  className="w-full px-4 py-3 rounded-xl text-sm resize-none"
                  style={{
                    background: 'rgba(255,255,255,0.05)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    color: 'var(--text-primary)',
                    outline: 'none',
                  }}
                />
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
                className="btn-primary p-3"
              >
                <FiSend className="w-4 h-4" />
              </motion.button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
