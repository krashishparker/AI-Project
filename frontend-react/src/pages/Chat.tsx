import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { resumeService } from '@/services/resume';
import { Resume, ChatMessage } from '@/types';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import { ArrowLeft, Send, Loader2, User, Bot } from 'lucide-react';

export default function Chat() {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const [resume, setResume] = useState<Resume | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadResume();
    loadChatHistory();
  }, [resumeId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadResume = async () => {
    try {
      const data = await resumeService.getResume(Number(resumeId));
      setResume(data);
    } catch (error) {
      console.error('Failed to load resume:', error);
      navigate('/dashboard');
    } finally {
      setIsInitialLoading(false);
    }
  };

  const loadChatHistory = async () => {
    try {
      const history = await resumeService.getChatHistory(Number(resumeId));
      const formattedMessages: ChatMessage[] = history.map((h, idx) => [
        {
          id: idx * 2,
          role: 'user',
          content: h.question,
          timestamp: new Date(h.created_at),
        },
        {
          id: idx * 2 + 1,
          role: 'assistant',
          content: h.answer,
          timestamp: new Date(h.created_at),
        },
      ]).flat();
      setMessages(formattedMessages);
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await resumeService.chat({
        resume_id: Number(resumeId),
        question: input,
      });

      const assistantMessage: ChatMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: ChatMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: error.response?.data?.detail || 'Failed to get response',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (isInitialLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="secondary" onClick={() => navigate('/dashboard')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div className="flex-1">
            <h1 className="font-semibold text-gray-900">{resume?.filename}</h1>
            <p className="text-sm text-gray-600">Chat with AI about this resume</p>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6 flex flex-col">
        <Card className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <Bot className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Start a conversation
                </h3>
                <p className="text-gray-600">
                  Ask questions about the resume, such as:
                </p>
                <div className="mt-4 space-y-2 text-left max-w-md mx-auto">
                  {[
                    'What skills does this candidate have?',
                    'Summarize the work experience',
                    'What projects has the candidate worked on?',
                    'Does the candidate know Python?',
                  ].map((suggestion, idx) => (
                    <button
                      key={idx}
                      onClick={() => setInput(suggestion)}
                      className="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm text-gray-700 transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  )}
                  <div
                    className={`max-w-[70%] rounded-lg p-3 ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    <p className="text-xs mt-1 opacity-70">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                  {message.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex gap-3 justify-start">
                <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div className="bg-gray-100 rounded-lg p-3">
                  <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t p-4">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question about the resume..."
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Card>
      </main>
    </div>
  );
}
