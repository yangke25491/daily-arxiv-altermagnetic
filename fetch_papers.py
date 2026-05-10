import requests
import feedparser
from datetime import date, timedelta
import os
import sys

# ===================== 配置区 =====================
SEARCH_KEYWORD = "altermagnetic"
TIME_RANGE_DAYS = 30
CATEGORY = "cond-mat.*"
MAX_RESULTS = 100
# 获取环境变量中的文件名，如果没有则使用默认值
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "altermagnetic_recent_papers.md")
# ==================================================

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
        print(f"请求 URL: {ARXIV_API_URL}")
        print(f"请求参数: {request_params}")

        response = requests.get(ARXIV_API_URL, params=request_params, timeout=30)
        print(f"HTTP 状态码: {response.status_code}")

        # 如果状态码不是 200，打印响应内容前 500 字符以便调试
        if response.status_code != 200:
            print(f"错误响应内容预览: {response.text[:500]}")
            response.raise_for_status()  # 这会抛出 HTTPError

        feed = feedparser.parse(response.content)
        if feed.bozo:
            raise Exception(f"Feed 解析失败: {feed.bozo_exception}")

        paper_entries = feed.entries
        total_papers = len(paper_entries)
        print(f"获取到论文数量: {total_papers}")

        # ===================== 生成 Markdown =====================
        markdown_content = f"# 凝聚态物理-交错磁(Altermagnetic)相关论文

"
        markdown_content += f"> 最后更新时间：**{END_DATE}**
"
        markdown_content += f"> 检索范围：过去 **{TIME_RANGE_DAYS}** 天
"
        markdown_content += f"> 论文数量：**{total_papers}** 篇

"
        markdown_content += "---

"

        for index, paper in enumerate(paper_entries, 1):
            paper_title = paper.title.replace("
", " ").strip()
            author_list = ", ".join([author.name for author in paper.authors])
            submit_date = paper.published.split("T")[0]
            arxiv_link = paper.id
            abstract = paper.summary.replace("
", " ").strip()

            markdown_content += f"## {index}. {paper_title}

"
            markdown_content += f"- **提交日期**：{submit_date}
"
            markdown_content += f"- **作者**：{author_list}
"
            markdown_content += f"- **arXiv链接**：{arxiv_link}

"
            markdown_content += f"### 摘要
{abstract}

"
            markdown_content += "---

"

        # ===================== 保存文件 =====================
        output_dir = os.path.dirname(OUTPUT_FILE)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"✅ 成功生成文件：{OUTPUT_FILE}")

    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 运行出错：{str(e)}")
        sys.exit(1)

