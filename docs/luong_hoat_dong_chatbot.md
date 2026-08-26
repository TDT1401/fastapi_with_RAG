# Luồng hoạt động của chatbot RAG

Tài liệu này mô tả luồng đang được triển khai trong mã nguồn tại `app/api/endpoints/chatbot.py`, bao gồm nạp nguồn tri thức, tạo vector store, trả lời câu hỏi và lưu hội thoại.

## Tổng quan kiến trúc

Chatbot dùng mô hình **RAG** (Retrieval-Augmented Generation): thay vì để mô hình ngôn ngữ trả lời chỉ bằng kiến thức sẵn có, ứng dụng tìm các đoạn phù hợp trong tài liệu đã nạp, đưa chúng vào prompt, rồi mới yêu cầu mô hình tạo câu trả lời.

```text
Nguồn PDF / URL web / Markdown
        |
        v
Tách nội dung -> chia đoạn -> embedding `nomic-embed-text`
        |
        v
ChromaDB trên đĩa: db/chroma_db_{loại}_ollama/{tên-nguồn}

Yêu cầu chat
        |
        v
Chọn đúng ChromaDB -> tìm 2 đoạn tương đồng nhất
        |
        v
Prompt (câu hỏi + context) -> Ollama `llama3.2` -> câu trả lời
        |
        v
Phản hồi API + lưu lịch sử vào chat_store.json
```

Hai model Ollama cục bộ được khai báo cố định:

| Vai trò | Model | Vị trí khai báo |
| --- | --- | --- |
| Tạo embedding cho tài liệu và truy vấn | `nomic-embed-text` | `app/services/vector_handler.py` |
| Sinh câu trả lời | `llama3.2` | `app/services/rag_chain.py` |

Vì vậy, trước khi sử dụng cần Ollama đang chạy và đã có hai model này. PostgreSQL/JWT là phần khác của dự án; luồng chatbot hiện không đọc hay ghi lịch sử vào PostgreSQL.

## Địa chỉ API và dữ liệu vào

`app/main.py` đăng ký `chatbot_router`; `app/api/api_router.py` gắn router này với prefix `/chatbot`. Các API chatbot là:

| API | Mục đích |
| --- | --- |
| `POST /chatbot/upload/pdf` | Lập chỉ mục một file PDF ở máy/chứa ứng dụng. |
| `POST /chatbot/upload/wp` | Lập chỉ mục nội dung của một URL web. |
| `POST /chatbot/upload/md` | Lập chỉ mục một file Markdown ở máy/chứa ứng dụng. |
| `GET /chatbot/documents` | Lấy danh sách các index tài liệu có thể chọn để chat. |
| `POST /chatbot/chat` | Truy vấn một nguồn đã được lập chỉ mục. |

Ba API `upload` nhận JSON theo schema `UploadRequest`:

```json
{ "file_path": "duong-dan-file-hoac-url" }
```

Để lấy các nguồn đã nạp cho `selector_choices`, gọi `GET /chatbot/documents`. Response gồm ID index và loại nguồn tương ứng:

```json
{
  "documents": [
    {
      "selector_choices": "e_vnexpress_net_12345",
      "reasoning_type": "wp"
    },
    {
      "selector_choices": "bao-cao",
      "reasoning_type": "pdf"
    }
  ]
}
```

Tên gọi “upload” ở đây không có nghĩa API nhận nội dung file qua `multipart/form-data`: với PDF/Markdown, `file_path` phải là đường dẫn mà tiến trình API có thể truy cập; với website, trường này là URL. API chỉ tạo index, không sao chép file vào project.

API chat nhận `ChatRequest`:

```json
{
  "user_id": "user-123",
  "chat_input": "Nội dung chính của tài liệu là gì?",
  "selector_choices": "tai-lieu-a",
  "reasoning_type": "pdf",
  "conversation_id": "20260826_153000"
}
```

### Dữ liệu cần truyền vào `chatbot_reply`

