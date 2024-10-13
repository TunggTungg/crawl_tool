import pdfx 
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import os
import arxiv

def download_arxiv_paper(arxiv_id, subfolder):
    try:
        client = arxiv.Client()
        result = arxiv.Search(id_list=[arxiv_id])
        paper_path = f"{arxiv_id}.{paper.title}.pdf"
        paper = next(client.results(result))
        paper.download_pdf(dirpath=subfolder)

        return True, paper_path
    except Exception as e:
        print(f"Failed to download paper {arxiv_id}: {e}")
        return False, paper_path

def process_new_papers(pdf_file_path, processed_papers=set(), output_folder: str = "outputs"):
    # Kiểm tra xem bài báo đã được xử lý chưa
    if pdf_file_path in processed_papers:
        return  # Nếu đã xử lý, thoát khỏi hàm

    # Đánh dấu bài báo này là đã được xử lý
    processed_papers.add(pdf_file_path)

    # Read PDF File
    pdf = pdfx.PDFx(pdf_file_path) 
    # Get list of URL
    results = pdf.get_references_as_dict()

    if 'arxiv' in results:
        print(f"Tổng số bài báo được phát hiện: {len(results['arxiv'])}")

        # Tạo thư mục con theo tên bài báo gốc
        paper_title = pdf_file_path.split("/")[-1].replace(".pdf", "").replace(" ", "_").replace("/", "_")
        output_folder = os.path.join(output_folder, paper_title)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Duyệt qua từng ID và tải
        total_papers = 0
        optimal_workers = 10  # Hoặc thử các giá trị như 15, 20

        with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
            futures = [executor.submit(download_arxiv_paper, arxiv_id, output_folder) for arxiv_id in results['arxiv']]
            for future in tqdm(futures, desc="Downloading papers"):
                result = future.result()
                if result[0]:
                    total_papers += 1
                    processed_papers.add(result[1])

        # success_rate = total_papers / len(results['arxiv']) * 100
        # print(f"Tổng số bài báo tải thành công: {total_papers}")
        # print(f"Tỉ lệ tải thành công: {success_rate:.2f}%")

        # # Mới: Trích xuất các hyperlink từ các bài báo đã tải xuống
        for id in results['arxiv']:
            paper_path = os.path.join(output_folder, file_name)
            print(f"Processing downloaded paper: {file_name}")
            process_new_papers(paper_path, processed_papers)  # Gọi lại hàm để trích xuất từ các bài báo đã tải xuống

def prompt_crawl_arxiv(keyword, max_results=10):
    search = arxiv.Search(
        query=keyword,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    output_folder = "downloads"  # Specify a folder to download papers
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for result in search.results():
        print(f"Title: {result.title}")
        print(f"Published: {result.published}")
        print(f"PDF URL: {result.pdf_url}\n")

        arxiv_id = result.entry_id.split('/')[-1]  # Extract arxiv ID from entry_id
        download_arxiv_paper(arxiv_id, output_folder)  # Download the paper
