# CS2205.CH203 — Scientific Research Methodology

## Giới thiệu

- **Tên môn học:** PHƯƠNG PHÁP LUẬN NGHIÊN CỨU KHOA HỌC — Research Methodology
- **Mã môn:** CS2205.JAN2026

### Giảng viên

- PGS.TS Lê Đình Duy — duyld@uit.edu.vn

### Học viên

| STT | Họ tên          | MSHV      | 
|:---:|-----------------|-----------|
|  1  | Lê Thành Duy Ân | 250201041 |

## Tên đề tài

**Phân tích hành vi chi tiêu nhằm hỗ trợ tối ưu hóa chương trình hoàn tiền cho người dùng thẻ tín dụng tại Việt Nam**

## Tổng quan dự án

Dự án tập trung phân tích hành vi chi tiêu của người dùng thẻ tín dụng tại Việt Nam nhằm xác định các nhóm chi tiêu phổ biến và gợi ý các nhóm ưu đãi hoàn tiền phù hợp.

Thay vì xem xét từng giao dịch riêng lẻ, dự án hướng đến việc nhóm người dùng dựa trên sự tương đồng trong thói quen chi tiêu, chẳng hạn như số tiền giao dịch, tần suất giao dịch, nhóm tuổi và các danh mục chi tiêu như ăn uống, mua sắm, du lịch, giáo dục, y tế và sinh hoạt hằng ngày.

Mục tiêu chính là tìm hiểu cách dữ liệu giao dịch có thể được sử dụng để mô tả hành vi người dùng và hỗ trợ đề xuất chương trình hoàn tiền phù hợp hơn cho từng nhóm khách hàng.

## Mục tiêu chính

- Phân tích hành vi giao dịch thẻ tín dụng của người dùng tại Việt Nam
- Xác định các mẫu chi tiêu phổ biến giữa các nhóm người dùng
- Áp dụng các kỹ thuật phân tích dữ liệu và phân cụm để nhóm người dùng có hành vi chi tiêu tương đồng
- Khảo sát các lĩnh vực chi tiêu phù hợp cho việc tối ưu hóa hoàn tiền

## Hướng tiếp cận dự kiến

Dự án dự kiến sử dụng dữ liệu giao dịch bao gồm các thông tin như mã người dùng đã ẩn danh, nhóm tuổi, số tiền giao dịch, thời gian giao dịch, tần suất giao dịch và danh mục chi tiêu.

Sau bước tiền xử lý và xây dựng đặc trưng, các phương pháp phân cụm như `K-Means` sẽ được áp dụng để nhóm những người dùng có hành vi chi tiêu tương tự nhau. Từ kết quả đó, dự án sẽ phân tích đặc điểm nổi bật của từng nhóm và xác định các danh mục chi tiêu có tiềm năng tối ưu hoàn tiền.

## Bộ dữ liệu tổng hợp

Dự án sử dụng bộ dữ liệu tổng hợp theo dạng quan hệ để mô phỏng hành vi sử dụng thẻ tín dụng. Các bảng chính gồm:

- `users.csv`: thông tin người dùng đã ẩn danh
- `banks.csv`: ngân hàng phát hành thẻ
- `cards.csv`: danh mục sản phẩm thẻ tín dụng
- `user_cards.csv`: thẻ mà từng người dùng đang sở hữu
- `merchant_category_codes.csv`: mã ngành hàng MCC
- `merchants.csv`: thông tin merchant và MCC tương ứng
- `reward_rules.csv`: quy tắc hoàn tiền hoặc tích điểm của từng thẻ
- `reward_rule_mccs.csv`: MCC hợp lệ cho từng quy tắc ưu đãi
- `transactions.csv`: giao dịch thẻ tín dụng đã được mô phỏng

Có thể sinh dữ liệu bằng lệnh:

```bash
python3 scripts/generate_synthetic_dataset.py --transactions 50000
```

Hoặc sinh bộ dữ liệu lớn hơn:

```bash
python3 scripts/generate_synthetic_dataset.py --transactions 100000
```

Mặc định dữ liệu được xuất vào thư mục `data/synthetic/`.

## Kết quả kỳ vọng

Dự án hướng đến các kết quả sau:

- Các nhóm người dùng có đặc điểm chi tiêu khác nhau
- Mô tả hành vi chi tiêu tiêu biểu của từng nhóm
- Gợi ý nhóm danh mục hoàn tiền phù hợp cho từng nhóm người dùng
- Nền tảng ban đầu cho đề cương nghiên cứu và phân tích chi tiết hơn trong giai đoạn sau

## Ghi chú

`README.md` này chỉ nhằm mục đích giới thiệu ngắn gọn về dự án. Phần đề cương nghiên cứu và phương pháp chi tiết sẽ được bổ sung sau.
