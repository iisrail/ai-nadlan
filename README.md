# AI-Nadlan 🏠📊

Predicting and analyzing real estate prices in Israel using geospatial data.

---

## 📦 Setup

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/ai-nadlan.git
cd ai-nadlan

2. Install Miniconda (if not installed)

Download Miniconda
 for your OS.

 conda env create -f environment.yml
conda activate ai-nadlan


ai-nadlan/
├── data/
│   ├── shape/         # raw shapefiles (NOT in git; share via cloud/drive)
│   └── exports/       # derived GeoJSON/Parquet/HTML outputs
├── notebooks/
│   └── check_shapefile.ipynb   # exploration and visualization
├── scripts/
│   └── convert_shapefiles.py   # batch processor
├── environment.yml    # conda env spec
├── .gitignore
└── README.md


📊 Data

Raw shapefiles (from data.gov.il
) should be placed in data/shape/.

They are not tracked in Git (too large).

Share shapefiles separately (Google Drive, Dropbox, etc.).

▶️ Usage
Convert shapefiles to GeoJSON/Parquet
python scripts/convert_shapefiles.py


Outputs are saved to data/exports/.

Explore in notebook
jupyter notebook notebooks/check_shapefile.ipynb

Interactive map

The notebook generates data/exports/SHEET_K_map.html.
Open it in your browser to see parcel polygons, centroids, and attributes.

🤝 Collaboration Notes

Keep heavy raw data (data/shape/) out of Git.

Always use the shared Conda environment (ai-nadlan) to avoid version mismatches.

When adding new dependencies, update environment.yml so teammates can rebuild consistently.

📌 Requirements

Python 3.11

Miniconda

GIS stack: geopandas, fiona, gdal, pyproj, shapely, rtree, pyogrio

Analysis: scikit-learn, osmnx, matplotlib, pyarrow, tqdm, requests, jupyter