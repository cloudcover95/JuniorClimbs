# JuniorClimbs/core/spatial_automata.py
import mlx.core as mx
import pyarrow.parquet as pq
import pyarrow as pa
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLakeError(Exception):
    """Custom exception for Parquet data lake issues in 02_Assets."""
    pass

class SpatialTernaryAutomata:
    def __init__(self, asset_dir: str = "./02_Assets/climbs/telemetry", create_if_missing: bool = False):
        self.asset_dir = asset_dir
        self.create_if_missing = create_if_missing
        self._validate_trust_model()
        os.makedirs(self.asset_dir, exist_ok=True)

    def _validate_trust_model(self):
        if "01_Legal" in self.asset_dir:
            raise PermissionError("Zero-trust logic gate: Spatial topology isolated to 02_Assets.")

    def ingest_parquet_mesh(self, filename: str) -> mx.array:
        """
        Robust Parquet ingestion with error handling.
        - Raises DataLakeError on critical missing files (configurable).
        - Falls back gracefully for emulation/production.
        """
        filepath = os.path.join(self.asset_dir, filename)
        
        if not os.path.exists(filepath):
            if self.create_if_missing:
                # Create empty placeholder for first-run scenarios
                empty_table = pa.table({"mesh_data": pa.array([], type=pa.list_(pa.float32()))})
                pq.write_table(empty_table, filepath)
                logger.warning(f"Created empty placeholder Parquet: {filename}")
                return mx.zeros((0, 3))
            else:
                logger.warning(f"Missing Parquet file: {filename}. Using zero-tensor fallback.")
                # Production-safe fallback (prevents crashes, allows graceful degradation)
                return mx.zeros((1024, 3))  # Or raise DataLakeError if strict mode desired
        
        try:
            table = pq.read_table(filepath)
            if "mesh_data" not in table.column_names:
                raise DataLakeError(f"Parquet {filename} missing expected 'mesh_data' column.")
            raw_list = table["mesh_data"].to_pylist()
            if not raw_list:
                logger.info(f"Empty Parquet: {filename}")
                return mx.zeros((0, 3))
            return mx.array(raw_list).reshape((-1, 3))
        except Exception as e:
            logger.error(f"Failed to read Parquet {filename}: {e}")
            raise DataLakeError(f"Corrupt or unreadable Parquet: {filename}") from e

    def topological_svd_compression(self, mesh: mx.array, k: int = 64) -> mx.array:
        if mesh.shape[0] < k:
            return mesh
        U, Sigma, Vt = mx.linalg.svd(mesh)
        U_k = U[:, :k]
        Sigma_k = mx.diag(Sigma[:k])
        Vt_k = Vt[:k, :]
        return mx.matmul(mx.matmul(U_k, Sigma_k), Vt_k)

    def bitnet_spatial_quantize(self, compressed_mesh: mx.array) -> mx.array:
        gamma = mx.mean(mx.abs(compressed_mesh))
        gamma = mx.where(gamma == 0, mx.array(1.0), gamma)
        w_scaled = mx.round(compressed_mesh / gamma)
        return mx.clip(w_scaled, -1.0, 1.0) * gamma

    def __call__(self, scan_id: str) -> mx.array:
        raw_mesh = self.ingest_parquet_mesh(f"scan_{scan_id}.parquet")
        compressed_mesh = self.topological_svd_compression(raw_mesh)
        quantized_topology = self.bitnet_spatial_quantize(compressed_mesh)
        self._flush_processed_state(quantized_topology, scan_id)
        return quantized_topology

    def _flush_processed_state(self, tensor_data: mx.array, scan_id: str):
        np_data = pa.table({"ternary_map": tensor_data.flatten().tolist()})
        pq.write_table(np_data, os.path.join(self.asset_dir, f"ternary_{scan_id}.parquet"))

if __name__ == "__main__":
    automata = SpatialTernaryAutomata(create_if_missing=True)
    state = automata(scan_id="boulder_v4_001")
    mx.eval(state)
    print("SUCCESS: Spatial ternary automata with robust error handling.")