Gọi endpoint `POST /chatbot/chat` với header `Content-Type: application/json` và body theo bảng sau:

| Trường | Kiểu | Bắt buộc | Giá trị / ý nghĩa |
| --- | --- | --- | --- |
| `user_id` | `string` | Có | Mã người dùng. Được dùng làm khóa để đọc và lưu lịch sử trong `chat_store.json`. |
| `chat_input` | `string` | Có | Câu hỏi gửi cho chatbot. Nên là chuỗi không rỗng. |
| `selector_choices` | `string` | Có | Tên index ChromaDB cần truy vấn; phải khớp với nguồn đã nạp và với `reasoning_type`. |
| `reasoning_type` | `"wp"` \| `"pdf"` \| `"md"` | Không | Loại nguồn cần truy vấn. Mặc định là `"wp"`. |
| `conversation_id` | `string` | Không | ID cuộc hội thoại để tiếp tục lịch sử cũ. Bỏ qua để server tự tạo ID mới. |

`selector_choices` không phải là tên tùy ý. Endpoint ghép nó vào đường dẫn sau để mở vector store:

```text
db/chroma_db_{reasoning_type}_ollama/{selector_choices}
```

Giá trị này được tạo khi gọi API nạp nguồn:

| `reasoning_type` | API nạp nguồn | Cách xác định `selector_choices` | Ví dụ |
| --- | --- | --- | --- |
| `pdf` | `POST /chatbot/upload/pdf` | Tên file PDF, bỏ phần mở rộng | `C:\\data\\bao-cao.pdf` → `bao-cao` |
| `md` | `POST /chatbot/upload/md` | Tên file Markdown, bỏ phần mở rộng | `docs/huong-dan.md` → `huong-dan` |
| `wp` | `POST /chatbot/upload/wp` | Hostname URL, bỏ `www.`, thay `.` bằng `_`, rồi thêm 5 chữ số ngẫu nhiên | `https://e.vnexpress.net/...` → `e_vnexpress_net_12345` |

Ví dụ request dùng website đã nạp (dùng đúng `selector_choices` do API upload trả về):

```json
{
  "user_id": "user-123",
  "chat_input": "Trang này nói gì về công nghệ?",
  "selector_choices": "e_vnexpress_net_12345",
  "reasoning_type": "wp"
}
```

Ví dụ request tiếp tục một cuộc hội thoại PDF:

```json
{
  "user_id": "user-123",
  "chat_input": "Hãy tóm tắt phần kết luận.",
  "selector_choices": "bao-cao",
  "reasoning_type": "pdf",
  "conversation_id": "20260826_153000"
}
```

Trong đó:

- `user_id`, `chat_input`, `selector_choices` là bắt buộc.
- `reasoning_type` chỉ nhận `pdf`, `wp` hoặc `md`; mặc định là `wp`.
- `selector_choices` phải khớp tên thư mục index đã sinh khi nạp nguồn.
- `conversation_id` là tùy chọn. Nếu bỏ qua, server sinh ID theo giờ địa phương dạng `YYYYMMDD_HHMMSS`.

Ví dụ khớp nguồn: PDF có đường dẫn `C:\data\bao-cao.pdf` được lưu vào `db/chroma_db_pdf_ollama/bao-cao`; khi chat phải dùng `reasoning_type: "pdf"` và `selector_choices: "bao-cao"`. Với URL `https://www.example.com/docs`, tên được chuẩn hóa thành dạng `example_com_12345`, nên index là `db/chroma_db_wp_ollama/example_com_12345`.

## Luồng nạp nguồn tri thức

Phần này chạy trước khi người dùng đặt câu hỏi. Nó được xử lý bởi các endpoint trong `chatbot.py`, hàm tạo store trong `vector_handler.py` và các hàm đọc/chia nội dung trong `utils/process.py`.

