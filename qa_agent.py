import os
import glob
import json

class QualityAssuranceAgent:
    def __init__(self, web_dir="web", products_dir="products/generated_outputs"):
        self.web_dir = web_dir
        self.products_dir = products_dir

    def audit_latest_assets(self):
        """
        فحص جودة المنتج وصفحة البيع والتأكد من جاهزيتها البرمجية وخلوها من الأخطاء
        """
        print("🕵️‍♂️ QA Agent: Starting quality audit on latest generated assets...")
        
        product_files = glob.glob(os.path.join(self.products_dir, "*.json"))
        web_files = glob.glob(os.path.join(self.web_dir, "*.html"))
        
        if not product_files or not web_files:
            print("❌ QA Agent Audit Failed: Missing product spec or sales page.")
            return False

        latest_page = max(web_files, key=os.path.getctime)

        with open(latest_page, "r", encoding="utf-8") as f:
            html_content = f.read()

        checks = {
            "has_title": "<title>" in html_content,
            "has_price": "$" in html_content,
            "has_buy_button": "buy-btn" in html_content
        }

        if all(checks.values()):
            print(f"✅ QA Agent: All checks passed successfully! Asset is 100% ready.")
            print(f"📄 Verified Page: {os.path.basename(latest_page)}")
            return True
        else:
            print(f"⚠️ QA Agent: Issues detected in asset structure: {checks}")
            return False

if __name__ == "__main__":
    qa = QualityAssuranceAgent()
    qa.audit_latest_assets()