import os
import glob
import json

class UpsellAgent:
    def __init__(self, products_dir="products/generated_outputs"):
        self.products_dir = products_dir

    def find_latest_product(self):
        files = glob.glob(os.path.join(self.products_dir, "*.json"))
        if not files:
            return None
        return max(files, key=os.path.getctime)

    def generate_upsell_offer(self):
        """
        إنشاء عرض إضافي (Upsell/Cross-Sell) لزيادة قيمة الطلب ومتوسط الربح لكل عميل
        """
        print("💰 Upsell Agent: Generating high-value cross-sell & order bump offer...")
        
        latest_file = self.find_latest_product()
        if not latest_file:
            print("❌ Upsell Agent Error: No product found to attach upsell.")
            return False

        with open(latest_file, "r", encoding="utf-8") as f:
            product = json.load(f)

        upsell_data = {
            "upsell_title": "VIP AI Mastery Toolkit & Automation Scripts",
            "upsell_price_usd": 19.99,
            "benefit": "Accelerate your workflow with pre-built Python scripts and advanced AI prompts."
        }

        # ربط عرض الـ Upsell بملف المنتج الأساسي
        product["upsell_offer"] = upsell_data
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(product, f, ensure_ascii=False, indent=4)

        print(f"✅ Upsell Agent: Upsell offer attached successfully! ({upsell_data['upsell_title']} - ${upsell_data['upsell_price_usd']})")
        return True

if __name__ == "__main__":
    agent = UpsellAgent()
    agent.generate_upsell_offer()