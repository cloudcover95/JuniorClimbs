# path: src/juniorclimbs/performance_report_generator.py
#!/usr/bin/env python3
"""
Performance Report Generator

Generates structured performance reports from multi-modal data.
Designed for production use in sports analytics and human performance.
"""

import logging
from typing import Any, Dict, Optional

try:
    from juniorhome.smart_llm_router import SmartLLMRouter
    HAS_ROUTER = True
except ImportError:
    HAS_ROUTER = False

logging.basicConfig(level=logging.INFO, format="[*] %(asctime)s - %(message)s")


class PerformanceReportGenerator:
    """
    Generates high-quality performance reports.
    """

    def __init__(self, llm_router: Optional[Any] = None):
        if HAS_ROUTER and llm_router is None:
            self.llm_router = SmartLLMRouter()
        else:
            self.llm_router = llm_router

        logging.info("PerformanceReportGenerator initialized")

    def generate_report(
        self,
        movement_data: Dict[str, Any],
        biometric_data: Optional[Dict[str, Any]] = None,
        session_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        combined = {
            "movement": movement_data,
        }
        if biometric_data:
            combined["biometrics"] = biometric_data
        if session_notes:
            combined["notes"] = session_notes

        prompt = f"""Create a professional performance report based on this data.

Data:
{combined}

Structure the report with:
1. Executive Summary
2. Key Strengths
3. Areas for Improvement
4. Specific Recommendations
5. Risk Assessment (if any)
"""

        if self.llm_router:
            result = self.llm_router.route(prompt, prefer_bitnet=False)
            return {
                "report": result.get("response", ""),
                "backend": result.get("backend", "unknown"),
                "data_used": combined,
            }

        return {"report": "No LLM available", "data_used": combined}

    def generate_quick_summary(self, data: Dict[str, Any]) -> str:
        prompt = f"Give a one-paragraph summary of this performance data:\n\n{data}"
        if self.llm_router:
            result = self.llm_router.route(prompt, prefer_bitnet=False)
            return result.get("response", "")
        return "No LLM available"
