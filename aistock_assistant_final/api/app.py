# -*- coding: utf-8 -*-
"""
===================================
A股智能分析系统 - FastAPI应用
===================================

职责:
1. 提供RESTful API
2. 支持股票分析/市场数据/自选股管理
3. 配置管理和历史数据查询
4. CORS支持
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from .deps import get_data_manager, get_ai_analyzer, get_search_service, get_notification_service

logger = logging.getLogger(__name__)


app = FastAPI(title="A股智能助手API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StockAnalysisRequest(BaseModel):
    """股票分析请求"""
    stock_code: str
    period: str = "daily"


class MarketDataResponse(BaseModel):
    """市场数据响应"""
    indices: List[Dict[str, Any]]
    summary: Dict[str, Any]
    sectors: List[Dict[str, Any]]


class WatchlistItem(BaseModel):
    """自选股项"""
    code: str
    name: str
    add_time: str


class WatchlistResponse(BaseModel):
    """自选股列表响应"""
    watchlist: List[WatchlistItem]
    total: int


@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "A股智能助手API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "GET /api/v1/health": "健康检查",
            "GET /api/v1/stock/analyze": "股票分析",
            "GET /api/v1/market": "市场数据",
            "GET /api/v1/watchlist": "自选股管理",
            "POST /api/v1/watchlist": "添加自选股",
            "DELETE /api/v1/watchlist/{code}": "移除自选股",
            "POST /api/v1/notify": "发送通知"
        }
    }


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "API服务正常运行"}


@app.post("/api/v1/stock/analyze")
async def analyze_stock(request: StockAnalysisRequest, 
                   data_manager = Depends(get_data_manager),
                   ai_analyzer = Depends(get_ai_analyzer),
                   search_service = Depends(get_search_service)):
    """
    股票分析API
    """
    try:
        stock_data = data_manager.get_stock_history(request.stock_code, request.period)
        if not stock_data:
            raise HTTPException(status_code=404, detail="股票数据获取失败")

        news_context = ""
        if request.stock_code:
            news_results = search_service.search_news(f"{request.stock_code} 股票", max_results=5)
            if news_results:
                news_context = "\n".join([
                    f"- {item.get('title', '')}: {item.get('snippet', '')}"
                    for item in news_results
                ])

        analysis_result = ai_analyzer.analyze(
            stock_code=request.stock_code,
            stock_name=stock_data.get('name', ''),
            stock_data=stock_data,
            news_context=news_context
        )

        return {
            "success": analysis_result.success,
            "data": analysis_result.to_dict()
        }

    except Exception as e:
        logger.error(f"股票分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/market")
async def get_market_data(data_manager = Depends(get_data_manager)):
    """
    获取市场数据API
    """
    try:
        indices = data_manager.get_all_indices()
        market_summary = data_manager.get_market_summary()
        sector_rank = data_manager.get_sector_rank()
        fund_flow = data_manager.get_fund_flow()

        return MarketDataResponse(
            indices=indices,
            summary=market_summary,
            sectors=sector_rank[:20],
            fund_flow=fund_flow[:10]
        )

    except Exception as e:
        logger.error(f"获取市场数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/watchlist", response_model=WatchlistResponse)
async def get_watchlist(data_manager = Depends(get_data_manager)):
    """
    获取自选股列表API
    """
    try:
        watchlist_data = data_manager.get_watchlist_data()

        watchlist_items = []
        for stock in watchlist_data:
            watchlist_items.append(WatchlistItem(
                code=stock.get('code', ''),
                name=stock.get('name', ''),
                add_time=stock.get('add_time', '')
            ))

        return WatchlistResponse(
            watchlist=watchlist_items,
            total=len(watchlist_items)
        )

    except Exception as e:
        logger.error(f"获取自选股列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/watchlist")
async def add_to_watchlist(request: dict,
                            data_manager = Depends(get_data_manager)):
    """
    添加自选股API
    """
    try:
        stock_code = request.get('code', '')
        stock_name = request.get('name', None)

        success = data_manager.add_to_watchlist(stock_code, stock_name)

        if success:
            return {"success": True, "message": f"添加成功: {stock_code}"}
        else:
            raise HTTPException(status_code=400, detail="添加失败")

    except Exception as e:
        logger.error(f"添加自选股失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/watchlist/{code}")
async def remove_from_watchlist(code: str,
                                 data_manager = Depends(get_data_manager)):
    """
    移除自选股API
    """
    try:
        success = data_manager.remove_from_watchlist(code)

        if success:
            return {"success": True, "message": f"移除成功: {code}"}
        else:
            raise HTTPException(status_code=404, detail="股票不在自选股中")

    except Exception as e:
        logger.error(f"移除自选股失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/notify")
async def send_notification(request: dict,
                              notification_service = Depends(get_notification_service)):
    """
    发送通知API
    """
    try:
        title = request.get('title', '')
        message = request.get('message', '')

        success = notification_service.send(title, message)

        if success:
            return {"success": True, "message": "通知发送成功"}
        else:
            raise HTTPException(status_code=400, detail="通知发送失败")

    except Exception as e:
        logger.error(f"发送通知失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info("启动FastAPI服务器...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