1. Endpoint tạo `file_id` từ tên file không có phần mở rộng (PDF/Markdown), hoặc `website_id` từ hostname URL kèm 5 chữ số ngẫu nhiên (web).
2. Endpoint tạo đường dẫn ChromaDB theo công thức `db/chroma_db_{reasoning_type}_ollama/{id}`.
3. Hàm `create_vector_store_pdf`, `create_vector_store_wp` hoặc `create_vector_store_md` kiểm tra thư mục này. Nếu đã tồn tại, kết quả là `Document already exists.` và nguồn không được nạp lại.
4. Nếu chưa có store, loader tương ứng đọc nguồn:
   - PDF: `PyPDFLoader` đọc thành các `Document` theo trang.
   - Website: `WebBaseLoader` tải và trích nội dung URL.
   - Markdown: `TextLoader` đọc file UTF-8.
5. `RecursiveCharacterTextSplitter` chia nội dung thành các đoạn tối đa 1.000 ký tự, chồng lấn 100 ký tự. Phần chồng lấn giúp ý nghĩa ở ranh giới hai đoạn ít bị mất hơn.
6. `OllamaEmbeddings(model="nomic-embed-text")` biến từng đoạn thành vector. `Chroma.from_documents(...)` lưu các đoạn cùng vector xuống thư mục ChromaDB.
7. Endpoint trả `message` kèm `selector_choices`, là đúng tên index để gửi thẳng vào API chat. Ví dụ:

   ```json
   {
     "message": "Document created successfully.",
     "selector_choices": "bao-cao"
   }
   ```

   Khi tạo index thất bại, `selector_choices` có giá trị `null`.

Tên thư mục store là khóa để chọn nguồn khi chat; nó không chứa `user_id` hay `conversation_id`. Do đó các nguồn tri thức hiện là dùng chung trong phạm vi server.

## Luồng trả lời `POST /chatbot/chat`

1. Endpoint lấy các trường từ request. Nếu thiếu `conversation_id`, hàm `generate_conversation_id()` tạo một ID mới.
2. `load_chat_history(user_id, conversation_id)` đọc `chat_store.json`. Cấu trúc file là `user_id -> conversation_id -> [[câu_hỏi, câu_trả_lời], ...]`. Khi đọc, mỗi mục được đổi lại thành tuple Python.
3. Nếu `chat_input` có nội dung, endpoint thêm tạm `(chat_input, None)` vào cuối lịch sử.
4. `build_rag_chain()` dựng chuỗi LangChain sau mỗi request:

   ```text
   RunnableLambda(get_context)
     | PromptTemplate
     | ChatOllama("llama3.2")
     | StrOutputParser
   ```

5. `rag_chain.invoke(...)` truyền `selector_choices`, `reasoning_type` và `chat_input` vào chuỗi.
6. `get_context(...)` mở ChromaDB từ `db/chroma_db_{reasoning_type}_ollama/{selector_choices}`, với cùng embedding model `nomic-embed-text`.
7. `retrieve_context(...)` tạo retriever kiểu `similarity`, tìm `k=2` đoạn gần với câu hỏi nhất, rồi ghép `page_content` của hai đoạn thành `context`.
8. Prompt nhận `query` và `context`. Nó yêu cầu mô hình chỉ trả lời dựa vào context; nếu không có thông tin thì trả câu tiếng Anh: `The answer to this question is not available in the provided content.`
9. `ChatOllama` gọi Ollama để sinh phản hồi; `StrOutputParser` chuyển kết quả về chuỗi `result`.
10. Endpoint thay mục lịch sử tạm cuối cùng bằng `(câu_hỏi, result)`, ghi toàn bộ lịch sử trở lại `chat_store.json`, chuyển sang dạng object `{ "user": ..., "bot": ... }` và trả response.

Ví dụ response thành công:

```json
{
  "answer": "...",
  "history": [
    { "user": "Câu hỏi trước", "bot": "Câu trả lời trước" },
    { "user": "Nội dung chính là gì?", "bot": "..." }
  ],
  "conversation_id": "20260826_153000"
}
```

## Lịch sử hội thoại và phạm vi ngữ cảnh

