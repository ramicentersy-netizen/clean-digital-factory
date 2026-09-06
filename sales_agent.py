import os
import glob
import json
import time

class SalesPageAgent:
    def __init__(self, products_dir="products/generated_outputs", web_dir="web"):
        self.products_dir = products_dir
        self.web_dir = web_dir
        os.makedirs(web_dir, exist_ok=True)

    def find_latest_product(self):
        files = glob.glob(os.path.join(self.products_dir, "*.json"))
        if not files:
            return None
        return max(files, key=os.path.getctime)

    def generate_sales_page(self, target_file=None):
        """
        توليد صفحة بيع احترافية مصممة للتحويل ومربوطة مباشرة ببوت تيليجرام للدفع والتسليم الفوري
        """
        print("🌐 Sales Agent: Building high-converting sales page with Telegram Bot integration...")
        
        latest_file = target_file if target_file else self.find_latest_product()
        if not latest_file:
            print("❌ Sales Agent Error: No product spec found.")
            return False

        with open(latest_file, "r", encoding="utf-8-sig") as f:
            product = json.load(f)

        # رابط بوت تيليجرام المباشر للتسليم الفوري
        telegram_bot_url = "https://t.me/RamiHasanDigitalStore_bot"
        usdt_wallet_address = "TL3BavN5gnMFqW2xjdnQDJRhc2n6spEFhK"

        timestamp = int(time.time())
        pid = product.get("product_id", "prod"); filename = f"{pid}_{timestamp}.html"
        filepath = os.path.join(self.web_dir, filename)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product['title']} | Official Store</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background: #f4f7f6; }}
        .header {{ background: linear-gradient(135deg, #0088cc, #2575fc); color: white; padding: 40px; text-align: center; border-radius: 12px; }}
        .content {{ background: white; padding: 30px; margin-top: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
        .price {{ font-size: 32px; color: #27ae60; font-weight: bold; margin: 20px 0; }}
        .buy-btn {{ display: block; width: 100%; box-sizing: border-box; background: #0088cc; color: white; text-align: center; padding: 18px; font-size: 20px; font-weight: bold; text-decoration: none; border-radius: 8px; margin-top: 30px; transition: 0.3s; box-shadow: 0 4px 10px rgba(0,136,204,0.3); }}
        .buy-btn:hover {{ background: #006699; }}
        .crypto-box {{ background: #f0f8ff; border: 1px dashed #0088cc; padding: 20px; border-radius: 8px; margin-top: 25px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{product['title']}</h1>
        <p>The Ultimate Digital Asset for {product['target_audience']}</p>
    </div>
    
    <div class="content">
        <h2>About This Template</h2>
        <p>{product['description']}</p>
        
        <div class="price">${product['price_usd']} USD</div>

        <h3>What's Included:</h3>
        <ul>
            <li>Complete Notion Workspace System</li>
            <li>Automated Client & Project Trackers</li>
            <li>Instant 24/7 Automated Delivery via Telegram</li>
            <li>Lifetime Access & Future Updates</li>
        </ul>

        <div class="crypto-box">
            <h4 style="margin-top: 0; color: #0088cc;">⚡ Instant 24/7 Delivery via Telegram Bot</h4>
            <p style="margin: 5px 0; font-size: 14px;">Pay securely with <b>USDT (TRC20)</b> and get your Notion template delivered directly to your chat instantly by our automated sales bot.</p>
            <p style="font-size: 13px; color: #666; margin-top: 8px;">Official TRC20 Wallet: <code style="word-break: break-all; font-weight: bold; color: #222;">{usdt_wallet_address}</code></p>
        </div>

        <a href="{telegram_bot_url}" target="_blank" class="buy-btn">⚡ Buy Now & Get Instant Access via Telegram</a>
    </div>
</body>
</html>
"""

        with open(filepath, "w", encoding="utf-8-sig") as f:
            f.write(html_content)

        print(f"✅ Sales Agent: Professional sales page generated successfully: {filepath}")
        return True

if __name__ == "__main__":
    agent = SalesPageAgent()
    agent.generate_sales_page()