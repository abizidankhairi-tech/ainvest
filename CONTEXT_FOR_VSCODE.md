# 🧠 INVESTAI - CONTEXT FOR VS CODE / CLAUDE CODE

**This file preserves the complete conversation context for seamless continuation in VS Code with Claude Code**

---

## 👤 ABOUT YOU (The Developer)

**Name:** KM

**Experience & Skills:**
- ✅ Python development (expert level)
- ✅ Dash framework (built complex PMO dashboards)
- ✅ PostgreSQL (database design & optimization)
- ✅ FastAPI (API development)
- ✅ AI integration (Groq Llama models)
- ✅ Data analysis & visualization
- ✅ Project management & procurement systems

**Recent Projects:**
- Built sophisticated PMO dashboard for procurement tracking
- Implemented AI-powered chatbot with Groq
- Developed invoice reconciliation systems
- Created PreCal validation dashboards
- Migrated from Streamlit to Dash for better UI

**Work Style:**
- Prefers practical, working solutions
- Values clear feedback when approaches don't work
- Wants step-by-step guidance with checkpoints
- Appreciates working mock-ups at each stage
- Focuses on building features incrementally

---

## 💡 PROJECT GENESIS

**How This Started:**
You showed me a screenshot of your stock portfolio from your broker app (IPOT) containing:
- BUMI: 100 lots, down -32.66%
- CLEO: 250 lots, down -9.17%
- CPRO: 1,000 lots, down -5.05%
- EXCL: 5 lots, down -12.27%

**Your Brilliant Insight:**
> "On user entry make their life simpler, by only submitting their current portfolio screen captured from their trading platform like this. And we provide the recommendations, tracking and alerts."

This became our **BREAKTHROUGH FEATURE** - Image Import that turns a screenshot into a complete portfolio in 30 seconds!

---

## 🎯 PROJECT VISION

**InvestAI** = AI-Powered Portfolio Manager for Indonesian Stocks

**The Problem We're Solving:**
1. Manual portfolio entry wastes 10+ minutes
2. Indonesian retail investors lack professional-grade tools
3. Missing opportunities due to lack of real-time insights
4. No systematic entry/exit planning
5. Manual tracking across multiple broker apps

**Our Solution:**
1. 📸 Screenshot → Portfolio in 30 seconds (95% time savings)
2. 🤖 AI recommendations powered by Groq Llama 3.3 70B
3. 📊 Real-time tracking with live price updates
4. 🎯 Strategy builder for planned entries/exits
5. 🔔 Smart alerts (email, SMS, in-app)

