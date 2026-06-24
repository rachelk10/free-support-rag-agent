import { useCallback, useState } from "react";
import type { ChatMessage } from "./types";
import { initialMessages, makeId } from "./mockData";
import { sendContactMessage } from "./api";

/**
 * Local chat state hook backed by mock data.
 *
 * Structured so it can later be swapped for a FastAPI-backed implementation:
 * replace the simulated reply in `send` with a fetch/stream call, and append
 * tokens to the assistant message for streaming support.
 */
export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [isTyping, setIsTyping] = useState(false);

  const send = useCallback(async (text: string) => {
    const userMessage: ChatMessage = {
      id: makeId(),
      role: "user",
      content: text,
      createdAt: Date.now(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const response = await sendContactMessage(text);
      const replyText =
        response.final_output ||
        (response.needs_human
          ? "הבקשה ממתינה לאישור אנושי. נחזור אליך ברגע שהתשובה מוכנה."
          : "השרת חזר ללא תשובה תקינה.");
      const reply: ChatMessage = {
        id: makeId(),
        role: "assistant",
        content: replyText,
        createdAt: Date.now(),
      };
      setMessages((prev) => [...prev, reply]);
    } catch (error) {
      const messageText =
        error instanceof Error
          ? `שגיאה בחיבור לשרת: ${error.message}`
          : "שגיאה בחיבור לשרת";
      const reply: ChatMessage = {
        id: makeId(),
        role: "assistant",
        content: messageText,
        createdAt: Date.now(),
      };
      setMessages((prev) => [...prev, reply]);
    } finally {
      setIsTyping(false);
    }
  }, []);

  const reset = useCallback(() => {
    setIsTyping(false);
    setMessages([]);
  }, []);

  return { messages, isTyping, send, reset };
}