# JuniorClimbs/core/parquet_schema_evolution.py
import logging
import os
from typing import Any, Dict, Optional

import pyarrow as pa
import pyarrow.parquet as pq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLakeError(Exception):
    pass

BITNET_SPATIAL_SCHEMA_V2 = pa.schema([
    pa.field("data", pa.list_(pa.float32())),
    pa.field("gamma", pa.float32()),
    pa.field("version", pa.int32()),
    pa.field("plasticity_modulation", pa.float32(), nullable=True),
    pa.field("shape", pa.list_(pa.int64())),
])

def get_current_schema() -> pa.Schema:
    return BITNET_SPATIAL_SCHEMA_V2

def read_parquet_with_evolution(
    filepath: str,
    target_schema: Optional[pa.Schema] = None,
    required: bool = False
) -> Optional[pa.Table]:
    if not os.path.exists(filepath):
        if required:
            raise DataLakeError(f"Required Parquet missing: {filepath}")
        logger.warning(f"Optional Parquet missing: {filepath} — returning None")
        return None
    try:
        if target_schema is None:
            target_schema = get_current_schema()
        table = pq.read_table(filepath, schema=target_schema)
        logger.info(f"Read evolved Parquet {filepath} (schema v{target_schema.metadata.get(b'version', b'1')})")
        return table
    except Exception as e:
        logger.error(f"Schema evolution failed for {filepath}: {e}")
        if required:
            raise DataLakeError from e
        return None

def write_parquet_with_metadata(
    table: pa.Table,
    filepath: str,
    version: int = 2,
    extra_metadata: Optional[Dict[str, str]] = None
) -> None:
    metadata = {
        b"schema_version": str(version).encode(),
        b"bitnet_ternary": b"1.58",
        b"ecosystem": b"JuniorCloudllc",
    }
    if extra_metadata:
        metadata.update({k.encode(): v.encode() for k, v in extra_metadata.items()})
    schema_with_meta = table.schema.with_metadata(metadata)
    table = table.cast(schema_with_meta)
    pq.write_table(table, filepath)
    logger.info(f"Wrote evolved Parquet {filepath} (v{version})")

def bitnet_terraform_weights(
    weights: Any,
    gamma: float,
    plasticity_mod: Optional[float] = None,
    version: int = 2
) -> pa.Table:
    import mlx.core as mx
    if isinstance(weights, mx.array):
        flat = weights.flatten().tolist()
        shape = list(weights.shape)
    else:
        flat = list(weights)
        shape = [len(flat)] if not hasattr(weights, 'shape') else list(weights.shape)
    data = {
        "data": [flat],
        "gamma": [gamma],
        "version": [version],
        "plasticity_modulation": [plasticity_mod] if plasticity_mod is not None else [None],
        "shape": [shape],
    }
    table = pa.table(data)
    return table.cast(get_current_schema())

if __name__ == "__main__":
    print("Parquet schema evolution ready for BitNet terraforming.")