# Giuseppe Vitolo - CV

One-page software engineering CVs, with editable content and a portable PDF generator.

- [English CV](Giuseppe_Vitolo_EN.pdf)
- [Danish CV](Giuseppe_Vitolo_CV.pdf)
- [Editable content](resume.json)
- [PDF generator](generate_cv.py)

## Generate the PDFs

Requires Python 3.10 or newer. No browser, system fonts or LaTeX installation is needed.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python generate_cv.py
```

Edit `resume.json`, then rerun the generator. Contact details are shared; English and Danish content is maintained separately. The original PDF filenames are preserved.

```sh
python generate_cv.py --language en
python generate_cv.py --language da --output-dir output/pdf
python generate_cv.py --data another_resume.json --output-dir output/pdf
```

The generator creates searchable PDF text and clickable links. It stops if a CV exceeds one A4 page, preserving the previous output instead of silently shrinking the text.

## Measurement context

Figures in the CV come from documented Pokoin project results, not estimates of customer adoption or revenue:

- **Home feed:** the September 29, 2026 load test used 8 concurrent requests. The baseline hit the Pi API directly; the optimized path used the live edge with caching and request coalescing. Median latency was 6.9 s before and 26 ms after; throughput was 1.3 and 284 requests/s. This compares the complete serving paths and is not a claim about uncached SQL or a Rust-only speedup.
- **Historical data:** 52,940,443 price observations, 951 archives, 32 monthly PostgreSQL partitions. Historical coverage is English and Japanese Pokemon, February 2024 through September 15, 2026; this is not all-game sales history.
- **Daily snapshot:** the September 30, 2026 snapshot contains 624,798 product/variant rows and 510,593 distinct products. These are provider catalog and price data, not active customers or completed sales.
- **Rust:** the verified production migration covers autocomplete. The CV does not claim that every Pokoin route has been migrated.
- **Kubernetes:** the CV describes configuration and failover work. Earlier four-pod load-test results are omitted because later deployment documentation reports a problem starting additional pods.
- **prduct:** the interactive Digital Product Passport assessment is a sprint prototype. The CV does not claim deployment of the production prduct platform, a production dataset size, or measured commercial uplift.

The prduct internship and independent Pokoin work use the year **2026** because exact start/end dates and the formal prduct job title were not available in the source material. Existing contact details, education and older employment dates are retained from the prior CVs.
