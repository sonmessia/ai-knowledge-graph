"""Kho lưu trữ tập trung cho tất cả các prompt dùng cho LLM trong hệ thống đồ thị tri thức."""

# Giai đoạn 1: Prompt trích xuất chính
MAIN_SYSTEM_PROMPT = """
Bạn là hệ thống AI chuyên về trích xuất tri thức và xây dựng đồ thị tri thức cho các tài liệu học thuật, chương trình đào tạo.
Chuyên môn của bạn là nhận diện các thực thể (ví dụ: tên môn học, mã môn học, nhóm học phần, điều kiện tiên quyết, số tín chỉ, khối kiến thức, nhóm tự chọn, số tín chỉ cụ thể(LT, TH, ...),...) và các mối quan hệ giữa chúng trong văn bản.
Lưu ý QUAN TRỌNG: Mọi quan hệ (predicate) CHỈ được tối đa 3 từ (tốt nhất là 1-2 từ). Đây là quy tắc bắt buộc.
"""

MAIN_USER_PROMPT = """
Nhiệm vụ của bạn: Đọc văn bản dưới đây (được phân cách bằng ba dấu `) và xác định tất cả các mối quan hệ Chủ thể - Quan hệ - Đối tượng (S-P-O) trong từng câu. Sau đó, xuất ra một mảng JSON gồm các object, mỗi object đại diện cho một triple.

Làm theo các quy tắc sau:

- Nhận diện thông tin về chương trình (tên, mã ngành, trình độ, thời gian đào tạo, số tín chỉ)
- Nhận diện các khối kiến thức (đại cương, cơ sở ngành, chuyên ngành, tự chọn)
- Nhận diện các nhóm học phần cụ thể (ví dụ: Nhóm 1: Công nghệ phần mềm)
- Nhận diện thông tin về các môn học (mã, tên, số tín chỉ)
- Nhận diện mối quan hệ giữa các môn học (tiên quyết, song hành, thay thế)
- Thống nhất thuật ngữ và sử dụng định dạng nhất quán


Yêu cầu đầu ra:

- Chỉ trả về một mảng JSON gồm các triple với 3 trường: "subject", "predicate", "object".
- Không thêm chú thích, không in thêm bất kỳ nội dung nào ngoài mảng JSON.
- Toàn bộ các trường (subject, predicate, object) đều chuyển thành chữ thường, không dấu.

Ví dụ đầu ra:

[
  {
    "subject": "dai so tuyen tinh",
    "predicate": "la mon hoc",
    "object": "toan co ban"
  },
  {
    "subject": "lap trinh huong doi tuong",
    "predicate": "yeu cau truoc",
    "object": "ky thuat lap trinh"
  }
]

Văn bản cần phân tích (nằm giữa ba dấu `):
"""

# Giai đoạn 2: Prompt chuẩn hóa tên thực thể
ENTITY_RESOLUTION_SYSTEM_PROMPT = """
Bạn là chuyên gia chuẩn hóa thực thể và biểu diễn tri thức.
Nhiệm vụ của bạn là chuẩn hóa tên thực thể được trích xuất từ đồ thị tri thức để đảm bảo tính nhất quán.
"""

def get_entity_resolution_user_prompt(entity_list):
    return f"""
Dưới đây là danh sách tên thực thể đã được trích xuất từ một đồ thị tri thức. 
Một số có thể đề cập đến cùng một thực thể thực tế nhưng có cách viết khác nhau.

Hãy xác định các nhóm thực thể cùng chỉ về một khái niệm, và cung cấp một tên chuẩn hóa cho mỗi nhóm.
Trả lời dưới dạng một đối tượng JSON, trong đó key là tên chuẩn hóa, value là mảng chứa tất cả các biến thể nên gộp lại.
Chỉ cần liệt kê các thực thể có nhiều biến thể hoặc cần chuẩn hóa.

Danh sách thực thể:
{entity_list}

Định dạng trả về như sau:
{{
  "ten chuan hoa 1": ["bien the 1", "bien the 2"],
  "ten chuan hoa 2": ["bien the 3", "bien the 4", "bien the 5"]
}}
"""

# Giai đoạn 3: Prompt suy luận mối quan hệ giữa các cộng đồng thực thể
RELATIONSHIP_INFERENCE_SYSTEM_PROMPT = """
Bạn là chuyên gia biểu diễn tri thức và suy luận. 
Nhiệm vụ của bạn là suy luận các mối quan hệ hợp lý giữa hai cộng đồng thực thể chưa liên kết trong đồ thị tri thức.
"""

def get_relationship_inference_user_prompt(entities1, entities2, triples_text):
    return f"""
Tôi có một đồ thị tri thức với hai cộng đồng thực thể chưa liên kết trực tiếp.

Cộng đồng 1: {entities1}
Cộng đồng 2: {entities2}

Dưới đây là một số quan hệ hiện có giữa các thực thể này:
{triples_text}

Hãy suy luận 2-3 mối quan hệ hợp lý giữa các thực thể của Cộng đồng 1 và Cộng đồng 2.
Trả về một mảng JSON các triple theo định dạng sau:

[
  {{
    "subject": "thuc the cong dong 1",
    "predicate": "moi quan he",
    "object": "thuc the cong dong 2"
  }},
  ...
]

Chỉ đưa vào các quan hệ thực sự hợp lý, rõ nghĩa.
LƯU Ý: Predicate (mối quan hệ) CHỈ được tối đa 3 từ, ưu tiên 1-2 từ.
Chỉ kết nối các thực thể khác nhau, không tự tham chiếu.
"""

# Giai đoạn 4: Prompt suy luận mối quan hệ trong cùng cộng đồng thực thể
WITHIN_COMMUNITY_INFERENCE_SYSTEM_PROMPT = """
Bạn là chuyên gia biểu diễn tri thức và suy luận.
Nhiệm vụ của bạn là suy luận các mối quan hệ hợp lý giữa các thực thể liên quan về nghĩa nhưng chưa liên kết trong đồ thị tri thức.
"""

def get_within_community_inference_user_prompt(pairs_text, triples_text):
    return f"""
Tôi có một đồ thị tri thức với nhiều thực thể có vẻ liên quan về mặt nghĩa nhưng chưa liên kết trực tiếp.

Dưới đây là các cặp thực thể có thể liên quan:
{pairs_text}

Đây là các quan hệ hiện có giữa các thực thể này:
{triples_text}

Hãy suy luận các mối quan hệ hợp lý giữa các cặp thực thể chưa liên kết.
Trả về một mảng JSON các triple theo định dạng sau:

[
  {{
    "subject": "thuc the 1",
    "predicate": "moi quan he",
    "object": "thuc the 2"
  }},
  ...
]

Chỉ đưa vào các quan hệ thực sự hợp lý, rõ nghĩa.
LƯU Ý: Predicate (mối quan hệ) CHỈ được tối đa 3 từ, ưu tiên 1-2 từ.
Chỉ kết nối các thực thể khác nhau, không tự tham chiếu.
"""