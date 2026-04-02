#!/usr/bin/env python3
import asyncio
from app.db.base import async_session_factory
from app.services.memory import MemoryService
from app.core.security import CurrentUser, Role
from app.schemas.memory import MemoryItemCreate

async def test():
    async with async_session_factory() as session:
        user = CurrentUser(user_id='hermes', role=Role.agent_runtime)
        data = MemoryItemCreate(memory_type='episodic', summary='Test', statement='Test statement')
        try:
            item = await MemoryService.create(session, data, user)
            print(f'Created memory: {item.id}')
        except Exception as e:
            print(f'Error: {e}')
            import traceback
            traceback.print_exc()

asyncio.run(test())