`chat_store.json` dùng để lưu và trả lại lịch sử theo người dùng và cuộc hội thoại. Lịch sử không được truyền vào `get_context`, prompt hay LLM. Nói cách khác, **mỗi câu hỏi RAG hiện độc lập với các câu trước**; `conversation_id` chỉ phục vụ lưu/nhóm lịch sử ở response, chưa tạo được hội thoại đa lượt theo ngữ cảnh.

Tệp lịch sử là một file JSON tương đối theo thư mục chạy ứng dụng. Nếu chạy nhiều worker/container hoặc có nhiều request ghi đồng thời, cơ chế này có thể phát sinh ghi đè/tranh chấp; đây không phải kho lưu trữ phù hợp cho môi trường production.

## Các giới hạn và điểm cần lưu ý của bản hiện tại

- Router chatbot không sử dụng `get_current_user` hay dependency xác thực. `user_id` do client gửi lên và chưa được đối chiếu với JWT/tài khoản; các endpoint chatbot hiện không được bảo vệ bởi auth ở cấp route.
- `selector_choices` được ghép trực tiếp vào đường dẫn. Client cần gửi đúng tên index; nên kiểm tra/giới hạn giá trị này trước khi triển khai công khai.
- Hệ thống không kiểm tra rõ ràng index có tồn tại hoặc có dữ liệu trước lúc truy vấn. Nếu chọn sai loại/tên nguồn, lỗi hoặc context rỗng phụ thuộc vào Chroma/Ollama ở runtime.
- Các hàm nạp PDF/website hiện bắt mọi exception rồi trả biến `status`. Nếu lỗi xảy ra trước khi biến này được gán, endpoint có thể phát sinh thêm lỗi `UnboundLocalError`; endpoint Markdown đã trả chuỗi lỗi cố định nên không gặp lỗi này.
- Nhánh `chat_input` rỗng khi chưa có lịch sử gọi `ChatResponse(reply=...)`, nhưng schema `ChatResponse` yêu cầu trường `answer`, không có trường `reply`. Nhánh này vì thế không trả được response hợp lệ. Nếu lịch sử đã tồn tại và input rỗng, code vẫn gọi RAG rồi ghi đè câu trả lời của lượt cuối.
- Conversation ID chỉ chính xác đến giây, vì thế hai cuộc hội thoại mới của cùng user trong cùng giây có thể dùng chung ID.
- Các endpoint được khai báo `async`, nhưng đọc file/web, Chroma, embedding và `rag_chain.invoke()` đều là thao tác đồng bộ; chúng có thể chặn event loop khi xử lý tài liệu lớn hoặc model phản hồi chậm.
- Prompt và thông báo fallback hiện bằng tiếng Anh. Chất lượng câu trả lời phụ thuộc vào nội dung được truy xuất, model Ollama và ngôn ngữ tài liệu; không có trích dẫn nguồn hay điểm tương đồng trong response.

## Bản đồ mã nguồn

| File | Trách nhiệm |
| --- | --- |
| `app/main.py` | Khởi tạo FastAPI và đăng ký router chatbot. |
| `app/api/api_router.py` | Gắn prefix `/chatbot`. |
| `app/api/endpoints/chatbot.py` | Bốn endpoint chat/nạp nguồn và điều phối lịch sử. |
| `app/schemas/requests.py` | Kiểm tra dữ liệu request (`ChatRequest`, `UploadRequest`). |
| `app/schemas/responses.py` | Định dạng response (`ChatResponse`, `UploadResponse`). |
| `app/utils/process.py` | Đọc PDF/web/Markdown, chia đoạn, sinh conversation ID. |
| `app/utils/document_index.py` | Sinh ID website và liệt kê các index ChromaDB có thể chọn. |
| `app/services/vector_handler.py` | Tạo/mở ChromaDB và tạo embedding qua Ollama. |
| `app/services/rag_chain.py` | Truy xuất context, dựng prompt và gọi LLM. |
| `app/utils/save_history.py` | Đọc/ghi `chat_store.json`. |
