
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Literal, Dict, Any

import pandas as pd


Category = Literal["financial", "esg", "other"]


@dataclass
class KPI:
    name: str
    category: Category
    value: float | None
    unit: str
    year: int
    description: str
    source: str
    chunk_ids: list[int]
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Convert list to a compact string for display
        d["chunk_ids"] = ", ".join(map(str, self.chunk_ids))
        return d


# -------------------------------------------------
# DEFINE YOUR KPIs HERE
# -------------------------------------------------

def _build_kpis() -> List[KPI]:
    kpis: List[KPI] = []

    # -------- FINANCIAL METRICS (replace) --------
    kpis.append(KPI(
        name="Revenue",
        category="financial",
        value=None,
        unit="€ bn",
        year=2024,
        description="Total revenue for FY24.",
        source="factset_financials_clean.txt",
        chunk_ids=[0],
        notes="Replace value and chunk_ids with actual data."
    ))

    kpis.append(KPI(
        name="EBITDA",
        category="financial",
        value=None,
        unit="€ bn",
        year=2024,
        description="EBITDA for FY24.",
        source="factset_financials_clean.txt",
        chunk_ids=[0],
    ))

    # -------- ESG METRICS--------

    kpis.append(KPI(
        name="Total GHG emissions (Scope 1+2+3)",
        category="esg",
        value=4_119_954,
        unit="tCO2e",
        year=2024,
        description=(
            "Total greenhouse gas emissions for FY24 across Scope 1, 2 and 3."
        ),
        source="factset_esg_clean.txt",
        chunk_ids=[0],
        notes="Sum of Scope 1 (116,092), Scope 2 (475,555) and Scope 3 (3,528,307) tCO2e."
    ))

    kpis.append(KPI(
        name="Scope 1 emissions",
        category="esg",
        value=116_092,
        unit="tCO2e",
        year=2024,
        description="Direct Scope 1 emissions from owned or controlled sources.",
        source="factset_esg_clean.txt",
        chunk_ids=[0],
        notes="Intensity: 0.9499 tCO2e per EUR million EVIC."
    ))

    kpis.append(KPI(
        name="Scope 2 emissions (market-based)",
        category="esg",
        value=475_555,
        unit="tCO2e",
        year=2024,
        description="Scope 2 emissions from purchased energy (market-based).",
        source="factset_esg_clean.txt",
        chunk_ids=[0],
        notes="Intensity: 3.8909 tCO2e per EUR million EVIC."
    ))

    kpis.append(KPI(
        name="Scope 3 emissions",
        category="esg",
        value=3_528_307,
        unit="tCO2e",
        year=2024,
        description="Scope 3 value-chain emissions (indirect).",
        source="factset_esg_clean.txt",
        chunk_ids=[0],
        notes="Intensity: 28.8683 tCO2e per EUR million EVIC."
    ))

    return kpis


# Precompute once
_ALL_KPIS: List[KPI] = _build_kpis()


# -------------------------------------------------
# PUBLIC HELPERS
# -------------------------------------------------

def get_kpis(category: Category | None = None) -> list[KPI]:
    """
    Return KPI objects, optionally filtered by category.
    """
    if category is None:
        return list(_ALL_KPIS)
    return [k for k in _ALL_KPIS if k.category == category]


def get_kpis_df(category: Category | None = None) -> pd.DataFrame:
    """
    Return KPIs as a pandas DataFrame for easy display in notebooks / Streamlit.
    """
    kpis = get_kpis(category)
    return pd.DataFrame([k.to_dict() for k in kpis])
