from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FundFlowAnalyzer:
    """资金流向分析器"""

    @staticmethod
    def analyze_fund_flow(fund_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析资金流向

        Args:
            fund_data: 资金流向数据列表

        Returns:
            分析结果
        """
        try:
            if not fund_data:
                return {
                    "summary": "无数据",
                    "main_inflow": 0,
                    "main_outflow": 0,
                    "net_inflow": 0,
                    "trend": "无法判断"
                }

            df = pd.DataFrame(fund_data)

            # 主力资金流向
            main_net = df['main_net_inflow'].sum()
            super_large_net = df['super_large_net_inflow'].sum()
            large_net = df['large_net_inflow'].sum()
            medium_net = df['medium_net_inflow'].sum()
            small_net = df['small_net_inflow'].sum()

            # 净流入
            total_inflow = df[df['main_net_inflow'] > 0]['main_net_inflow'].sum()
            total_outflow = abs(df[df['main_net_inflow'] < 0]['main_net_inflow'].sum())
            net_inflow = total_inflow - total_outflow

            # 趋势分析
            trend = FundFlowAnalyzer._analyze_trend(df)

            # 资金异动股票
            abnormal_stocks = FundFlowAnalyzer._detect_abnormal(df)

            return {
                "summary": FundFlowAnalyzer._generate_summary(main_net, trend),
                "main_inflow": total_inflow,
                "main_outflow": total_outflow,
                "net_inflow": net_inflow,
                "trend": trend,
                "super_large_net": super_large_net,
                "large_net": large_net,
                "medium_net": medium_net,
                "small_net": small_net,
                "abnormal_stocks": abnormal_stocks,
                "top_inflow": FundFlowAnalyzer._get_top_stocks(df, 5, True),
                "top_outflow": FundFlowAnalyzer._get_top_stocks(df, 5, False)
            }
        except Exception as e:
            logger.error(f"资金流向分析失败: {e}")
            return {"error": str(e)}

    @staticmethod
    def _analyze_trend(df: pd.DataFrame) -> str:
        """分析资金流向趋势"""
        try:
            if len(df) < 5:
                return "数据不足"

            # 计算最近5天的资金流向
            recent_net = df['main_net_inflow'].tail(5).sum()

            # 计算整体趋势
            if recent_net > 0:
                if recent_net > df['main_net_inflow'].sum() * 0.1:
                    return "主力资金大幅流入，市场强势"
                else:
                    return "主力资金持续流入，市场偏强"
            elif recent_net < 0:
                if abs(recent_net) > abs(df['main_net_inflow'].sum()) * 0.1:
                    return "主力资金大幅流出，市场弱势"
                else:
                    return "主力资金持续流出，市场偏弱"
            else:
                return "资金流向平衡，市场震荡"
        except Exception as e:
            logger.error(f"分析资金流向趋势失败: {e}")
            return "无法判断"

    @staticmethod
    def _generate_summary(main_net: float, trend: str) -> str:
        """生成资金流向摘要"""
        try:
            if main_net > 100000000:  # 大于1亿
                return f"今日主力资金净流入{main_net/100000000:.2f}亿，{trend}"
            elif main_net < -100000000:
                return f"今日主力资金净流出{abs(main_net)/100000000:.2f}亿，{trend}"
            elif main_net > 0:
                return f"今日主力资金净流入{main_net/10000:.2f}万，{trend}"
            elif main_net < 0:
                return f"今日主力资金净流出{abs(main_net)/10000:.2f}万，{trend}"
            else:
                return f"今日主力资金流向平衡，{trend}"
        except Exception as e:
            logger.error(f"生成资金流向摘要失败: {e}")
            return "资金流向摘要生成失败"

    @staticmethod
    def _detect_abnormal(df: pd.DataFrame, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """检测资金异动股票"""
        try:
            if df.empty:
                return []

            # 计算标准差
            std = df['main_net_inflow'].std()
            mean = df['main_net_inflow'].mean()

            # 异常值：超过均值±2倍标准差
            abnormal = df[
                (df['main_net_inflow'] > mean + threshold * std) |
                (df['main_net_inflow'] < mean - threshold * std)
            ]

            abnormal_stocks = []
            for _, row in abnormal.iterrows():
                abnormal_stocks.append({
                    "code": row['code'],
                    "name": row['name'],
                    "main_net_inflow": row['main_net_inflow'],
                    "change_percent": row['change_percent'],
                    "type": "大幅流入" if row['main_net_inflow'] > 0 else "大幅流出"
                })

            return abnormal_stocks
        except Exception as e:
            logger.error(f"检测资金异动失败: {e}")
            return []

    @staticmethod
    def _get_top_stocks(df: pd.DataFrame, top_n: int = 10, 
                        inflow: bool = True) -> List[Dict[str, Any]]:
        """获取资金流入/流出最多的股票"""
        try:
            if df.empty:
                return []

            if inflow:
                sorted_df = df.sort_values('main_net_inflow', ascending=False)
            else:
                sorted_df = df.sort_values('main_net_inflow', ascending=True)

            top_stocks = []
            for _, row in sorted_df.head(top_n).iterrows():
                top_stocks.append({
                    "code": row['code'],
                    "name": row['name'],
                    "main_net_inflow": row['main_net_inflow'],
                    "change_percent": row['change_percent'],
                    "price": row['price']
                })

            return top_stocks
        except Exception as e:
            logger.error(f"获取资金流向排行失败: {e}")
            return []

    @staticmethod
    def analyze_stock_fund_flow(stock_code: str, fund_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析单只股票的资金流向

        Args:
            stock_code: 股票代码
            fund_history: 历史资金流向数据

        Returns:
            分析结果
        """
        try:
            if not fund_history:
                return {
                    "stock_code": stock_code,
                    "trend": "无数据",
                    "accumulation": 0,
                    "distribution": 0,
                    "signal": "无法判断"
                }

            df = pd.DataFrame(fund_history)

            # 计算累计流入/流出
            accumulation = df[df['main_net_inflow'] > 0]['main_net_inflow'].sum()
            distribution = abs(df[df['main_net_inflow'] < 0]['main_net_inflow'].sum())

            # 最近5天趋势
            recent_5d = df['main_net_inflow'].tail(5).sum()
            recent_10d = df['main_net_inflow'].tail(10).sum()

            # 资金流向信号
            signal = FundFlowAnalyzer._get_fund_signal(recent_5d, recent_10d, accumulation, distribution)

            return {
                "stock_code": stock_code,
                "trend": "资金持续流入" if recent_5d > 0 else "资金持续流出",
                "accumulation": accumulation,
                "distribution": distribution,
                "net_flow": accumulation - distribution,
                "recent_5d": recent_5d,
                "recent_10d": recent_10d,
                "signal": signal,
                "strength": abs(recent_5d) / 1000000  # 资金强度（百万）
            }
        except Exception as e:
            logger.error(f"分析股票资金流向失败 {stock_code}: {e}")
            return {"error": str(e)}

    @staticmethod
    def _get_fund_signal(recent_5d: float, recent_10d: float, 
                        accumulation: float, distribution: float) -> str:
        """获取资金流向信号"""
        try:
            if recent_5d > 0 and recent_10d > 0:
                if accumulation > distribution * 2:
                    return "资金大幅流入，强烈买入信号"
                else:
                    return "资金持续流入，买入信号"
            elif recent_5d < 0 and recent_10d < 0:
                if distribution > accumulation * 2:
                    return "资金大幅流出，卖出信号"
                else:
                    return "资金持续流出，卖出信号"
            elif recent_5d > 0 and recent_10d < 0:
                return "资金短期流入，中期流出，观望"
            elif recent_5d < 0 and recent_10d > 0:
                return "资金短期流出，中期流入，观望"
            else:
                return "资金流向平衡，观望"
        except Exception as e:
            logger.error(f"获取资金流向信号失败: {e}")
            return "无法判断"

    @staticmethod
    def analyze_sector_fund_flow(sector_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析板块资金流向

        Args:
            sector_data: 板块数据列表

        Returns:
            分析结果
        """
        try:
            if not sector_data:
                return {
                    "summary": "无数据",
                    "hot_sectors": [],
                    "cold_sectors": []
                }

            df = pd.DataFrame(sector_data)

            # 按资金流向排序
            df_sorted = df.sort_values('fund_flow', ascending=False)

            # 热门板块（资金流入前5）
            hot_sectors = []
            for _, row in df_sorted.head(5).iterrows():
                hot_sectors.append({
                    "name": row['name'],
                    "fund_flow": row['fund_flow'],
                    "change_percent": row['change_percent'],
                    "leading_stock": row['leading_stock']
                })

            # 冷门板块（资金流出前5）
            cold_sectors = []
            for _, row in df_sorted.tail(5).iterrows():
                cold_sectors.append({
                    "name": row['name'],
                    "fund_flow": row['fund_flow'],
                    "change_percent": row['change_percent'],
                    "leading_stock": row['leading_stock']
                })

            return {
                "summary": f"今日{len(hot_sectors)}个板块资金流入，{len(cold_sectors)}个板块资金流出",
                "hot_sectors": hot_sectors,
                "cold_sectors": cold_sectors,
                "total_inflow": df[df['fund_flow'] > 0]['fund_flow'].sum(),
                "total_outflow": abs(df[df['fund_flow'] < 0]['fund_flow'].sum())
            }
        except Exception as e:
            logger.error(f"分析板块资金流向失败: {e}")
            return {"error": str(e)}