import { motion } from "framer-motion";
import avatar from "@/assets/assistant-avatar.png";

export function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="flex items-end gap-2.5"
      aria-live="polite"
      aria-label="Assistant is typing"
    >
      <img
        src={avatar}
        alt=""
        width={32}
        height={32}
        className="h-8 w-8 shrink-0 rounded-full border border-border bg-card object-cover"
      />
      <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm border border-border bg-card px-4 py-3 shadow-sm">
        <span className="typing-dot h-2 w-2 rounded-full bg-primary" />
        <span
          className="typing-dot h-2 w-2 rounded-full bg-primary"
          style={{ animationDelay: "0.15s" }}
        />
        <span
          className="typing-dot h-2 w-2 rounded-full bg-primary"
          style={{ animationDelay: "0.3s" }}
        />
      </div>
    </motion.div>
  );
}