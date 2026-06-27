# Smart CV-JD Matching System (Graph-Based Architecture)

Hệ thống phân tích hồ sơ ứng viên (CV) và đối chiếu thông minh với yêu cầu tuyển dụng (Job Description - JD) ứng dụng cấu trúc dữ liệu Đồ thị tri thức (Knowledge Graph) và thiết kế hệ thống hướng đối tượng (OOP). Dự án thuộc chương trình đào tạo Khóa học AI Viet Nam (AIO2026) - Module 01.

## 🚀 Tính năng cốt lõi (Core Features)

* **Layout-Aware ETL Pipeline:** Hệ thống trích xuất văn bản từ cấu trúc PDF phức tạp, tự động nhóm và sắp xếp khối văn bản theo tọa độ không gian đồ họa (PyMuPDF) để bảo toàn chính xác cấu trúc CV 2 cột.
* **OCR Fail-safe Engine:** Cơ chế tự động phát hiện tài liệu scan dạng hình ảnh và kích hoạt hệ thống nhận diện ký tự quang học (Tesseract OCR) khi dữ liệu text thô bị thiếu hụt.
* **Knowledge Graph Matching Logic:** Giải quyết triệt để nhược điểm của phương pháp đối sánh từ khóa thô (Exact Keyword Match). Sử dụng thuật toán duyệt đồ thị nâng cao (BFS) kết hợp hàm suy giảm khoảng cách (Decay Factor) để tính toán điểm liên đới ngữ nghĩa giữa các kỹ năng có tính liên kết hoặc phân cấp phân tầng.
* **High Performance Memoization Cache:** Tích hợp bộ đệm lưu trữ trạng thái khoảng cách đồ thị cục bộ, tối ưu hóa tốc độ xử lý từ $O(V+E)$ về $O(1)$ cho các truy vấn trùng lặp khi chạy tập dữ liệu lớn.
* **Production-grade Web Dashboard:** Giao diện Dashboard tối giản, hiện đại (Tailwind CSS) tương tác trực tiếp với hệ thống API (FastAPI) bất đồng bộ, biểu diễn cấu trúc năng lực trực quan qua biểu đồ Radar (Chart.js) và truy vết chính xác đường đi thực thi thuật toán trên Graph Path.

## 📁 Cấu trúc thư mục dự án (Project Architecture)

```text
smart-cv-matching/
├── checkpoints/          # Lưu trữ cấu trúc phân tầng đồ thị tri thức (Graph Weights)
├── data/
│   └── raw/temp/         # Thư mục xử lý file biểu mẫu tạm thời (Tự động dọn dẹp)
├── docs/                 # Tài liệu thiết kế hệ thống và Technical Report
├── frontend/
│   └── index.html        # Giao diện chính tương tác Dashboard (Tailwind, Vanilla JS, Chart.js)
├── logs/
│   └── metrics.json      # Nhật ký giám sát hiệu năng và lịch sử chấm điểm hệ thống
├── src/
│   ├── api/              # Tầng đóng gói phân phối dịch vụ API (FastAPI)
│   │   ├── main.py       # Điểm khởi chạy ứng dụng và quản lý vòng đời hệ thống (Lifespan)
│   │   ├── routes.py     # Định tuyến điều phối Endpoint và xử lý kiểm soát ngoại lệ
│   │   └── schemas.py    # Khung xác thực và ràng buộc mô hình dữ liệu (Pydantic)
│   ├── core/             # Tầng xử lý logic thuật toán nòng cốt
│   │   ├── graph.py      # Định nghĩa mô hình cấu trúc dữ liệu SkillNode và SkillGraph
│   │   └── matcher.py    # Thuật toán duyệt BFS truy vết đường đi và tính toán điểm số
│   └── etl/              # Đường ống xử lý và chuyển đổi dữ liệu
│       └── parser.py     # Cấu trúc trích xuất văn bản đa tầng (PyMuPDF / OCR Fallback)
├── requirements.txt      # Danh sách chi tiết các thư viện phụ thuộc môi trường
└── README.md             # Tài liệu hướng dẫn sử dụng hệ thống