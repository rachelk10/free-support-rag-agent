import { useEffect, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Sparkles, X, RefreshCw } from "lucide-react";
import avatar from "@/assets/assistant-avatar.png";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import { ChatInput } from "./ChatInput";
import type { ChatMessage } from "./types";

interface ChatPanelProps {
  messages: ChatMessage[];
  isTyping: boolean;
  onSend: (text: string) => void;
  onClose: () => void;
  onReset: () => void;
}

export function ChatPanel({
  messages,
  isTyping,
  onSend,
  onClose,
  onReset,
}: ChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages, isTyping]);

  const isEmpty = messages.length === 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 24, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 24, scale: 0.96 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      role="dialog"
      aria-label="AI chat assistant"
      className="pointer-events-auto flex h-[min(620px,80vh)] w-[min(400px,calc(100vw-2rem))] flex-col overflow-hidden rounded-3xl border border-border bg-background shadow-widget"
    >
      {/* Header */}
      <header className="flex items-center gap-3 bg-gradient-primary px-4 py-3.5 text-primary-foreground">
        <img
          src={avatar}
          alt="עוזר טקי"
          width={40}
          height={40}
          className="h-10 w-10 shrink-0 rounded-full border-2 border-white/40 bg-card object-cover"
        />
        <div className="min-w-0 flex-1">
          <h2 className="flex items-center gap-1.5 truncate text-sm font-semibold">
            Techy <Sparkles className="h-3.5 w-3.5" />
          </h2>
          <p className="flex items-center gap-1.5 text-xs text-primary-foreground/80">
            <span className="h-2 w-2 rounded-full bg-emerald-300" />
            Online · AI Assistant
          </p>
        </div>
        <button
          type="button"
          onClick={onReset}
          aria-label="Reset conversation"
          className="grid h-8 w-8 place-items-center rounded-full text-primary-foreground/90 transition-colors hover:bg-white/20"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close chat"
          className="grid h-8 w-8 place-items-center rounded-full text-primary-foreground/90 transition-colors hover:bg-white/20"
        >
          <X className="h-4 w-4" />
        </button>
      </header>

      {/* Conversation */}
      <div
        ref={scrollRef}
        className="chat-scroll flex-1 space-y-4 overflow-y-auto bg-muted/30 px-4 py-4"
      >
        {isEmpty ? (
          <div className="flex h-full flex-col items-center justify-center px-6 text-center">
            <img
              src={avatar}
              alt=""
              width={64}
              height={64}
              className="mb-3 h-16 w-16 rounded-full border border-border bg-card object-cover"
            />
            <p className="text-sm font-semibold text-foreground">
              Start a conversation
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              Ask me anything — I'm here to help.
            </p>
          </div>
        ) : (
          <>
            {messages.map((m) => (
              <MessageBubble key={m.id} message={m} />
            ))}
            <AnimatePresence>{isTyping && <TypingIndicator />}</AnimatePresence>
          </>
        )}
      </div>

      <ChatInput onSend={onSend} disabled={isTyping} />
    </motion.div>
  );
}