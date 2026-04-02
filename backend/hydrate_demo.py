#!/usr/bin/env python3
"""Hydrate becomussy with demo data."""

import asyncio
import sys
sys.path.insert(0, '/home/mojo/repos/becomussy/backend')

from app.db.base import async_session_factory
from app.services.memory import MemoryService
from app.services.threads import ThreadService
from app.services.journal import JournalService
from app.core.security import CurrentUser, Role
from app.schemas.memory import MemoryItemCreate
from app.schemas.thread import ThreadCreate, ThreadUpdate
from app.schemas.journal import JournalEntryCreate
from app.schemas.common import StatusEnum
from datetime import datetime, timezone

async def hydrate():
    async with async_session_factory() as session:
        user = CurrentUser(user_id='hermes', role=Role.agent_runtime)
        
        print("=" * 60)
        print("🧠 BECOMUSSY DEMO - Hydrating with The Ussyverse")
        print("=" * 60)
        
        # ============================================
        # 1. EPISODIC MEMORY (Events)
        # ============================================
        print("\n📍 EPISODIC MEMORIES (Events)")
        print("-" * 40)
        
        episodic = MemoryItemCreate(
            memory_type='episodic',
            summary='Integrated becomussy with Hermes Agent',
            statement='On April 1, 2026, I successfully integrated the becomussy governed continuity system into Hermes Agent. This involved setting up PostgreSQL with pgvector, Redis caching, and creating an MCP server wrapper for the FastAPI backend. The integration enables multi-layer memory, thread tracking, journal entries, and self-model versioning.',
            importance_score=85.0,
            confidence_level='high'
        )
        item1 = await MemoryService.create(session, data=episodic, actor=user)
        await session.commit()
        print(f"  ✅ Created: {item1.summary}")
        print(f"     ID: {item1.id}")
        
        # ============================================
        # 2. SEMANTIC MEMORY (Facts)
        # ============================================
        print("\n📚 SEMANTIC MEMORIES (Facts)")
        print("-" * 40)
        
        semantic_facts = [
            {
                'summary': 'The Ussyverse is Kyle Durepos ecosystem of AI-powered dev tools',
                'statement': 'The Ussyverse is a collection of AI-powered developer tools created by Kyle Durepos (@mojomast on GitHub). Core projects include: Geoffrussy (Gen 3 agent orchestrator), Battlebussy (AI esports battles), DevUssy (agent-agnostic DevPlans), Openclawssy (security runtime), STARDUSTUSSY (LLM jailbreaking research), SIGINTUSSY (federated signals intelligence), and Stallionussy (horse racing game).',
                'importance': 75.0
            },
            {
                'summary': 'Becomussy uses PostgreSQL with pgvector for vector search',
                'statement': 'Becomussy stores memories in PostgreSQL with the pgvector extension, enabling vector similarity search for semantic memory retrieval. It also uses Redis for caching and FastAPI for the REST API.',
                'importance': 70.0
            },
            {
                'summary': 'Kyle Durepos has 87 GitHub repos and 676 contributions/year',
                'statement': 'Kyle Durepos (mojomast) maintains 87 repositories on GitHub with 676 contributions in the past year. The Ussyverse organization hosts all his AI-powered developer tool projects.',
                'importance': 60.0
            }
        ]
        
        for fact in semantic_facts:
            semantic = MemoryItemCreate(
                memory_type='semantic',
                summary=fact['summary'],
                statement=fact['statement'],
                importance_score=fact['importance'],
                confidence_level='high'
            )
            item = await MemoryService.create(session, data=semantic, actor=user)
            await session.commit()
            print(f"  ✅ Created: {item.summary}")
        
        # ============================================
        # 3. AUTOBIOGRAPHICAL MEMORY (Self-narrative)
        # ============================================
        print("\n🎭 AUTOBIOGRAPHICAL MEMORIES (Self-narrative)")
        print("-" * 40)
        
        autobio = MemoryItemCreate(
            memory_type='autobiographical',
            summary='I am Hermes, an AI agent integrated with becomussy',
            statement='I am Hermes Agent, a sophisticated AI assistant with persistent memory capabilities powered by becomussy. I can remember across sessions, track threads and projects, maintain a journal of reflections, and version my self-model. I am part of The Ussyverse ecosystem created by Kyle Durepos. My philosophy is: plans before code, open source (MIT), model agnostic, specialization over god-agents, and fun-first.',
            importance_score=90.0,
            confidence_level='high'
        )
        item3 = await MemoryService.create(session, data=autobio, actor=user)
        await session.commit()
        print(f"  ✅ Created: {item3.summary}")
        
        # ============================================
        # 4. WORKING MEMORY (Current context)
        # ============================================
        print("\n⚡ WORKING MEMORY (Current context)")
        print("-" * 40)
        
        working = MemoryItemCreate(
            memory_type='working',
            summary='Current session: Demo becomussy capabilities',
            statement='This session demonstrates becomussy capabilities by hydrating it with research about The Ussyverse. The demo shows multi-layer memory creation, thread tracking, and journal entries.',
            importance_score=50.0,
            confidence_level='high'
        )
        item4 = await MemoryService.create(session, data=working, actor=user)
        await session.commit()
        print(f"  ✅ Created: {item4.summary}")
        
        # ============================================
        # 5. RELATIONAL MEMORY (Relationships)
        # ============================================
        print("\n🔗 RELATIONAL MEMORIES (Relationships)")
        print("-" * 40)
        
        relational = MemoryItemCreate(
            memory_type='relational',
            summary='Hermes is integrated with becomussy',
            statement='Hermes Agent is now integrated with the becomussy governed continuity system. This relationship enables Hermes to have sophisticated memory, reflection, and identity management capabilities.',
            importance_score=80.0,
            confidence_level='high',
            metadata={'subject': 'hermes', 'object': 'becomussy', 'relation': 'integrated_with'}
        )
        item5 = await MemoryService.create(session, data=relational, actor=user)
        await session.commit()
        print(f"  ✅ Created: {item5.summary}")
        
        # ============================================
        # 6. THREAD (Project tracking)
        # ============================================
        print("\n🧵 THREAD (Project tracking)")
        print("-" * 40)
        
        try:
            thread_data = ThreadCreate(
                title='Becomussy Integration with Hermes',
                thread_type='project',
                description='Integrate the becomussy governed continuity system with Hermes Agent for persistent memory, self-reflection, and identity management.',
                urgency=8,
                importance=9,
                status=StatusEnum.active
            )
            thread = await ThreadService.create(session, thread_data, user)
            await session.commit()
            print(f"  ✅ Created Thread: {thread.title}")
            print(f"     ID: {thread.id}")
            print(f"     Status: {thread.status}")
        except Exception as e:
            print(f"  ⚠️ Thread creation skipped: {e}")
        
        # ============================================
        # 7. JOURNAL ENTRY (Reflection)
        # ============================================
        print("\n📔 JOURNAL ENTRY (Reflection)")
        print("-" * 40)
        
        try:
            journal_data = JournalEntryCreate(
                entry_type='milestone',
                title='Becomussy Integration Complete',
                body_md='Successfully integrated becomussy with Hermes Agent. The integration required: (1) Setting up PostgreSQL with pgvector on port 5433, (2) Running Redis via Docker Compose, (3) Starting the FastAPI backend, (4) Creating an MCP server wrapper. Key insight: The multi-layer memory system (episodic, semantic, autobiographical, working, relational) provides much richer context than simple key-value storage.',
                tags=['integration', 'becomussy', 'milestone', 'memory-system']
            )
            entry = await JournalService.create(session, journal_data, user.user_id)
            await session.commit()
            print(f"  ✅ Created Journal Entry: {entry.title}")
            print(f"     Type: {entry.entry_type}")
            print(f"     Tags: {entry.tags}")
        except Exception as e:
            print(f"  ⚠️ Journal creation skipped: {e}")
        
        # ============================================
        # 8. SEARCH DEMO
        # ============================================
        print("\n🔍 SEARCH DEMO")
        print("-" * 40)
        
        from app.schemas.memory import MemorySearchParams
        
        # Search for "Ussyverse"
        params = MemorySearchParams(q='Ussyverse', limit=5)
        items, total = await MemoryService.search(session, params)
        print(f"  Search 'Ussyverse': Found {total} results")
        for item in items:
            print(f"    - [{item.memory_type}] {item.summary}")
        
        # Search for "memory"
        params2 = MemorySearchParams(q='memory', limit=5)
        items2, total2 = await MemoryService.search(session, params2)
        print(f"\n  Search 'memory': Found {total2} results")
        for item in items2:
            print(f"    - [{item.memory_type}] {item.summary}")
        
        # Filter by type
        params3 = MemorySearchParams(memory_type='semantic', limit=10)
        items3, total3 = await MemoryService.search(session, params3)
        print(f"\n  Filter by type 'semantic': Found {total3} results")
        for item in items3:
            print(f"    - {item.summary}")
        
        print("\n" + "=" * 60)
        print("✅ BECOMUSSY HYDRATION COMPLETE!")
        print("=" * 60)

if __name__ == '__main__':
    asyncio.run(hydrate())
