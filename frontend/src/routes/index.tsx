import { createFileRoute } from "@tanstack/react-router";
import { ChatWidget } from "@/components/chat/ChatWidget";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Techy — AI Chat Assistant Widget" },
      {
        name: "description",
        content:
          "A premium purple-and-white AI chatbot widget for modern SaaS websites, ready to connect to your backend.",
      },
      { property: "og:title", content: "Techy — AI Chat Assistant Widget" },
      {
        property: "og:description",
        content:
          "A premium purple-and-white AI chatbot widget for modern SaaS websites.",
      },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <div className="min-h-screen bg-background">
      <header className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-primary text-sm font-bold text-primary-foreground">
            T
          </span>
          <span className="text-lg font-bold tracking-tight">Techy</span>
        </div>
        <nav className="hidden gap-7 text-sm font-medium text-muted-foreground sm:flex">
          <a href="#" className="transition-colors hover:text-foreground">Product</a>
          <a href="#" className="transition-colors hover:text-foreground">Pricing</a>
          <a href="#" className="transition-colors hover:text-foreground">Docs</a>
        </nav>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-20 text-center sm:py-28">
        <span className="inline-flex items-center gap-2 rounded-full border border-border bg-accent px-3 py-1 text-xs font-medium text-accent-foreground">
          ✨ AI Assistant Widget
        </span>
        <h1 className="mt-6 text-4xl font-extrabold tracking-tight sm:text-5xl">
          Add a premium AI chat experience to{" "}
          <span className="bg-gradient-primary bg-clip-text text-transparent">
            your website
          </span>
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-base text-muted-foreground">
צ'אטבוט מעוצב ברמה מקצועית, מוכן לשימוש אמיתי, עם תמיכה מלאה ב-Markdown, הצגת קוד בצורה נוחה ואנימציות חלקות שמעניקות חוויית משתמש מודרנית ומהנה. לחצו על הכפתור בפינה הימנית התחתונה כדי לנסות אותו.        </p>
        <div className="mt-8 flex justify-center gap-3">
          <a
            href="#"
            className="rounded-xl bg-gradient-primary px-6 py-3 text-sm font-semibold text-primary-foreground shadow-button transition-transform hover:scale-105"
          >
            Get started
          </a>
          <a
            href="#"
            className="rounded-xl border border-border bg-card px-6 py-3 text-sm font-semibold text-foreground transition-colors hover:bg-accent"
          >
            Learn more
          </a>
        </div>
      </main>

      <ChatWidget />
    </div>
  );
}
