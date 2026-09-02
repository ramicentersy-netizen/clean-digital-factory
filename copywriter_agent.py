import os
import json
import glob

class CopywriterAgent:
    def __init__(self, output_dir="marketing"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def find_latest_product(self):
        files = glob.glob("products/generated_outputs/*.json")
        if not files:
            return None
        latest_file = max(files, key=os.path.getctime)
        with open(latest_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_social_posts(self):
        product = self.find_latest_product()
        if not product:
            print("❌ No product found to write marketing content for.")
            return

        post_content = f"""🚀 Tired of feeling overwhelmed and disorganized in your daily freelance work?

We’ve just launched the ultimate solution for creators, remote workers, and solo-entrepreneurs:
📌 {product['title']}

✨ What's inside this powerful Notion workspace?
"""
        for comp in product.get('components', []):
            post_content += f"✔️ {comp}\n"

        post_content += f"""
🎯 Perfect for: {product['target_audience']}
💰 Price: Only ${product['price_usd']}!

💬 Drop a comment with "INTERESTED" below or send us a DM, and we’ll slide right into your inbox with the details!

#Notion #FreelancerLife #RemoteWork #Productivity #DigitalProducts #Solopreneur
"""

        file_name = f"post_{product['product_id']}.txt"
        file_path = os.path.join(self.output_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(post_content)

        print(f"✅ Successfully generated Western-targeted marketing post: {file_path}")
        return post_content

if __name__ == "__main__":
    agent = CopywriterAgent()
    agent.generate_social_posts()