# Chuyển từ Poetry sang Miniconda

## Thay đổi đã thực hiện

- Thêm `environment.yml` cho môi trường Conda tên `fastapi-rag` với Python 3.13.
- Tách dependency thành `requirements.txt` (runtime) và
  `requirements-dev.txt` (test, lint, kiểm tra kiểu).
- Gỡ toàn bộ metadata, dependency và build backend của Poetry khỏi
  `pyproject.toml`; file này chỉ còn cấu hình pytest, coverage, mypy và ruff.
- Cập nhật `Dockerfile` để cài từ `requirements.txt`, không cài Poetry.
- Thêm `OPENAI_API_KEY` vào `.env.example` và cập nhật README.

## Cài đặt lần đầu: hai lựa chọn

### Lựa chọn 1 — Dùng `environment.yml` (khuyến nghị)

```powershell
conda env create -f environment.yml
conda activate fastapi-rag
```

### Lựa chọn 2 — Cài thủ công

```powershell
conda create -n fastapi-rag -c conda-forge python=3.13 pip
conda activate fastapi-rag
python -m pip install -r requirements-dev.txt
```

Nếu không cần công cụ phát triển, thay dòng pip cuối bằng:

```powershell
python -m pip install -r requirements.txt
```

Sau khi cài xong theo một trong hai cách, cấu hình và chạy ứng dụng:

```powershell
Copy-Item .env.example .env
# Mở .env và thay OPENAI_API_KEY bằng API key của bạn.
docker compose up -d
alembic upgrade head
uvicorn app.main:app --reload
```

Truy cập Swagger UI tại http://localhost:8000/.

## Cập nhật môi trường

Khi `requirements.txt`, `requirements-dev.txt` hoặc `environment.yml` thay đổi:

```powershell
# Nếu cài bằng environment.yml
conda env update -f environment.yml --prune

# Nếu cài thủ công
conda activate fastapi-rag
python -m pip install -r requirements-dev.txt
```

Để xóa hoàn toàn môi trường:

```powershell
conda env remove -n fastapi-rag
```

## Lưu ý

- Không dùng `poetry install`, `poetry run` hay `poetry export` nữa.
- Không dùng `pip freeze` để ghi đè các file requirements: lệnh này đưa toàn bộ
  dependency gián tiếp vào file và làm khó bảo trì. Hãy chỉ thêm dependency trực
  tiếp cùng khoảng phiên bản phù hợp.
- Nếu Conda chưa hoạt động trong PowerShell, chạy `conda init powershell`, sau đó
  khởi động lại terminal.
