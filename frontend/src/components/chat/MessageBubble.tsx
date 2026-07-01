import { motion } from "framer-motion";
import avatar from "@/assets/assistant-avatar.png";
import { MarkdownMessage } from "./MarkdownMessage";
import type { ChatMessage } from "./types";

function formatTime(ts: number) {
  return new Date(ts).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className={`flex w-full gap-2.5 ${isUser ? "flex-row-reverse" : "flex-row"}`}
    >
      {!isUser && (
        <img
          src={avatar}
          alt="AI assistant avatar"
          width={32}
          height={32}
          loading="lazy"
          className="h-8 w-8 shrink-0 rounded-full border border-border bg-card object-cover"
        />
      )}
      <div
        className={`flex max-w-[78%] flex-col gap-1 ${isUser ? "items-end" : "items-start"}`}
      >
        <div
          className={
            isUser
              ? "rounded-2xl rounded-tr-sm bg-gradient-primary px-4 py-2.5 text-sm leading-relaxed text-primary-foreground shadow-button"
              : "rounded-2xl rounded-tl-sm border border-border bg-card px-4 py-2.5 text-card-foreground shadow-sm"
          }
        >
          {isUser ? (
            <p
              dir="auto"
              className="whitespace-pre-wrap break-words text-sm leading-relaxed [unicode-bidi:plaintext]"
            >
              {message.content}
            </p>
          ) : (
            <MarkdownMessage content={message.content} />
          )}
        </div>
        <span className="px-1 text-[10px] text-muted-foreground">
          {formatTime(message.createdAt)}
        </span>
      </div>
    </motion.div>
  );
}