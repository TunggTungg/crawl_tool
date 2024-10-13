import pdfx 
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import os
import arxiv

def download_arxiv_paper(arxiv_id):
    try:
        client = arxiv.Client()
        paper = next(client.results(arxiv.Search(id_list=[arxiv_id])))
        paper.download_pdf(dirpath="./outputs")
        return True, arxiv_id
    except Exception as e:
        print(f"Failed to download paper {arxiv_id}: {e}")
        return False, arxiv_id

def process_new_papers(pdf_file_path):
    # Read PDF File
    pdf = pdfx.PDFx(pdf_file_path) 
    # Get list of URL
    results = pdf.get_references_as_dict()
    if 'arxiv' in results:
        print(f"Tổng số bài báo được phát hiện: {len(results['arxiv'])}")

        # Duyệt qua từng ID và tải
        total_papers = 0
        optimal_workers = 10  # Hoặc thử các giá trị như 15, 20
        output_folder = 'outputs'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
            futures = [executor.submit(download_arxiv_paper, arxiv_id) for arxiv_id in results['arxiv']]
            for future in tqdm(futures, desc="Downloading papers"):
                result = future.result()
                if result[0]:
                    total_papers += 1

        success_rate = total_papers / len(results['arxiv']) * 100
        print(f"Tổng số bài báo tải thành công: {total_papers}")
        print(f"Tỉ lệ tải thành công: {success_rate:.2f}%")

def crawl_arxiv(keyword, max_results=10):
    search = arxiv.Search(
        query=keyword,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    for result in search.results():
        print(f"Title: {result.title}")
        print(f"Published: {result.published}")
        print(f"PDF URL: {result.pdf_url}\n")
        