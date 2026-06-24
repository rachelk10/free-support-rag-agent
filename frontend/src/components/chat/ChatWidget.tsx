import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { MessageCircle, X } from "lucide-react";
import { ChatPanel } from "./ChatPanel";
import { useChat } from "./useChat";

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const { messages, isTyping, send, reset } = useChat();

  // Close on Escape for accessibility.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col items-end gap-3 sm:bottom-6 sm:right-6">
      <AnimatePresence>
        {open && (
          <ChatPanel
            messages={messages}
            isTyping={isTyping}
            onSend={send}
            onClose={() => setOpen(false)}
            onReset={reset}
          />
        )}
      </AnimatePresence>

      <motion.button
        type="button"
        onClick={() => setOpen((v) => !v)}
        whileHover={{ scale: 1.06 }}
        whileTap={{ scale: 0.94 }}
        aria-label={open ? "Close chat" : "Open chat"}
        aria-expanded={open}
        className="relative grid h-14 w-14 place-items-center rounded-full bg-gradient-primary text-primary-foreground shadow-button"
      >
        <AnimatePresence mode="wait" initial={false}>
          {open ? (
            <motion.span
              key="close"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.18 }}
            >
              <X className="h-6 w-6" />
            </motion.span>
          ) : (
            <motion.span
              key="open"
              initial={{ rotate: 90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: -90, opacity: 0 }}
              transition={{ duration: 0.18 }}
            >
              <MessageCircle className="h-6 w-6" />
            </motion.span>
          )}
        </AnimatePresence>
        {!open && (
          <span className="absolute right-0 top-0 flex h-3.5 w-3.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary-glow opacity-75" />
            <span className="relative inline-flex h-3.5 w-3.5 rounded-full border-2 border-background bg-primary-glow" />
          </span>
        )}
      </motion.button>
    </div>
  );
}