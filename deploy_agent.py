import os
import glob
import shutil
import subprocess

class DeploymentAgent:
    def __init__(self, web_dir="web"):
        self.web_dir = web_dir

    def find_latest_sales_page(self):
        files = glob.glob(os.path.join(self.web_dir, "*.html"))
        if not files:
            return None
        return max(files, key=os.path.getctime)

    def deploy_to_github_pages(self):
        """
        نسخ أحدث صفحة بيع وتحويلها إلى index.html، ثم رفعها تلقائياً إلى GitHub Pages
        """
        print("☁️ Deployment Agent: Preparing latest sales page for GitHub Pages deployment...")
        
        latest_page = self.find_latest_sales_page()
        if not latest_page:
            print("❌ Deployment Agent Error: No sales page found to deploy.")
            return False

        # نسخ الملف الأحدث وتسميته index.html في المجلد الرئيسي ليكون الواجهة للموقع
        index_path = "index.html"
        shutil.copy(latest_page, index_path)
        print(f"📄 Deployment Agent: Copied {os.path.basename(latest_page)} to root as index.html")

        # تنفيذ أوامر Git لرفع الملف تلقائياً إلى مستودع GitHub
        try:
            print("🔄 Deployment Agent: Pushing updates to GitHub repository...")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Auto-deploy latest digital product sales page via Deployment Agent"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            
            print("✅ Deployment Agent: Successfully deployed live to GitHub Pages!")
            print("🌍 Your Live Store URL: https://ramicentersy-netizen.github.io/clean-digital-factory/")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git Automation Warning: Could not push automatically ({e}).")
            print("💡 Tip: index.html is successfully updated in your root folder ready for manual push if needed!")
            return False

    def deploy_to_cloud(self):
        """
        دالة توافقية لكي يعمل run.py دون أخطاء
        """
        return self.deploy_to_github_pages()

if __name__ == "__main__":
    agent = DeploymentAgent()
    agent.deploy_to_cloud()