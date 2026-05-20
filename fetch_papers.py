import requests
import feedparser
import re
from datetime import date, timedelta
import os

SEARCH_KEYWORD = "altermagnetic"

TIME_RANGE_DAYS = 30
CATEGORY1 = "cond-mat.supr-con"
CATEGORY2 = "cond-mat.str-el"
MAX_RESULTS = 100
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "index.md")

def process_latex_math(text):
    result = []
    parts = re.split(r'(\\$[^$]+\\$)', text)
    for part in parts:
        if re.match(r'^\\$[^$]+\\$$$, part):
            inner = part[1:-1]
            if re.match(r'~[^$]+$', inner):
                inner = '{}' + inner
            inner = inner.replace('_', '\_').replace('*', '\*')
            result.append('$' + inner + '$')
        else:
            cleaned = re.sub(
                r'\\(?:text|textbf|textit|emph|mathorm|mathbf|mathit|mathcal|mathsf|mathtt|it|bf|rm|sl|sc|tt|cal)\s*\{([^}]*)\}',
                r'\1',
                part
            )
            escaped = cleaned.replace('{', '\{').replace('}', '\}').replace('_', '\_').replace('*', '\*')
            result.append(escaped)
    return ''.join(result)

END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=TIME_RANGE_DAYS)

search_query = (
    f'(ti:"{SEARCH_KEYWORD}" OR abs:"{SEARCH_KEYWORD}") '
    f'AND (cat:{CATEGORY1} OR cat:{CATEGORY2}) '
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
        print(f"正在检索 {START_DATE} 至 {END_DATE} 的相关论文...")
        response = requests.get(ARXIV_API_URL, params=request_params, timeout=120)
        response.raise_for_status()

        feed = feedparser.parse(response.content)
        if feed.bozo:
            raise Exception(f"数据觧析失败: {feed.bozo_exception}")

        paper_entries = feed.entries
        total_papers = len(paper_entries)

        if total_papers == 0:
            print(f"在指定时间范围内，桢o到与{SEARCH_KEYWORD}相关的凝聚态物理论文")
            exit()

        front_matter = "---\nlayout: default\ntitle: 交错磁论文
---\n\n"
        markdown_content = front_matter
        markdown_content += "# 凝聚态物理-交错磁(Altermagnetic)相关论文\n\n"
        markdown_content += f"> 检索时间范围：**{START_DATE}至{END_DATE}**\n"
        markdown_content += f"> 数据检索到 **{total_papers}** 篇相关论文，按提交时间降序排列\n\n"
        markdown_content += "---\n\n"

        for index, paper in enumerate(paper_entries, 1):
            paper_title = process_latex_math(paper.title.replace("\n", " ").strip())
            author_list = ", ".join([author.name for author in paper.authors])
            submit_date = paper.published.split("T")[0]
            arxiv_link = paper.id
            abstract = process_latex_math(paper.summary.replace("\n", " ").strip())

            markdown_content += f"## {index}. {paper_title}\n\n"
            markdown_content += f"- **检索日期**：{submit_date}\n"
            markdown_content += f"- **作蠅**：{author_list}\n"
            markdown_content += f"- **arXiv链接**���{arxiv_link}]({arxiv_link})\n\n"
            markdown_content += f"### 摘要\n{abstract}\n\n"
            markdown_content += "---\n\n"

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"\n检索完成！结果已保存到当前目录的 {OUTPUT_FILE} 文件中")

    except Exception as e:
        print(f"运行出错：{str(e)}")
