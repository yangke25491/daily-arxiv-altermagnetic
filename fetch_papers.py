import requests
import feedparser
from datetime import date, timedelta
import os

# ===================== 配置区域 =====================
SEARCH_KEYWORD = "altermagnetic"
TIME_RANGE_DAYS = 7
CATEGORY = "cond-mat.*"
MAX_RESULTS = 50
# 从环境变量中获取文件名，如果没有则使用默认值
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "altermagnetic_recent_papers.md")
# ====================================================

END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=TIME_RANGE_DAYS)

search_query = (
    f'(ti:"{SEARCH_KEYWORD}" OR abs:"{SEARCH_KEYWORD}") '
    f'AND cat:{CATEGORY} '
    f'AND submittedDate:[{START_DATE.strftime("%Y%m%d")}0000 TO {END_DATE.strftime("%Y%m%d")}2359]'
)

ARXIV_API_URL = "http://export.arxiv.org/api/query"

request_params = {
    "search_query": search_query,
    "start": 0,
    "max_results": MAX_RESULTS,
    "sortBy": "submittedDate",
    "sortOrder": "descending"
}

if __name__ == "__main__":
    try:
        print(f"正在检索 {START_DATE} 至 {END_DATE} 的论文...")
        response = requests.get(ARXIV_API_URL, params=request_params, timeout=30)
        response.raise_for_status()

        feed = feedparser.parse(response.content)
        if feed.bozo:
            raise Exception(f"解析失败: {feed.bozo_exception}")

        paper_entries = feed.entries
        total_papers = len(paper_entries)

        # ===================== 生成 Markdown =====================
        markdown_content = f"# 凝聚态物理-交错磁(Altermagnetic)相关论文\n\n"
        markdown_content += f"> 最后更新时间：**{END_DATE}**\n"
        markdown_content += f"> 检索范围：过去 **{TIME_RANGE_DAYS}** 天\n"
        markdown_content += f"> 论文数量：**{total_papers}** 篇\n\n"
        markdown_content += "---\n\n"

        for index, paper in enumerate(paper_entries, 1):
            paper_title = paper.title.replace("\n", " ").strip()
            author_list = ", ".join([author.name for author in paper.authors])
            submit_date = paper.published.split("T")[0]
            arxiv_link = paper.id
            abstract = paper.summary.replace("\n", " ").strip()

            markdown_content += f"## {index}. {paper_title}\n\n"
            markdown_content += f"- **提交日期**：{submit_date}\n"
            markdown_content += f"- **作者**：{author_list}\n"
            markdown_content += f"- **arXiv链接**：{arxiv_link}\n\n"
            markdown_content += f"### 摘要\n${abstract}$\n\n"
            markdown_content += "---\n\n"

        # ===================== 保存文件 =====================
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"✓ 成功生成文件：{OUTPUT_FILE}")
        print(f"📄 共处理 {total_papers} 篇论文")

    except Exception as e:
        print(f"✗ 运行出错：{str(e)}")
        exit(1)