import glob
import json
import os
from datetime import datetime
from typing import Dict, Any, List

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

# Debug-mode NDJSON log path/constants
DEBUG_LOG_PATH = r"c:\Users\vinay\OneDrive\Desktop\core\bse_500\.cursor\debug.log"
SESSION_ID = "debug-session"


def _agent_log(hypothesis_id: str, location: str, message: str, data: Dict[str, Any]):
    payload = {
        "sessionId": SESSION_ID,
        "runId": "prefill",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(datetime.utcnow().timestamp() * 1000),
    }
    try:
        # region agent log
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as _log:
            _log.write(json.dumps(payload) + "\n")
        # endregion
    except Exception:
        pass


def _load_market_df() -> pd.DataFrame:
    try:
        df = pd.read_csv("MarketWatch.csv")
        _agent_log("H3", "llm_parser_gemini.py:_load_market_df", "marketwatch_loaded", {"rows": len(df)})
        return df
    except FileNotFoundError:
        _agent_log("H3", "llm_parser_gemini.py:_load_market_df", "marketwatch_missing", {})
        return pd.DataFrame()


def load_text_data() -> Dict[str, str]:
    data: Dict[str, str] = {}
    txt_files = glob.glob("*.txt")
    _agent_log("H3", "llm_parser_gemini.py:load_text_data", "txt_scan", {"count": len(txt_files)})
    for file in txt_files:
        company_name = os.path.basename(file).split("_")[0].upper()
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        data[company_name] = data.get(company_name, "") + "\n" + content
    return data


PROMPT_TEMPLATE = """
You are a financial data extraction LLM.

From the following text (which may contain financials, company descriptions, exports, or supply chain info),
extract and summarize the key company data.

Return ONLY a JSON object with these fields:
- company_name
- sector
- revenue
- net_profit
- EPS
- PAT
- key_products
- export_countries
- supply_chain_summary
- risk_factors
- highlights

TEXT:
{company_text}
"""


def configure_gemini():
    load_dotenv()
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        _agent_log("H3", "llm_parser_gemini.py:configure_gemini", "missing_api_key", {})
        raise EnvironmentError("GOOGLE_API_KEY is not set")
    genai.configure(api_key=api_key)
    _agent_log("H3", "llm_parser_gemini.py:configure_gemini", "configured", {})


def generate_company_payload(company: str, text: str, sector_hint: str = "") -> Dict[str, Any]:
    prompt = PROMPT_TEMPLATE.format(company_text=text + f"\n\nKnown sector: {sector_hint}")
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    content = response.text.strip()
    json_str = content.strip("```json").strip("```").strip()
    parsed = json.loads(json_str)
    _agent_log("H4", "llm_parser_gemini.py:generate_company_payload", "llm_response", {"company": company, "keys": list(parsed.keys())})
    return parsed


def process_all_companies(run_id: str = "prefill") -> List[Dict[str, Any]]:
    configure_gemini()
    market_df = _load_market_df()
    text_data = load_text_data()
    output_data: List[Dict[str, Any]] = []
    _agent_log("H4", "llm_parser_gemini.py:process_all_companies", "start", {"runId": run_id, "companies": list(text_data.keys())})

    for company, text in tqdm(text_data.items(), desc="Processing Companies"):
        try:
            sector = ""
            if not market_df.empty and "Security Name" in market_df.columns:
                match = market_df[market_df["Security Name"].str.upper().str.contains(company, na=False)]
                if not match.empty and "Industry" in match.columns:
                    sector = match["Industry"].iloc[0]

            payload = generate_company_payload(company, text, sector)
            output_data.append(payload)
            print(f"✅ Parsed {company}")
        except Exception as e:
            print(f"❌ Error processing {company}: {e}")
            _agent_log("H4", "llm_parser_gemini.py:process_all_companies", "company_error", {"company": company, "error": str(e)})

    if output_data:
        final_df = pd.DataFrame(output_data)
        final_df.to_csv("Parsed_Company_Data.csv", index=False)
        print("\n✅ Extraction completed. Saved to Parsed_Company_Data.csv")
    else:
        print("\n⚠️ No valid results generated.")

    _agent_log("H4", "llm_parser_gemini.py:process_all_companies", "end", {"runId": run_id, "count": len(output_data)})
    return output_data


def process_single_company(company: str, run_id: str = "prefill") -> Dict[str, Any]:
    configure_gemini()
    market_df = _load_market_df()
    text_data = load_text_data()
    normalized = company.strip().upper()
    matched_text = ""

    # Combine any text data matching the company prefix
    for key, txt in text_data.items():
        if normalized in key:
            matched_text += txt + "\n"

    if not matched_text:
        _agent_log("H4", "llm_parser_gemini.py:process_single_company", "no_text_found", {"company": normalized})
        raise ValueError(f"No text data found for {company}")

    sector = ""
    if not market_df.empty and "Security Name" in market_df.columns:
        match = market_df[market_df["Security Name"].str.upper().str.contains(normalized, na=False)]
        if not match.empty and "Industry" in match.columns:
            sector = match["Industry"].iloc[0]

    _agent_log("H4", "llm_parser_gemini.py:process_single_company", "start", {"company": normalized, "runId": run_id})
    payload = generate_company_payload(normalized, matched_text, sector)
    _agent_log("H4", "llm_parser_gemini.py:process_single_company", "end", {"company": normalized, "runId": run_id})
    return payload


if __name__ == "__main__":
    process_all_companies()
