import type { ChatMessage } from "./types";

let counter = 0;
export const makeId = () => `msg_${Date.now()}_${counter++}`;

export const initialMessages: ChatMessage[] = [];

const sampleReplies: string[] = [
  `Great question! Here's a concise breakdown:

1. **Plan** the component structure
2. **Build** reusable pieces
3. **Polish** the micro-interactions

Want me to expand on any step?`,
  `Here's a quick example you can adapt:

\`\`\`python
def fibonacci(n: int) -> list[int]:
    seq = [0, 1]
    while len(seq) < n:
        seq.append(seq[-1] + seq[-2])
    return seq[:n]

print(fibonacci(8))
\`\`\`

Let me know if you'd like it in another language!`,
  `Sure! A few key points:

- It blends naturally with your **purple-and-white** theme
- Fully responsive across devices
- Ready to connect to your FastAPI backend later

Anything else I can help with?`,
  `Happy to help with that. Here's a small comparison:

| Option | Speed | Effort |
| --- | --- | --- |
| Approach A | Fast | Low |
| Approach B | Medium | Medium |

I'd recommend **Approach A** for most cases.`,
];

export function getMockReply(): string {
  return sampleReplies[Math.floor(Math.random() * sampleReplies.length)];
}