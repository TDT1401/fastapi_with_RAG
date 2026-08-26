# FastAPI with RAG

Backend FastAPI bất đồng bộ, PostgreSQL, xác thực JWT và chatbot RAG sử dụng
OpenAI cùng ChromaDB. Dự án dùng **Miniconda** để quản lý môi trường Python;
không cần Poetry.

## Yêu cầu

- [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/)
- Docker Desktop (để chạy PostgreSQL)
- OpenAI API key (để gọi các API chatbot/RAG)

## Cài đặt môi trường

Tại thư mục gốc của dự án, chọn **một** trong hai cách sau.

### Cách 1 — Cài từ `environment.yml` (khuyến nghị)

File `environment.yml` tạo môi trường Python 3.13 và cài toàn bộ dependency
chạy ứng dụng, test và lint.

```powershell
conda env create -f environment.yml
conda activate fastapi-rag
```

### Cách 2 — Tạo môi trường và cài thủ công

Dùng cách này khi bạn muốn kiểm soát từng bước cài đặt hoặc không dùng file YML.

```powershell
# Tạo môi trường Conda với đúng phiên bản Python
conda create -n fastapi-rag -c conda-forge python=3.13 pip
conda activate fastapi-rag

# Cài dependency chạy ứng dụng, test và lint
python -m pip install -r requirements-dev.txt
```

Chỉ cần chạy ứng dụng mà không cần test/lint thì thay lệnh cuối bằng:

```powershell
python -m pip install -r requirements.txt
```

## Chạy dự án trên Windows (PowerShell)

Sau khi hoàn tất **một** cách cài đặt ở trên:

```powershell
# 1. Tạo file cấu hình cục bộ và điền OPENAI_API_KEY của bạn
Copy-Item .env.example .env

# 2. Khởi động PostgreSQL
docker compose up -d

# 3. Áp dụng migration
alembic upgrade head

# 4. Chạy API
uvicorn app.main:app --reload
```

Mở http://localhost:8000/ để dùng Swagger UI. Để dừng PostgreSQL, chạy
`docker compose down`.

> Nếu PowerShell báo không nhận ra `conda`, đóng và mở lại terminal sau khi cài
> Miniconda, hoặc chạy `conda init powershell` rồi mở lại PowerShell.

## Cấu hình môi trường

File `.env` không được commit. Sao chép từ `.env.example`, sau đó thay giá trị
`OPENAI_API_KEY` bằng API key thật. Các biến `DATABASE__*` phải khớp với cấu
hình PostgreSQL Docker; mặc định database được mở tại `localhost:5455`.

## Lệnh phát triển

```powershell
conda activate fastapi-rag

# Cập nhật packages theo các file requirements (cách 1)
conda env update -f environment.yml --prune

# Hoặc cập nhật packages thủ công (cách 2)
python -m pip install -r requirements-dev.txt

# Kiểm tra định dạng/lint
pre-commit install --install-hooks
pre-commit run --all-files

# Chạy kiểm thử (PostgreSQL phải đang hoạt động)
pytest
```

`pytest` tạo các test database trên PostgreSQL. Có thể chạy kiểm tra kiểu với
`mypy app`.

## Quản lý dependencies

- Thêm dependency chạy ứng dụng vào `requirements.txt`.
- Thêm công cụ test/lint vào `requirements-dev.txt`.
- Dùng `conda env update -f environment.yml --prune` (cách 1) hoặc
  `python -m pip install -r requirements-dev.txt` (cách 2) sau khi thay đổi.

`environment.yml` quản lý Python và pip trong Conda; các phiên bản package
Python được khai báo rõ trong hai file requirements. Cách này hoạt động tốt với
cả package web lẫn package AI/ML.

## Docker

Docker image không còn cài Poetry. Build image bằng:

```powershell
docker build -t fastapi-rag .
```

Container cần nhận các biến trong `.env` và có thể kết nối được tới PostgreSQL.

## Tài liệu liên quan

- [Hướng dẫn chuyển từ Poetry sang Miniconda](MIGRATION_POETRY_TO_MINICONDA.md)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/)
