import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
import aiohttp
from sqlmodel import select
from app.services.discovery import DiscoveryService
from app.db.models import AgentRegistry, ProtocolMapping

@pytest.mark.asyncio
class TestDiscoveryService:
    @patch("app.services.discovery.sessionmaker")
    @patch("app.services.discovery.DiscoveryService._ping_agent")
    async def test_ping_agents_loop(self, mock_ping_agent, mock_sessionmaker):
        # Setup mocks
        mock_session = AsyncMock()
        mock_sessionmaker.return_value.return_value.__aenter__.return_value = mock_session
        
        agent = AgentRegistry(
            agent_id="agent-1",
            name="Test Agent",
            endpoint_url="http://localhost:8080",
            supported_protocols=["A2A"]
        )
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [agent]
        mock_session.execute.return_value = mock_result
        
        service = DiscoveryService(ping_interval=0.1)
        
        # Run for one iteration
        task = asyncio.create_task(service._ping_agents_loop())
        await asyncio.sleep(0.2)
        task.cancel()
        
        assert mock_ping_agent.called
        assert mock_session.commit.called

    @patch("aiohttp.ClientSession.get")
    async def test_ping_agent_success(self, mock_get):
        # Mock response
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_get.return_value.__aenter__.return_value = mock_resp
        
        agent = AgentRegistry(
            agent_id="agent-1",
            endpoint_url="localhost:8080",
            is_active=False
        )
        db_session = MagicMock()
        service = DiscoveryService()
        
        async with aiohttp.ClientSession() as client_session:
            await service._ping_agent(client_session, agent, db_session)
        
        assert agent.is_active is True
        assert agent.last_seen is not None
        db_session.add.assert_called_with(agent)

    @patch("aiohttp.ClientSession.get")
    async def test_ping_agent_timeout(self, mock_get):
        mock_get.side_effect = asyncio.TimeoutError()
        
        agent = AgentRegistry(
            agent_id="agent-1",
            endpoint_url="http://localhost:8080",
            is_active=True
        )
        db_session = MagicMock()
        service = DiscoveryService()
        
        async with aiohttp.ClientSession() as client_session:
            await service._ping_agent(client_session, agent, db_session)
        
        assert agent.is_active is False
        db_session.add.assert_called_with(agent)

    async def test_find_collaborators(self):
        # Mock database session
        session = AsyncMock()
        
        # Mock protocol mappings: A2A -> MCP
        mapping = ProtocolMapping(source_protocol="A2A", target_protocol="MCP")
        mapping_result = MagicMock()
        mapping_result.scalars.return_value.all.return_value = [mapping]
        
        # Mock candidate agents:
        # Agent 1: supports [MCP] -> score should be 1.0 (mappable from A2A)
        # Agent 2: supports [XYZ] -> score should be 0.0
        agent1 = AgentRegistry(agent_id="a1", supported_protocols=["MCP"], is_active=True)
        agent2 = AgentRegistry(agent_id="a2", supported_protocols=["XYZ"], is_active=True)
        agent_result = MagicMock()
        agent_result.scalars.return_value.all.return_value = [agent1, agent2]
        
        session.execute.side_effect = [mapping_result, agent_result]
        
        results = await DiscoveryService.find_collaborators(
            session=session,
            source_protocols=["A2A"],
            min_score=0.5
        )
        
        assert len(results) == 1
        assert results[0]["agent"].agent_id == "a1"
        assert results[0]["compatibility_score"] == 1.0

    async def test_start_stop_discovery(self):
        service = DiscoveryService()
        with patch("asyncio.create_task") as mock_create:
            await service.start_periodic_discovery()
            assert service._ping_task is not None
            mock_create.assert_called_once()
            
            # Idempotency check
            await service.start_periodic_discovery()
            mock_create.assert_called_once()
            
            # Stop
            mock_task = asyncio.Future()
            mock_task.cancel() # Simulate cancellation
            service._ping_task = mock_task
            await service.stop_periodic_discovery()
            assert service._ping_task is None
