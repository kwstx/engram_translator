export interface RouteOptions {
  apiKey?: string;
  secret?: string;
}

export type EngramAdapter = (
  message: string,
  options?: RouteOptions,
) => Promise<unknown>;

export interface EngramSDK {
  adapters: Record<string, EngramAdapter>;
  tradingTemplates: {
    platforms: string[];
    enable: (platform: string, config: any) => void;
    getConfigs: () => Record<string, any>;
  };
  routeTo: (
    target: string,
    message: string,
    options?: RouteOptions,
  ) => Promise<unknown>;
}

export const loadEngramConfig = (): EngramSDK => {
  const adapters: Record<string, EngramAdapter> = {};

  const tradingConfigs: Record<string, any> = {};
  const tradingTemplates = {
    platforms: ['binance', 'coinbase', 'robinhood', 'kalshi', 'stripe', 'paypal', 'feeds'],
    enable: (platform: string, config: any) => {
      tradingConfigs[platform.toLowerCase()] = config;
    },
    getConfigs: () => tradingConfigs,
  };

  return {
    adapters,
    tradingTemplates,
    routeTo: async (
      target: string,
      message: string,
      options?: RouteOptions,
    ) => {
      const platform = target.toLowerCase();
      if (tradingTemplates.platforms.includes(platform)) {
        // This would call the backend or a library that handles the heavy lifting
        console.log(`[Engram] Routing to trading template: ${platform}`);
        
        return { status: 'simulated', platform, message: 'Trading template routed' };
      }

      const adapter = adapters[platform];
      if (!adapter) {
        throw new Error(
          `[Engram] Unsupported adapter: "${target}". ` +
            `Available adapters: ${Object.keys(adapters).join(', ') || 'none'}`,
        );
      }
      return adapter(message, options);
    },
  };
};

