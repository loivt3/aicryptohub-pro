"""
On-Chain Data Service for AI Hub AI Engine
Fetches token metadata and holders from block explorer APIs
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


# Chain configurations - 23+ supported chains
# Etherscan API V2: Single key works for all EVM chains via chainid parameter
# Base URL: https://api.etherscan.io/v2/api?chainid={chain_id}

ETHERSCAN_V2_BASE = "https://api.etherscan.io/v2/api"

CHAINS = {
    # EVM Chains - All use Etherscan V2 with chainid parameter
    "ethereum": {
        "chain_id": 1,
        "name": "Ethereum",
        "native_symbol": "ETH",
        "type": "evm",
    },
    "bsc": {
        "chain_id": 56,
        "name": "BNB Smart Chain",
        "native_symbol": "BNB",
        "type": "evm",
    },
    "polygon": {
        "chain_id": 137,
        "name": "Polygon",
        "native_symbol": "MATIC",
        "type": "evm",
    },
    "arbitrum": {
        "chain_id": 42161,
        "name": "Arbitrum One",
        "native_symbol": "ETH",
        "type": "evm",
    },
    "base": {
        "chain_id": 8453,
        "name": "Base",
        "native_symbol": "ETH",
        "type": "evm",
    },
    "avalanche": {
        "chain_id": 43114,
        "name": "Avalanche C-Chain",
        "native_symbol": "AVAX",
        "type": "evm",
    },
    "optimism": {
        "chain_id": 10,
        "name": "Optimism",
        "native_symbol": "ETH",
        "type": "evm",
    },
    "fantom": {
        "chain_id": 250,
        "name": "Fantom Opera",
        "native_symbol": "FTM",
        "type": "evm",
    },
    "cronos": {
        "chain_id": 25,
        "name": "Cronos",
        "native_symbol": "CRO",
        "type": "evm",
    },
    "zksync": {
        "chain_id": 324,
        "name": "zkSync Era",
        "native_symbol": "ETH",
        "type": "evm",
    },
    "linea": {
        "chain_id": 59144,
        "name": "Linea",
        "native_symbol": "ETH",
        "type": "evm",
    },
    "scroll": {
        "chain_id": 534352,
        "name": "Scroll",
        "native_symbol": "ETH",
        "type": "evm",
    },
    "mantle": {
        "chain_id": 5000,
        "name": "Mantle",
        "native_symbol": "MNT",
        "type": "evm",
    },
    "gnosis": {
        "chain_id": 100,
        "name": "Gnosis Chain",
        "native_symbol": "xDAI",
        "type": "evm",
    },
    "celo": {
        "chain_id": 42220,
        "name": "Celo",
        "native_symbol": "CELO",
        "type": "evm",
    },
    "moonbeam": {
        "chain_id": 1284,
        "name": "Moonbeam",
        "native_symbol": "GLMR",
        "type": "evm",
    },
    "blast": {
        "chain_id": 81457,
        "name": "Blast",
        "native_symbol": "ETH",
        "type": "evm",
    },
    # Additional EVM chains supported by Etherscan V2
    "sepolia": {
        "chain_id": 11155111,
        "name": "Sepolia Testnet",
        "native_symbol": "ETH",
        "type": "evm",
    },
    "holesky": {
        "chain_id": 17000,
        "name": "Holesky Testnet",
        "native_symbol": "ETH",
        "type": "evm",
    },
    "polygon_zkevm": {
        "chain_id": 1101,
        "name": "Polygon zkEVM",
        "native_symbol": "ETH",
        "type": "evm",
    },
    "zora": {
        "chain_id": 7777777,
        "name": "Zora",
        "native_symbol": "ETH",
        "type": "evm",
    },
    
    # Non-EVM Chains (different API structure)
    "solana": {
        "chain_id": None,
        "name": "Solana",
        "api_url": "https://api.solscan.io",
        "native_symbol": "SOL",
        "type": "solana",
    },
    "tron": {
        "chain_id": None,
        "name": "TRON",
        "api_url": "https://apilist.tronscanapi.com/api",
        "native_symbol": "TRX",
        "type": "tron",
    },
    "sui": {
        "chain_id": None,
        "name": "Sui",
        "api_url": "https://suiscan.xyz/api",
        "native_symbol": "SUI",
        "type": "sui",
    },
    "aptos": {
        "chain_id": None,
        "name": "Aptos",
        "api_url": "https://api.aptoscan.com/api",
        "native_symbol": "APT",
        "type": "aptos",
    },
    "ton": {
        "chain_id": None,
        "name": "TON",
        "api_url": "https://tonapi.io/v2",
        "native_symbol": "TON",
        "type": "ton",
    },
    "near": {
        "chain_id": None,
        "name": "NEAR Protocol",
        "api_url": "https://api.nearblocks.io/v1",
        "native_symbol": "NEAR",
        "type": "near",
    },
}


class OnChainService:
    """Service for fetching on-chain data from block explorers - supports EVM and non-EVM chains"""
    
    # Rate limiting (5 requests per second for free tier)
    REQUEST_DELAY = 0.25
    
    def __init__(self, api_keys: Dict[str, str] = None):
        """
        Initialize on-chain service
        
        Args:
            api_keys: Dict of chain_slug -> api_key
        """
        self.api_keys = api_keys or {}
        self._last_request_time = 0
    
    async def _rate_limit(self):
        """Enforce rate limiting"""
        import time
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.REQUEST_DELAY:
            await asyncio.sleep(self.REQUEST_DELAY - elapsed)
        self._last_request_time = time.time()
    
    async def _evm_api_request(
        self,
        chain_slug: str,
        params: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Make API request to Etherscan V2 (unified endpoint for all EVM chains)"""
        chain = CHAINS.get(chain_slug)
        if not chain or chain.get("type") != "evm":
            return None
        
        # Use single Etherscan API key for all EVM chains
        etherscan_key = self.api_keys.get("etherscan", "") or self.api_keys.get("ethereum", "")
        if etherscan_key:
            params["apikey"] = etherscan_key
        
        # Add chainid for Etherscan V2
        params["chainid"] = chain["chain_id"]
        
        await self._rate_limit()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(ETHERSCAN_V2_BASE, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1":
                        return data.get("result")
                    else:
                        logger.warning(f"EVM API error: {data.get('message')}")
                        return None
                        
        except Exception as e:
            logger.error(f"EVM request failed: {e}")
        
        return None
    
    # ==================== SOLANA ====================
    
    async def _solana_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make request to Solscan API"""
        await self._rate_limit()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"accept": "application/json"}
                api_key = self.api_keys.get("solana", "")
                if api_key:
                    headers["token"] = api_key
                
                url = f"https://api.solscan.io{endpoint}"
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                    
        except Exception as e:
            logger.error(f"Solana request failed: {e}")
        
        return None
    
    async def get_solana_token_info(self, token_address: str) -> Optional[Dict[str, Any]]:
        """Get Solana token metadata"""
        data = await self._solana_request(f"/token/meta?tokenAddress={token_address}")
        
        if data:
            return {
                "chain": "solana",
                "contract_address": token_address,
                "name": data.get("name"),
                "symbol": data.get("symbol"),
                "decimals": data.get("decimals"),
                "total_supply": data.get("supply"),
                "holder_count": data.get("holder"),
            }
        
        return None
    
    async def get_solana_holders(self, token_address: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get top Solana token holders"""
        data = await self._solana_request(f"/token/holders?tokenAddress={token_address}&offset=0&size={limit}")
        
        holders = []
        if data and data.get("data"):
            for i, h in enumerate(data["data"][:limit], 1):
                holders.append({
                    "rank": i,
                    "address": h.get("owner"),
                    "balance": h.get("amount"),
                    "percentage": h.get("share"),
                })
        
        return holders
    
    # ==================== TRON ====================
    
    async def _tron_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make request to TronScan API"""
        await self._rate_limit()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"https://apilist.tronscanapi.com/api{endpoint}"
                response = await client.get(url)
                
                if response.status_code == 200:
                    return response.json()
                    
        except Exception as e:
            logger.error(f"Tron request failed: {e}")
        
        return None
    
    async def get_tron_token_info(self, contract_address: str) -> Optional[Dict[str, Any]]:
        """Get TRON token metadata"""
        data = await self._tron_request(f"/token_trc20?contract={contract_address}")
        
        if data and data.get("trc20_tokens"):
            token = data["trc20_tokens"][0]
            return {
                "chain": "tron",
                "contract_address": contract_address,
                "name": token.get("name"),
                "symbol": token.get("symbol"),
                "decimals": token.get("decimals"),
                "total_supply": token.get("total_supply_with_decimals"),
                "holder_count": token.get("holders_count"),
            }
        
        return None
    
    async def get_tron_holders(self, contract_address: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get top TRON token holders"""
        data = await self._tron_request(f"/token_trc20/holders?contract={contract_address}&start=0&limit={limit}")
        
        holders = []
        if data and data.get("data"):
            for i, h in enumerate(data["data"][:limit], 1):
                holders.append({
                    "rank": i,
                    "address": h.get("holder_address"),
                    "balance": h.get("balance"),
                    "percentage": h.get("percent"),
                })
        
        return holders
    
    # ==================== TON ====================
    
    async def _ton_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make request to TON API"""
        await self._rate_limit()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                api_key = self.api_keys.get("ton", "")
                headers = {}
                if api_key:
                    headers["X-API-Key"] = api_key
                
                url = f"https://tonapi.io/v2{endpoint}"
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                    
        except Exception as e:
            logger.error(f"TON request failed: {e}")
        
        return None
    
    async def get_ton_token_info(self, token_address: str) -> Optional[Dict[str, Any]]:
        """Get TON jetton metadata"""
        data = await self._ton_request(f"/jettons/{token_address}")
        
        if data:
            return {
                "chain": "ton",
                "contract_address": token_address,
                "name": data.get("metadata", {}).get("name"),
                "symbol": data.get("metadata", {}).get("symbol"),
                "decimals": data.get("metadata", {}).get("decimals"),
                "total_supply": data.get("total_supply"),
                "holder_count": data.get("holders_count"),
            }
        
        return None
    
    # ==================== NEAR ====================
    
    async def _near_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make request to NEAR Blocks API"""
        await self._rate_limit()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"https://api.nearblocks.io/v1{endpoint}"
                response = await client.get(url)
                
                if response.status_code == 200:
                    return response.json()
                    
        except Exception as e:
            logger.error(f"NEAR request failed: {e}")
        
        return None
    
    async def get_near_token_info(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get NEAR token metadata"""
        data = await self._near_request(f"/fts/{contract_id}")
        
        if data and data.get("contracts"):
            token = data["contracts"][0]
            return {
                "chain": "near",
                "contract_address": contract_id,
                "name": token.get("name"),
                "symbol": token.get("symbol"),
                "decimals": token.get("decimals"),
                "total_supply": token.get("total_supply"),
            }
        
        return None
    
    # ==================== UNIFIED METHODS ====================
    
    async def get_token_info(
        self,
        chain_slug: str,
        contract_address: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get token metadata - routes to correct chain handler
        """
        chain = CHAINS.get(chain_slug)
        if not chain:
            logger.error(f"Unknown chain: {chain_slug}")
            return None
        
        chain_type = chain.get("type", "evm")
        
        # Route to specific chain handler
        if chain_type == "solana":
            return await self.get_solana_token_info(contract_address)
        elif chain_type == "tron":
            return await self.get_tron_token_info(contract_address)
        elif chain_type == "ton":
            return await self.get_ton_token_info(contract_address)
        elif chain_type == "near":
            return await self.get_near_token_info(contract_address)
        else:
            # EVM chains
            supply_result = await self._evm_api_request(chain_slug, {
                "module": "stats",
                "action": "tokensupply",
                "contractaddress": contract_address,
            })
            
            if not supply_result:
                return None
            
            info_result = await self._evm_api_request(chain_slug, {
                "module": "token",
                "action": "tokeninfo",
                "contractaddress": contract_address,
            })
            
            token_info = {
                "contract_address": contract_address,
                "chain": chain_slug,
                "total_supply": supply_result,
            }
            
            if info_result and isinstance(info_result, list) and len(info_result) > 0:
                info = info_result[0]
                token_info.update({
                    "name": info.get("tokenName"),
                    "symbol": info.get("symbol"),
                    "decimals": int(info.get("divisor", 18)),
                    "holder_count": int(info.get("holdersCount", 0)),
                })
            
            return token_info
    
    async def get_top_holders(
        self,
        chain_slug: str,
        contract_address: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get top token holders - routes to correct chain handler"""
        chain = CHAINS.get(chain_slug)
        if not chain:
            return []
        
        chain_type = chain.get("type", "evm")
        
        if chain_type == "solana":
            return await self.get_solana_holders(contract_address, limit)
        elif chain_type == "tron":
            return await self.get_tron_holders(contract_address, limit)
        else:
            # EVM chains - requires Pro API
            result = await self._evm_api_request(chain_slug, {
                "module": "token",
                "action": "tokenholderlist",
                "contractaddress": contract_address,
                "page": 1,
                "offset": limit,
            })
            
            if result and isinstance(result, list):
                holders = []
                for i, holder in enumerate(result[:limit], 1):
                    holders.append({
                        "rank": i,
                        "address": holder.get("TokenHolderAddress"),
                        "balance": holder.get("TokenHolderQuantity"),
                        "percentage": None,
                    })
                return holders
            
            return []
    
    async def get_token_balance(
        self,
        chain_slug: str,
        contract_address: str,
        wallet_address: str,
    ) -> Optional[str]:
        """Get token balance for a specific wallet"""
        chain = CHAINS.get(chain_slug)
        if not chain:
            return None
        
        if chain.get("type") == "evm":
            return await self._evm_api_request(chain_slug, {
                "module": "account",
                "action": "tokenbalance",
                "contractaddress": contract_address,
                "address": wallet_address,
                "tag": "latest",
            })
        
        # For non-EVM, would need specific implementation
        return None
    
    async def get_native_balance(
        self,
        chain_slug: str,
        wallet_address: str,
    ) -> Optional[str]:
        """Get native token balance (ETH, SOL, etc.)"""
        chain = CHAINS.get(chain_slug)
        if not chain:
            return None
        
        if chain.get("type") == "evm":
            return await self._evm_api_request(chain_slug, {
                "module": "account",
                "action": "balance",
                "address": wallet_address,
                "tag": "latest",
            })
        elif chain.get("type") == "solana":
            data = await self._solana_request(f"/account?address={wallet_address}")
            if data:
                return str(data.get("lamports", 0))
        
        return None
    
    def get_supported_chains(self) -> List[Dict[str, Any]]:
        """Get list of supported chains"""
        return [
            {
                "slug": slug,
                "name": chain["name"],
                "chain_id": chain["chain_id"],
                "native_symbol": chain["native_symbol"],
                "type": chain.get("type", "evm"),
                "has_api_key": bool(self.api_keys.get(slug)),
            }
            for slug, chain in CHAINS.items()
        ]


# Singleton
_onchain_service: Optional[OnChainService] = None


def get_onchain_service() -> OnChainService:
    """Get on-chain service singleton"""
    global _onchain_service
    if _onchain_service is None:
        from config import get_settings
        settings = get_settings()
        
        # Load API keys from settings
        api_keys = {}
        if hasattr(settings, 'etherscan_api_key') and settings.etherscan_api_key:
            api_keys["ethereum"] = settings.etherscan_api_key
        if hasattr(settings, 'bscscan_api_key') and settings.bscscan_api_key:
            api_keys["bsc"] = settings.bscscan_api_key
        if hasattr(settings, 'polygonscan_api_key') and settings.polygonscan_api_key:
            api_keys["polygon"] = settings.polygonscan_api_key
        
        _onchain_service = OnChainService(api_keys)
    
    return _onchain_service

