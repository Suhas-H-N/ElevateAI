# ElevateAI — Premium AI Interview Platform

> Next.js 14 · Supabase · OpenAI/Anthropic · Tailwind CSS · Framer Motion

A production-ready, full-stack AI interview preparation platform with real-time streaming AI conversations, animated scorecards, resume optimization, and a premium dark UI.

---

## ✨ Feature Overview

| Feature | Details |
|---------|---------|
| 🤖 **AI Interviewer** | Streaming GPT-4o-mini chat with role/difficulty/type configuration |
| 🎤 **Speech-to-Text** | Browser Web Speech API — speak answers instead of typing |
| 📊 **Animated Scorecard** | Communication, Technical, Structure, Confidence dimensions + keyword analysis |
| 📄 **Resume Optimizer** | PDF upload → ATS match score + AI improvement suggestions |
| 📈 **Progress Dashboard** | Recharts area chart, skill breakdown, streak tracking |
| 🔐 **Auth** | Supabase Auth — Email/Password + Google + GitHub OAuth |
| 🌐 **Edge-Ready API** | Streaming interview route on Vercel Edge Runtime |
| 🎨 **Design System** | Deep Slate + Indigo palette, glassmorphism, Framer Motion transitions |

---

## 🗂 Project Structure

```
elevate-ai/
├── app/
│   ├── layout.tsx              # Root layout — fonts, noise overlay, toaster
│   ├── page.tsx                # Landing page
│   ├── globals.css             # Design system: glass, cards, buttons, inputs
│   ├── dashboard/
│   │   ├── layout.tsx          # AppShell wrapper
│   │   └── page.tsx            # Stats, charts, recent interviews
│   ├── interview/
│   │   └── page.tsx            # Setup → streaming AI chat
│   ├── feedback/
│   │   ├── page.tsx            # Scorecard list
│   │   └── [id]/page.tsx       # Individual scorecard
│   ├── resume/
│   │   └── page.tsx            # PDF upload + AI analysis
│   ├── auth/
│   │   ├── login/page.tsx      # Email + OAuth login
│   │   └── signup/page.tsx     # Signup with password strength
│   └── api/
│       ├── interview/stream/route.ts   # SSE streaming AI interviewer
│       ├── scorecard/route.ts          # Scorecard generation
│       ├── resume/analyze/route.ts     # PDF parse + AI analysis
│       └── auth/callback/route.ts      # Supabase OAuth callback
│
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx         # Collapsible sidebar with Framer Motion
│   │   └── AppShell.tsx        # Authenticated page wrapper
│   ├── ui/
│   │   ├── ScoreRing.tsx       # Animated SVG score ring
│   │   ├── SkeletonLoader.tsx  # Multiple skeleton variants
│   │   └── Badge.tsx           # Badge, StatCard, EmptyState, ProgressBar
│   ├── dashboard/
│   │   └── PerformanceChart.tsx # Recharts area chart
│   ├── interview/
│   │   ├── InterviewChat.tsx   # Streaming chat + speech + typing indicator
│   │   └── InterviewSetup.tsx  # Role/difficulty/type configuration UI
│   ├── feedback/
│   │   └── ScorecardView.tsx   # Full scorecard with collapsible Q breakdown
│   └── resume/
│       └── ResumeUploader.tsx  # Drag-drop PDF + job description + results
│
├── hooks/
│   ├── useAuth.ts              # Supabase auth state
│   └── useInterview.ts         # Interview session + streaming state
│
├── lib/
│   ├── utils.ts                # cn(), formatDate, score helpers, labels
│   ├── ai/
│   │   ├── prompts.ts          # All AI system prompts
│   │   └── client.ts           # OpenAI + Anthropic unified client
│   └── supabase/
│       ├── client.ts           # Browser client
│       ├── server.ts           # Server client (SSR)
│       └── middleware.ts       # Auth protection middleware
│
├── types/index.ts              # All TypeScript interfaces
├── middleware.ts               # Next.js route protection
├── supabase/schema.sql         # Full DB schema with RLS
├── tailwind.config.ts          # Full design token system
└── .env.local.example          # Environment variable template
```

---

## ⚙️ Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/elevate-ai.git
cd elevate-ai
npm install         # or: pnpm install / yarn install
```

### 2. Environment Variables

```bash
cp .env.local.example .env.local
```

Open `.env.local` and fill in:

```env
# Supabase — from supabase.com → Project Settings → API
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# AI — at least one required
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 3. Set Up Supabase

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** → paste the entire contents of `supabase/schema.sql` → Run
3. In **Authentication → Providers**: enable Google and/or GitHub
4. In **Authentication → URL Configuration**: add `http://localhost:3000/api/auth/callback` to Redirect URLs

### 4. Run Locally

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## 🧠 AI Provider Setup

### OpenAI (Recommended for interviews)
- Get key: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Uses: `gpt-4o-mini` (fast + cheap) for streaming interviews
- Cost: ~$0.002–0.01 per interview session

### Anthropic (Optional)
- Get key: [console.anthropic.com](https://console.anthropic.com)
- Uses: `claude-3-5-haiku-20241022` for scorecard generation
- Swap provider in `lib/ai/client.ts` → `provider: "anthropic"`

The app works with **either or both** providers. The API routes default to OpenAI but gracefully fall back.

---

## 🚀 Deploy to Vercel

```bash
npm install -g vercel
vercel

# Set env vars in Vercel dashboard or via CLI:
vercel env add OPENAI_API_KEY
vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
```

After deploying, update Supabase:
- Auth → URL Configuration → add your `https://yourapp.vercel.app/api/auth/callback`
