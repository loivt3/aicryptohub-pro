"""
Portfolio CRUD Endpoints - Complete Implementation
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security import get_current_user
from app.services.database import DatabaseService, get_db_service

router = APIRouter()


class PortfolioHolding(BaseModel):
    coin_id: str
    symbol: Optional[str] = None
    name: Optional[str] = None
    image: Optional[str] = None
    amount: float
    buy_price: float
    current_price: Optional[float] = None
    value: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None


class PortfolioSummary(BaseModel):
    total_value: float
    total_invested: float
    total_pnl: float
    total_pnl_percent: float
    holdings_count: int


class AddHoldingRequest(BaseModel):
    coin_id: str
    amount: float
    buy_price: float


class UpdateHoldingRequest(BaseModel):
    amount: Optional[float] = None
    buy_price: Optional[float] = None


@router.get("", response_model=List[PortfolioHolding])
async def get_portfolio(
    current_user: dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service),
):
    """Get all portfolio holdings for current user"""
    holdings = db.get_portfolio(current_user["user_id"])
    return holdings


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(
    current_user: dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service),
):
    """Get portfolio summary with totals and PnL"""
    holdings = db.get_portfolio(current_user["user_id"])
    
    total_value = sum(h.get("value", 0) for h in holdings)
    total_invested = sum(float(h.get("amount", 0)) * float(h.get("buy_price", 0)) for h in holdings)
    total_pnl = total_value - total_invested
    total_pnl_percent = ((total_value / total_invested) - 1) * 100 if total_invested > 0 else 0
    
    return PortfolioSummary(
        total_value=total_value,
        total_invested=total_invested,
        total_pnl=total_pnl,
        total_pnl_percent=total_pnl_percent,
        holdings_count=len(holdings),
    )


@router.post("", response_model=PortfolioHolding, status_code=status.HTTP_201_CREATED)
async def add_portfolio_holding(
    request: AddHoldingRequest,
    current_user: dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service),
):
    """Add a new holding to portfolio"""
    success = db.add_holding(
        user_id=current_user["user_id"],
        coin_id=request.coin_id,
        amount=request.amount,
        buy_price=request.buy_price,
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add holding")
    
    return PortfolioHolding(
        coin_id=request.coin_id,
        symbol=request.coin_id.upper(),
        amount=request.amount,
        buy_price=request.buy_price,
    )


@router.put("/{coin_id}", response_model=PortfolioHolding)
async def update_portfolio_holding(
    coin_id: str,
    request: UpdateHoldingRequest,
    current_user: dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service),
):
    """Update an existing holding"""
    # Get existing to merge
    success = db.add_holding(
        user_id=current_user["user_id"],
        coin_id=coin_id,
        amount=request.amount or 0,
        buy_price=request.buy_price or 0,
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update holding")
    
    return PortfolioHolding(
        coin_id=coin_id,
        symbol=coin_id.upper(),
        amount=request.amount or 0,
        buy_price=request.buy_price or 0,
    )


@router.delete("/{coin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio_holding(
    coin_id: str,
    current_user: dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service),
):
    """Delete a holding from portfolio"""
    success = db.delete_holding(current_user["user_id"], coin_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete holding")
    
    return None


@router.get("/audit", response_model=dict)
async def audit_portfolio(
    current_user: dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service),
):
    """
    AI Portfolio Auditor
    Analyzes portfolio health, diversification, and risks.
    """
    from app.services.ai_hedge_fund import ai_hedge_fund_service
    
    # 1. Get Portfolio
    holdings = db.get_portfolio(current_user["user_id"])
    
    # 2. Run Audit
    audit_result = ai_hedge_fund_service.audit_portfolio(holdings)
    
    return audit_result


@router.get("/simulate", response_model=dict)
async def simulate_portfolio(
    btc_change: float = -10.0,
    current_user: dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db_service),
):
    """
    AI Stress Simulator
    Simulates portfolio performance based on BTC price change scenario.
    param btc_change: Percentage change of Bitcoin price (default -10%)
    """
    from app.services.ai_hedge_fund import ai_hedge_fund_service
    
    # 1. Get Portfolio
    holdings = db.get_portfolio(current_user["user_id"])
    
    # 2. Run Simulation
    simulation_result = ai_hedge_fund_service.simulate_stress(holdings, btc_change)
    
    return simulation_result
