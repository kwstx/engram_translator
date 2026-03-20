import axios from 'axios';

/**
 * MiroFish Swarm Bridge for Engram
 * 
 * A self-contained module to pipe inter-agent messages and live external data
 * directly into a running MiroFish swarm simulation.
 * 
 * Usage:
 * const bridge = MiroFishBridge('http://localhost:5001');
 * await bridge.pipe('agent-1', 'A2A', { seed_text: '...', num_agents: 1000 });
 */
export const MiroFishBridge = (baseUrl = 'http://localhost:5001') => {
  /**
   * Pipe data into MiroFish Swarm (Seed Injection)
   * Wraps raw text seeds and optinal agent counts for the MiroFish bridge endpoint.
   */
  const pipe = async (agentId: string, protocol: string, payload: { seed_text: string; num_agents?: number }, swarmId = 'default') => {
    const response = await axios.post(`${baseUrl}/api/v1/mirofish/pipe`, {
      agent_id: agentId,
      protocol: protocol,
      payload: payload,
      swarm_id: swarmId,
    });
    return response.data;
  };

  /**
   * God's Eye Injection
   * Injects live external events (prices, messages, signals) mid-simulation.
   */
  const godsEye = async (swarmId: string, contextObjects: any[]) => {
    const response = await axios.post(`${baseUrl}/api/v1/mirofish/gods-eye`, {
      swarm_id: swarmId,
      context_objects: contextObjects,
    });
    return response.data;
  };

  /**
   * Engram Message Bus Subscriber (Placeholder)
   * This handles inter-agent routing by subscribing to the message bus
   * and piping relevant messages to the swarm.
   */
  const subscribeToRouting = (subscriberUtility: any, agentId: string) => {
    if (!subscriberUtility) {
      console.warn('Engram message bus subscriber utility not found. Please provide one for inter-agent routing.');
      return;
    }

    // Example of how it would hook into an existing subscriber pattern
    subscriberUtility.subscribe(agentId, async (message: any) => {
      console.log(`[MiroFish Bridge] Routing message from ${agentId} to swarm...`);
      await pipe(agentId, message.protocol || 'MCP', {
        seed_text: typeof message.payload === 'string' ? message.payload : JSON.stringify(message.payload),
        num_agents: message.num_agents || 1000
      });
    });
  };

  return {
    pipe,
    godsEye,
    subscribeToRouting,
    baseUrl
  };
};

// Export as default for one-line imports
export default MiroFishBridge;
