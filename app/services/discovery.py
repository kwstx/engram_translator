import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import List, Dict, Any, Set, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select
from app.db.models import AgentRegistry, ProtocolMapping
from app.db.session import engine

logger = logging.getLogger(__name__)

class DiscoveryService:
    """
    Service responsible for agent discovery, health monitoring, and collaboration matching.
    """
    
    def __init__(self, ping_interval: int = 60):
        self.ping_interval = ping_interval
        self._ping_task: Optional[asyncio.Task] = None

    async def start_periodic_discovery(self):
        """
        Starts the background task for periodic agent pinging.
        """
        if self._ping_task is not None:
            logger.warning("DiscoveryService: Periodic discovery already running.")
            return
        
        logger.info(f"DiscoveryService: Starting periodic discovery every {self.ping_interval}s.")
        self._ping_task = asyncio.create_task(self.ping_agents_loop())

    async def stop_periodic_discovery(self):
        """
        Stops the periodic discovery background task.
        """
        if self._ping_task:
            logger.info("DiscoveryService: Stopping periodic discovery.")
            self._ping_task.cancel()
            try:
                await self._ping_task
            except asyncio.CancelledError:
                pass
            self._ping_task = None

    async def ping_agents_loop(self):
        """
        Main loop for pinging registered agents.
        """
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        while True:
            try:
                async with async_session() as session:
                    query = select(AgentRegistry)
                    result = await session.execute(query)
                    agents = result.scalars().all()

                    if agents:
                        logger.info(f"DiscoveryService: Pinging {len(agents)} agents...")
                        async with aiohttp.ClientSession() as client_session:
                            tasks = [self._ping_agent(client_session, agent, session) for agent in agents]
                            await asyncio.gather(*tasks)

                        await session.commit()
                        logger.info("DiscoveryService: Health status updated in registry.")
                    else:
                        logger.debug("DiscoveryService: No agents registered for discovery.")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in DiscoveryService loop: {str(e)}", exc_info=True)
            
            await asyncio.sleep(self.ping_interval)

    async def _ping_agent(self, client_session: aiohttp.ClientSession, agent: AgentRegistry, session: AsyncSession):
        """
        Pings a single agent and updates its status.
        """
        try:
            url = agent.endpoint_url if agent.endpoint_url.startswith("http") else f"http://{agent.endpoint_url}"
            health_url = url.rstrip("/") + "/health"
            
            async with client_session.get(health_url, timeout=5) as response:
                is_active = response.status == 200
        except Exception as e:
            logger.debug(f"Ping failed for Agent {agent.agent_id}: {str(e)}")
            is_active = False

        agent.is_active = is_active
        agent.last_seen = datetime.utcnow()
        session.add(agent)

    @staticmethod
    async def find_collaborators(session: AsyncSession, source_protocols: List[str], min_score: float = 0.7) -> List[AgentRegistry]:
        """
        Retrieves rivals with a compatibility score > min_score.
        
        Formula: (shared_protocols + mappable_protocols) / total_protocols
        - total_protocols: Number of protocols supported by the potential collaborator.
        - shared_protocols: Protocols supported by both agents.
        - mappable_protocols: Protocols in the collaborator's list that the source agent 
                             can translate to using available ProtocolMappings.
        """
        # 1. Fetch all available protocol mappings to determine translation capabilities
        mapping_query = select(ProtocolMapping)
        mapping_result = await session.execute(mapping_query)
        mappings = mapping_result.scalars().all()
        
        source_set = {p.upper() for p in source_protocols}
        # Protocols we can reach from what the source supports
        mappable_targets = {m.target_protocol.upper() for m in mappings if m.source_protocol.upper() in source_set}

        # 2. Fetch all currently active candidate agents
        agent_query = select(AgentRegistry).where(AgentRegistry.is_active == True)
        agent_result = await session.execute(agent_query)
        candidates = agent_result.scalars().all()

        collaborators = []
        for agent in candidates:
            target_protocols = {p.upper() for p in agent.supported_protocols}
            if not target_protocols:
                continue
                
            shared = source_set.intersection(target_protocols)
            # Mappable are those target protocols we don't share but can translate to
            mappable = target_protocols.intersection(mappable_targets).difference(source_set)
            
            score = (len(shared) + len(mappable)) / len(target_protocols)
            
            if score >= min_score:
                logger.info(f"Found collaborator {agent.agent_id} with score {score:.2f}")
                collaborators.append(agent)
                
        return collaborators
