import os
import glob
import json

class TrafficAgent:
    def __init__(self, marketing_dir="marketing"):
        self.marketing_dir = marketing_dir

    def find_latest_post(self):
        files = glob.glob(os.path.join(self.marketing_dir, "*.txt"))
        if not files:
            return None
        return max(files, key=os.path.getctime)

    def prepare_social_traffic_campaign(self):
        """
        تجهيز الحملة الإعلانية والترافيك لترويج المنتج في مجتمعات السوق الغربي
        """
        print("🌐 Traffic Agent: Preparing social traffic campaign for Western audience...")
        
        latest_post_file = self.find_latest_post()
        if not latest_post_file:
            print("❌ Traffic Agent Error: No marketing post found to broadcast.")
            return False

        with open(latest_post_file, "r", encoding="utf-8") as f:
            post_text = f.read()

        # محاكاة إعداد الحملة لمنصات مثل Reddit / X / Telegram
        campaign_channels = ["Reddit (r/Notion & r/Freelance)", "X (Twitter) Tech Communities", "Telegram Digital Channels"]
        
        print(f"✅ Traffic Agent: Campaign packaged successfully!")
        print(f"🎯 Target Channels: {', '.join(campaign_channels)}")
        print(f"📢 Post Preview Snippet: {post_text.splitlines()[0]}...")
        return True

if __name__ == "__main__":
    agent = TrafficAgent()
    agent.prepare_social_traffic_campaign()