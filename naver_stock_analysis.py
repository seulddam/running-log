diff --git a//dev/null b/naver_stock_analysis.py
index 0000000000000000000000000000000000000000..b6818dc0f628269a7f037468cdb9c5609c9fef2d 100644
--- a//dev/null
+++ b/naver_stock_analysis.py
@@ -0,0 +1,73 @@
+import argparse
+import requests
+import pandas as pd
+
+
+NAVER_URL = "https://api.finance.naver.com/siseJson.naver"
+
+
+def fetch_price_history(stock_code: str, start: str, end: str, timeframe: str = "day") -> pd.DataFrame:
+    """Fetch price history from Naver Finance.
+
+    Args:
+        stock_code: Naver stock code, e.g. "005930".
+        start: Start date string in YYYYMMDD.
+        end: End date string in YYYYMMDD.
+        timeframe: "day" or "week" etc.
+
+    Returns:
+        DataFrame with Date and Close price columns.
+    """
+    params = {
+        "symbol": stock_code,
+        "requestType": 1,
+        "startTime": start,
+        "endTime": end,
+        "timeframe": timeframe,
+    }
+    res = requests.get(NAVER_URL, params=params)
+    res.raise_for_status()
+    data = res.json()
+    # Naver returns [[date, close, ...], ...]
+    if not data or len(data) <= 1:
+        return pd.DataFrame()
+    columns = data[0]
+    rows = data[1:]
+    df = pd.DataFrame(rows, columns=columns)
+    df['날짜'] = pd.to_datetime(df['날짜'])
+    return df[['날짜', '종가']]
+
+
+def compute_return(df: pd.DataFrame) -> float:
+    if df.empty:
+        return float('nan')
+    start_price = float(df['종가'].iloc[0])
+    end_price = float(df['종가'].iloc[-1])
+    return (end_price - start_price) / start_price
+
+
+def main():
+    parser = argparse.ArgumentParser(description="Naver Finance stock analysis")
+    parser.add_argument("codes", nargs='+', help="Stock codes to analyze")
+    parser.add_argument("--start", required=True, help="Start date YYYYMMDD")
+    parser.add_argument("--end", required=True, help="End date YYYYMMDD")
+    parser.add_argument("--amount", type=float, default=1000000, help="Investment amount")
+    parser.add_argument("--top", type=int, default=5, help="Number of top stocks to show")
+    args = parser.parse_args()
+
+    results = []
+    for code in args.codes:
+        df = fetch_price_history(code, args.start, args.end)
+        ret = compute_return(df)
+        if pd.notna(ret):
+            final_value = args.amount * (1 + ret)
+            results.append((code, ret, final_value))
+
+    results.sort(key=lambda x: x[1], reverse=True)
+    print("Rank\tCode\tReturn(%)\tFinal Value")
+    for idx, (code, ret, value) in enumerate(results[:args.top], 1):
+        print(f"{idx}\t{code}\t{ret * 100:.2f}\t{value:.2f}")
+
+
+if __name__ == "__main__":
+    main()
