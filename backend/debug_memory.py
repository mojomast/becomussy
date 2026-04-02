#!/usr/bin/env python3
"""Debug script to test memory creation with full error handling."""
import asyncio
import traceback
from app.db.base import async_session_factory
from app.services.memory import MemoryService
from app.core.security import CurrentUser, Role
from app.schemas.memory import MemoryItemCreate

async def test():
    async with async_session_factory() as session:
        user = CurrentUser(user_id='hermes', role=Role.agent_runtime)
        
        # Test with minimal data
        print("Test 1: Minimal data")
        try:
            data = MemoryItemCreate(memory_type='episodic')
            print(f"  Schema created: {data.model_dump()}")
            item = await MemoryService.create(session, data, user)
            print(f'  Created memory: {item.id}')
        except Exception as e:
            print(f'  Error: {e}')
            traceback.print_exc()
        
        # Test with summary and statement
        print("\nTest 2: With summary and statement")
        try:
            data = MemoryItemCreate(
                memory_type='episodic',
                summary='Test summary',
                statement='Test statement'
            )
            print(f"  Schema created: {data.model_dump()}")
            item = await MemoryService.create(session, data, user)
            print(f'  Created memory: {item.id}')
        except Exception as e:
            print(f'  Error: {e}')
            traceback.print_exc()
        
        # Test with all optional fields
        print("\nTest 3: With all optional fields")
        try:
            from decimal import Decimal
            data = MemoryItemCreate(
                memory_type='semantic',
                summary='Full test',
                statement='Full statement',
                importance_score=Decimal('75.0'),
                confidence_level='high',
                metadata={'test': 'value'}
            )
            print(f"  Schema created: {data.model_dump()}")
            item = await MemoryService.create(session, data, user)
            print(f'  Created memory: {item.id}')
        except Exception as e:
            print(f'  Error: {e}')
            traceback.print_exc()
        
        # Commit at the end
        await session.commit()
        print("\nAll tests completed and committed!")

asyncio.run(test())
