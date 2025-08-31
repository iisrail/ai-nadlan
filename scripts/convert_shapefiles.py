# scripts/convert_shapefiles.py
from pathlib import Path
import sys
import warnings

import geopandas as gpd

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parents[1]  # project root
IN_DIR = ROOT / "data" / "shape"
OUT_DIR = ROOT / "data" / "exports"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def read_shapefile(path: Path) -> gpd.GeoDataFrame:
    """
    Try common Hebrew encodings; prefer fiona engine (stable with .dbf).
    """
    tries = [
        dict(engine="fiona", encoding="cp1255"),
        dict(engine="fiona", encoding="iso-8859-8"),
        dict(engine="fiona"),
    ]
    last_err = None
    for kw in tries:
        try:
            return gpd.read_file(path, **kw)
        except Exception as e:
            last_err = e
    raise last_err


def ensure_wgs84(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Reproject to EPSG:4326 (lon/lat). If CRS missing, leave as-is but warn.
    """
    if gdf.crs is None:
        print("  [!] No CRS found; leaving as-is (consider setting gdf.set_crs(...))")
        return gdf
    try:
        epsg = gdf.crs.to_epsg()
    except Exception:
        epsg = None
    if epsg == 4326:
        return gdf
    try:
        return gdf.to_crs(4326)
    except Exception as e:
        print(f"  [!] Reprojection failed: {e}; keeping original CRS.")
        return gdf


def add_features(gdf_orig: gpd.GeoDataFrame, gdf_ll: gpd.GeoDataFrame):
    """
    - area_m2 from original if in a projected (meter) CRS
    - centroid as numeric lon/lat columns (avoid extra geometry columns)
    """
    # area in m² (only if original CRS is projected, not geographic)
    try:
        epsg = gdf_orig.crs.to_epsg() if gdf_orig.crs is not None else None
    except Exception:
        epsg = None
    if epsg and epsg != 4326:
        try:
            gdf_orig["area_m2"] = gdf_orig.geometry.area
        except Exception:
            print("  [i] area_m2 not added (geometry invalid or CRS issue).")

    # centroid as lon/lat numbers
    try:
        cen = gdf_ll.geometry.centroid
        gdf_ll["centroid_lon"] = cen.x
        gdf_ll["centroid_lat"] = cen.y
    except Exception:
        pass

    return gdf_orig, gdf_ll


def export_layers(name: str, gdf_ll: gpd.GeoDataFrame):
    # ensure CRS is 4326 for GeoJSON
    if gdf_ll.crs is None or (gdf_ll.crs.to_epsg() != 4326):
        try:
            gdf_ll = gdf_ll.set_crs(4326, allow_override=True)
        except Exception:
            pass

    geojson_path = OUT_DIR / f"{name}.geojson"
    parquet_path = OUT_DIR / f"{name}.parquet"

    try:
        gdf_ll.to_file(geojson_path, driver="GeoJSON")
        print(f"  ✔ GeoJSON:  {geojson_path.name}")
    except Exception as e:
        print(f"  [!] GeoJSON export failed: {e}")

    try:
        gdf_ll.to_parquet(parquet_path, index=False)
        print(f"  ✔ Parquet:  {parquet_path.name}")
    except Exception as e:
        print(f"  [!] Parquet export failed: {e}")


def summarize(gdf_ll: gpd.GeoDataFrame):
    cols = list(gdf_ll.columns)
    print(f"  Rows: {len(gdf_ll)} | Columns: {len(cols)}")
    print(f"  CRS (LL): {gdf_ll.crs}")
    show = [c for c in cols if c.lower() in {
        "gush_num", "gush_suffi", "locality_n", "status_tex",
        "shape_area", "shape_len", "area_m2", "centroid_lon", "centroid_lat"
    }]
    if show:
        print("  Sample columns:", show)
    try:
        print(gdf_ll.head(2))
    except Exception:
        pass


def main():
    if not IN_DIR.exists():
        print(f"[ERROR] Input directory not found: {IN_DIR}")
        sys.exit(1)

    shp_files = sorted(IN_DIR.glob("*.shp"))
    if not shp_files:
        print(f"[ERROR] No .shp files in {IN_DIR}")
        sys.exit(1)

    print(f"Found {len(shp_files)} shapefile(s) in {IN_DIR}.\n")

    for shp in shp_files:
        name = shp.stem
        print(f"=== {name} ===")
        try:
            gdf = read_shapefile(shp)
            print(f"  Original CRS: {gdf.crs}")
            gdf_ll = ensure_wgs84(gdf)
            gdf, gdf_ll = add_features(gdf, gdf_ll)
            export_layers(name, gdf_ll)
            summarize(gdf_ll)
        except Exception as e:
            print(f"  [!] Failed to process {name}: {e}")
        print()


if __name__ == "__main__":
    main()
