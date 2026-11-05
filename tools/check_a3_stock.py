"""Read-only JLCPCB public stock and assembly-process check for the two Rev A3 prototype jobs."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

CATALOG = Path(__file__).resolve().parents[1] / "hardware/RevA3/catalog.json"
HEADERS = {"User-Agent":"Mozilla/5.0", "Accept":"*/*", "Origin":"https://jlcpcb.com",
           "Referer":"https://jlcpcb.com/parts", "Content-Type":"application/json"}

def get(url, payload=None):
    request=urllib.request.Request(url, data=json.dumps(payload).encode() if payload else None, headers=HEADERS)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request,timeout=30) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code not in (429,502,503,504) or attempt==3:
                raise
            time.sleep(2**attempt+1)

def field(page, label):
    entry=re.search(re.escape(label)+r"</dt>\s*<dd[^>]*>(.*?)</dd>",page,flags=re.S)
    if not entry:
        raise ValueError(f"Missing part-detail field {label}")
    return " ".join(html.unescape(re.sub("<[^>]+>"," ",entry[1])).split())

def check(endpoint, item):
    code,expected=item
    payload={"keyword":code,"currentPage":1,"pageSize":25,"searchSource":"search","stockFlag":False}
    result=json.loads(get(endpoint,payload))
    page=result["data"]["componentPageInfo"]["list"]
    row=next(r for r in page if r["componentCode"]==code and r["componentModelEn"]==expected["mpn"])
    detail=get("https://jlcpcb.com/partdetail/"+row["urlSuffix"]).decode()
    method=field(detail,"Assembly Type")
    service=field(detail,"PCBA Type")
    available=max(0,min(row["stockCount"],row["canPresaleNumber"]))
    required=0
    for job in expected["jobs"].values():
        fit=job["fit"]
        reserve=max(5,row["lossNumber"] or 0,-(-3*fit//100))
        required+=max(fit+reserve,row["leastPatchNumber"] or 0)
    return {"code":code,"mpn":row["componentModelEn"],"verified_utc":datetime.now(timezone.utc).isoformat(),
            "stock":row["stockCount"],"can_presale":row["canPresaleNumber"],"available":available,
            "loss":row["lossNumber"],"minimum_patch":row["leastPatchNumber"],"required":required,
            "placement":method,"service":service,"url":"https://jlcpcb.com/partdetail/"+row["urlSuffix"],
            "passes":available>=required and method==expected["placement"] and "Standard" in service}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,help="Optional separate JSON report")
    args=parser.parse_args()
    data=json.loads(CATALOG.read_text(encoding="utf-8"))
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows=list(pool.map(lambda item:check(data["endpoint"],item),sorted(data["components"].items())))
    if args.output:
        args.output.write_text(json.dumps(rows,indent=2)+"\n",encoding="utf-8")
    failed=[r for r in rows if not r["passes"]]
    for row in failed:
        print(row["code"],row["mpn"],"required",row["required"],"available",row["available"],row["placement"])
    print(f"{len(rows)-len(failed)}/{len(rows)} exact JLCPCB stock and process checks passed.")
    raise SystemExit(bool(failed))