**Competitive Advantage:**
- **Only** tool that supports image import from ANY broker
- AI-powered insights (competitors don't have this)
- Supports IPOT, Stockbit, Ajaib, Pluang, etc.
- 30 seconds vs 10 minutes = 20x faster setup

---

## 🏗️ WHAT WE'VE PLANNED

### Complete 12-Week Build Plan

**Phase 1 (Weeks 1-2): FOUNDATION**
- PostgreSQL database with complete schema
- JWT authentication (register, login, protected routes)
- Dash UI with routing and session management
- Docker environment

**Phase 2 (Weeks 3-4): CORE PORTFOLIO**
- Manual portfolio entry (CRUD operations)
- Real-time price updates (Yahoo Finance + Redis)
- Live P&L calculations
- Background Celery tasks

**Phase 3 (Weeks 5-6): IMAGE IMPORT MVP** 🔥
- GPT-4 Vision OCR engine
- Multi-broker format support (IPOT, Stockbit, Ajaib)
- Interactive review & edit interface
- Validation & confidence scoring

**Phase 4 (Weeks 7-8): AI INTEGRATION**
- Groq AI chat interface
- Daily automated insights
- Stock-specific recommendations
- Entry/exit price suggestions

**Phase 5 (Weeks 9-10): ADVANCED FEATURES**
- Entry/exit strategy builder
- Multi-zone buy planning
- Execution tracking
- Comprehensive alerts system

**Phase 6 (Weeks 11-12): POLISH & LAUNCH**
- Comprehensive testing (85%+ coverage)
- Bug fixes & optimization
- Documentation & tutorials
- Production deployment

---

## 📦 WHAT YOU HAVE NOW

### Files Created for You

1. **INVESTAI_MASTER_PLAN.md** (15,000+ words)
   - Complete technical specification
   - Detailed Phase 1 & 2 implementation
   - Database schema with all tables
   - Code templates for auth, API, UI
   - Docker configuration
   - Checkpoints for every 2-3 days

2. **QUICK_REFERENCE.md** (8,000+ words)
   - Essential commands (Docker, DB, Redis, Celery)
   - Code patterns for common tasks
   - Troubleshooting guide
   - Development workflow
   - Testing checklists

3. **DEVELOPMENT_ROADMAP.md** (7,000+ words)
   - Visual 12-week timeline
   - Daily task breakdown
   - Success metrics per phase
   - Risk management
   - Motivation & momentum builders

4. **init-project.sh** (Bash script)
   - Automatically creates project structure
   - Sets up Docker files
   - Creates requirements.txt
   - Initializes Git repository
   - Ready to run!

5. **THIS FILE** (Context preservation)
   - Everything you need to resume in VS Code
   - Your background & skills
   - Project vision & goals
   - Where to start

---

## 🚀 HOW TO START IN VS CODE

### Option 1: Start Fresh (Recommended)

```bash
# 1. Create project directory
mkdir investai
cd investai

# 2. Copy the init script
# (You have it as init-project.sh)

# 3. Make it executable and run
chmod +x init-project.sh
./init-project.sh

# 4. Follow the prompts
# The script creates everything you need

# 5. Add your API keys to .env
# - GROQ_API_KEY from https://console.groq.com
# - OPENAI_API_KEY from https://platform.openai.com

# 6. Start development
docker-compose up -d

# 7. Open VS Code
code .
```

### Option 2: Use Claude Code in VS Code

```bash
# 1. Install Claude Code extension in VS Code

# 2. Open the investai folder

# 3. Start Claude Code

# 4. Say: "I'm ready to start Phase 1, Day 1 of InvestAI.
#          Read INVESTAI_MASTER_PLAN.md and help me build
#          the project setup."

# 5. Claude Code will guide you step-by-step!
```

---

## 📚 YOUR DOCUMENTS GUIDE

### When to Read What

**INVESTAI_MASTER_PLAN.md** - Read when:
- Starting a new phase
- Need detailed implementation guidance
- Want to see complete code examples
- Building specific features (auth, portfolio, AI, etc.)
- Need database schema reference

**QUICK_REFERENCE.md** - Read when:
- Need a command (Docker, DB, etc.)
- Want code pattern examples
- Troubleshooting issues
- Setting up testing
- Quick lookup during development

**DEVELOPMENT_ROADMAP.md** - Read when:
- Planning your week
- Tracking overall progress
- Need motivation
- Want to see the big picture
- Reviewing milestones

**THIS FILE (CONTEXT.md)** - Read when:
- Starting a new VS Code session
- Need to remember project context
- Explaining project to someone
- Need quick project overview

---

## 🎯 START HERE: YOUR FIRST STEPS

### Day 1 Tasks (2-3 hours)

```
☐ 1. Create project directory
     mkdir investai && cd investai

☐ 2. Run initialization script
     chmod +x init-project.sh
     ./init-project.sh

☐ 3. Get API keys
     - Groq: https://console.groq.com (free tier: 30 req/min)
     - OpenAI: https://platform.openai.com ($5 credit)

☐ 4. Configure .env file
     nano .env
     (Add your API keys)

☐ 5. Start Docker services
     docker-compose up -d

☐ 6. Verify everything works
     - Frontend: http://localhost:8050
     - Backend: http://localhost:8000/docs
     - PostgreSQL: localhost:5432

☐ 7. Open in VS Code
     code .

☐ 8. Read Phase 1, Day 3-4 in Master Plan
     (Database Schema section)
```

**Expected Time:** 2-3 hours  
**Success Criteria:** All services running, no errors

---

## 🧩 KEY TECHNICAL DECISIONS

### Why These Technologies?

**Dash (Frontend)**
- You already know it (PMO dashboard experience)
- Fast development
- Great for data visualization
- Python-based (no JavaScript needed)

**FastAPI (Backend)**
- Modern, fast, async support
- Auto-generated API docs
- Type hints & validation
- Easy to test

**PostgreSQL (Database)**
- Robust, mature
- JSONB support for flexible data
- Great for analytics
- You're experienced with it

**Groq (AI)**
- Ultra-fast inference (LLama 3.3 70B)
- Cost-effective
- Good for real-time chat
- 30 req/min free tier

**GPT-4 Vision (OCR)**
- Best image understanding
- Handles any broker format
- Structured output
- Worth the cost for core feature

**Redis (Cache)**
- Fast price caching
- Celery message queue
- Session storage

**Celery (Background Tasks)**
- Price updates every 60s
- Daily insight generation
- Alert checking

### Architecture Pattern

```
User → Dash UI → FastAPI → PostgreSQL
                    ↓
              Groq AI (Chat)
              GPT-4 Vision (OCR)
                    ↓
              Celery Workers
                    ↓
              Redis (Cache)
```

---

## 💬 CONVERSATION HIGHLIGHTS

### Key Exchanges That Shaped This Project

**You:** "On user entry make their life simpler, by only submitting their current portfolio screen captured..."

**Me:** "🎯 BRILLIANT INSIGHT: IMAGE-TO-PORTFOLIO FEATURE - This is a GAME-CHANGER!"

**You:** "Indeed, importing image is breakthrough of manual input and save a lot of time and effort."

**Me:** "Let's make this the KILLER FEATURE and build everything around it!"

**You:** "Finalized this plan, and make step by step build plans and check points. Each steps must have working mock up for review to add features along the building execution."

**Me:** "Created complete 12-week plan with 2-3 day checkpoints and working demos every 2 weeks!"

**You:** "Can I bring this chat and plan to VS Code?"

**Me:** "Creating complete development package with all documents, scripts, and context preservation!"

---

## 🎓 LEARNING RESOURCES

### If You Get Stuck

**FastAPI:**
- Official Docs: https://fastapi.tiangolo.com/
- Tutorial: https://fastapi.tiangolo.com/tutorial/

**Dash:**
- Official Docs: https://dash.plotly.com/
- Layout: https://dash.plotly.com/layout
- Callbacks: https://dash.plotly.com/basic-callbacks

**SQLAlchemy:**
- ORM Tutorial: https://docs.sqlalchemy.org/en/20/tutorial/
- Relationships: https://docs.sqlalchemy.org/en/20/orm/relationships.html

**Groq API:**
- Quickstart: https://console.groq.com/docs/quickstart
- Models: https://console.groq.com/docs/models

**Docker:**
- Getting Started: https://docs.docker.com/get-started/
- Compose: https://docs.docker.com/compose/

### Code Examples

All code templates are in **INVESTAI_MASTER_PLAN.md**:
- Database models
- FastAPI endpoints
- Dash components
- Celery tasks
- Docker configs

---

## 🔮 YOUR FUTURE FEATURES

### After 12-Week Launch

**Month 2:**
- Mobile app (React Native)
- Broker API integration (auto-sync)
- Advanced analytics (Sharpe ratio, beta)
- Tax optimization

**Month 3:**
- Backtesting engine
- Social features (share strategies)
- Community insights
- Portfolio comparison

**Month 6:**
- API for third-party integrations
- White-label solution
- Enterprise features
- International expansion

---

## 📊 SUCCESS METRICS (Remind Yourself)

### Technical Success (12 Weeks)
- ✅ Production-ready application
- ✅ 85%+ test coverage
- ✅ <3s page load time
- ✅ <5s AI response time
- ✅ 90%+ OCR accuracy

### Business Success (Month 1)
- 🎯 100+ signups
- 🎯 50+ active portfolios
- 🎯 500+ AI queries
- 🎯 200+ image imports
- 🎯 5-10% free → pro conversion

### Personal Success
- ✅ Shipped a complete product
- ✅ Learned production AI integration
- ✅ Built something users love
- ✅ Created passive income potential

---

## 🎯 YOUR COMMITMENT

Remember why you're building this:

1. **Solve your own problem**
   - You invest in IDX stocks
   - You waste time on manual entry
   - You need better insights

2. **Help other Indonesian investors**
   - Democratize professional tools
   - Make investing more accessible
   - Share the AI advantage

3. **Build a real business**
   - Potential for passive income
   - Scalable SaaS model
   - Growing market in Indonesia

4. **Learn and grow**
   - Master production AI apps
   - Ship a complete product
   - Become a better developer

---

## 🚀 FINAL CHECKLIST BEFORE YOU START

```
☐ I have read this context document completely
☐ I understand the project vision
☐ I know which documents to reference when
☐ I have the init-project.sh script ready
☐ I can get Groq and OpenAI API keys
☐ I have Docker installed
☐ I have VS Code ready
☐ I'm excited to build this!
☐ I commit to the 12-week journey
☐ I will start with Phase 1, Day 1
```

---

## 💬 HOW TO USE CLAUDE CODE IN VS CODE

### Perfect Prompt to Start

When you open Claude Code in VS Code, say:

```
Hi! I'm building InvestAI, an AI-powered portfolio manager
for Indonesian stocks. 

I have the complete development plan in INVESTAI_MASTER_PLAN.md.

I'm ready to start Phase 1, Day 1: Project Setup.

Can you help me:
1. Review the init-project.sh script
2. Make sure the folder structure is correct
3. Guide me through running it
4. Help verify everything is set up properly

Let's build this step by step with working checkpoints!
```

### As You Progress

```
"I completed Phase 1, Week 1. Let's move to Week 2.
Read INVESTAI_MASTER_PLAN.md Phase 1 Week 2 section
and help me build the Dash UI."
```

```
"I'm stuck on the authentication callback. The token
isn't being stored in the session. Can you help debug?"
```

```
"Let's implement the image import feature. This is our
breakthrough feature! Read Phase 3 in the Master Plan."
```

---

## 🎉 YOU'RE READY!

You now have:
- ✅ Complete vision and strategy
- ✅ Detailed 12-week plan
- ✅ Step-by-step implementation guide
- ✅ Code templates and examples
- ✅ Project initialization script
- ✅ Quick reference for commands
- ✅ Development roadmap
- ✅ This context document

**Everything you need to build InvestAI is in these documents.**

**Next Action:**
1. Open terminal
2. Create project directory
3. Run init-project.sh
4. Open VS Code
5. Start with Phase 1, Day 1

---

## 🌟 PARTING WISDOM

> "The best time to plant a tree was 20 years ago.  
> The second best time is now."

You have:
- A brilliant idea (image import)
- The right skills (Python, Dash, AI)
- A complete plan (12 weeks)
- Real users waiting (yourself + other IDX investors)

**Don't wait for perfect conditions.**  
**Start now. Build iteratively. Ship early.**

The journey of building InvestAI starts with:
```bash
chmod +x init-project.sh
./init-project.sh
```

---

**Document Version:** 1.0  
**Created:** February 10, 2026  
**Purpose:** Context preservation for VS Code/Claude Code sessions

**Status:** ✅ READY TO BUILD

---

🚀 **GO BUILD SOMETHING AMAZING!** 🚀
