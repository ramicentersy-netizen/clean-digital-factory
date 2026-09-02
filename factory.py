import os
import json
from datetime import datetime

class DigitalProductFactory:
    def __init__(self, output_dir="products/generated_outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_top_demand_product(self):
        """
        توليد مواصفات المنتج الأكثر طلباً: نظام إدارة المستقلين
        """
        product_spec = {
            "product_id": f"prod_freelance_hub_{int(datetime.now().timestamp())}",
            "niche": "Remote Work & Freelancer Productivity",
            "title": "The Ultimate Freelancer Client & Project Hub (Notion Template)",
            "description": "An all-in-one workspace designed for freelancers to track clients, manage active projects, monitor invoices, and organize daily tasks seamlessly.",
            "target_audience": "Freelancers, Remote Workers, Solo-Entrepreneurs",
            "price_usd": 9.99,
            "components": [
                "Client Relationship Manager (CRM)",
                "Project & Task Kanban Board",
                "Invoice & Income Tracker",
                "Daily Productivity Planner"
            ],
            "status": "Ready for Sales Page Generation",
            "created_at": datetime.now().isoformat()
        }
        
        file_path = os.path.join(self.output_dir, f"{product_spec['product_id']}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(product_spec, f, ensure_ascii=False, indent=4)
            
        print(f"✅ تم بنجاح توليد مواصفات المنتج: {product_spec['title']}")
        return product_spec

if __name__ == "__main__":
    factory = DigitalProductFactory()
    factory.generate_top_demand_product()