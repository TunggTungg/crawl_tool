# Import Module
import pdfx 
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import os
from utils.utils import process_new_papers


def process_papers_in_parallel(papers):
    with ThreadPoolExecutor() as executor:
        executor.map(process_new_papers, [os.path.join("output", paper) for paper in papers])

# def main():
#     mode = input("Choose mode (1: Search by keyword, 2: Process PDF file path): ")
    
#     if mode == '1':
#         keyword = input("Please input keyword: ")
#         crawl_arxiv(keyword)
#     elif mode == '2':
#         paper_path = input("Please input paper path: ")
#         process_new_papers(paper_path)
#     else:
#         print("Invalid mode selected.")

# # Call the main function
# if __name__ == "__main__":
#     main()

processed_papers = []  # Danh sách chứa tên các bài báo đã xử lý
process_new_papers("NEW.pdf")
while True:
    new_papers = [paper for paper in os.listdir("output") if paper.endswith(".pdf") and paper not in processed_papers]
    if new_papers:
        process_papers_in_parallel(new_papers)
        # Xóa các tệp đã xử lý và thêm vào danh sách đã xử lý
        processed_papers.extend(new_papers)  # Thêm vào danh sách đã xử lý
    else:
        break
