import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from models.template_manager import TemplateManager
from models.dashboard_manager import DashboardManager

class ReportManager:
    def __init__(self):
        self.template_manager = TemplateManager()
        self.dashboard_manager = DashboardManager()
        
    def generate_report(self, template_id, model_id, start_date, end_date, output_path):
        """Tạo báo cáo từ template"""
        try:
            # Lấy thông tin template
            templates = self.template_manager.get_all_templates()
            template = next((t for t in templates if t['id'] == template_id), None)
            if not template:
                raise ValueError("Không tìm thấy template")
                
            # Lấy dữ liệu đo
            parameters = self.dashboard_manager.get_parameters_by_model(model_id)
            measurements = {}
            statistics = {}
            
            for param in parameters:
                data = self.dashboard_manager.get_measurement_data(
                    param['id'],
                    start_date,
                    end_date
                )
                measurements[param['name']] = data
                
                # Tính toán thống kê
                stats = self.dashboard_manager.get_parameter_statistics(
                    param['id'],
                    start_date,
                    end_date
                )
                statistics[param['name']] = stats
                
            # Đọc template
            df_template = pd.read_excel(template['file_path'])
            
            # Tạo báo cáo mới
            df_report = df_template.copy()
            
            # Điền dữ liệu vào báo cáo
            for param_name, data in measurements.items():
                if not data:
                    continue
                    
                # Tìm cột tương ứng trong template
                col_idx = None
                for i, col in enumerate(df_template.columns):
                    if param_name.lower() in col.lower():
                        col_idx = i
                        break
                        
                if col_idx is not None:
                    # Điền giá trị đo
                    for i, row in enumerate(data):
                        if i < len(df_report):
                            df_report.iloc[i, col_idx] = row['value']
                            
            # Thêm thông tin báo cáo
            df_report.insert(0, 'Ngày tạo', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            df_report.insert(1, 'Từ ngày', start_date.strftime('%Y-%m-%d'))
            df_report.insert(2, 'Đến ngày', end_date.strftime('%Y-%m-%d'))
            
            # Tạo thư mục cho biểu đồ
            charts_dir = os.path.join(os.path.dirname(output_path), 'charts')
            os.makedirs(charts_dir, exist_ok=True)
            
            # Tạo biểu đồ cho từng thông số
            for param_name, data in measurements.items():
                if not data:
                    continue
                    
                # Tạo biểu đồ đường thời gian
                plt.figure(figsize=(10, 6))
                dates = [row['timestamp'] for row in data]
                values = [row['value'] for row in data]
                plt.plot(dates, values)
                plt.title(f'Biểu đồ {param_name}')
                plt.xlabel('Thời gian')
                plt.ylabel('Giá trị')
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # Lưu biểu đồ
                chart_path = os.path.join(charts_dir, f'{param_name}_timeline.png')
                plt.savefig(chart_path)
                plt.close()
                
                # Tạo biểu đồ phân phối
                plt.figure(figsize=(10, 6))
                plt.hist(values, bins=20)
                plt.title(f'Phân phối {param_name}')
                plt.xlabel('Giá trị')
                plt.ylabel('Tần suất')
                plt.tight_layout()
                
                # Lưu biểu đồ
                chart_path = os.path.join(charts_dir, f'{param_name}_distribution.png')
                plt.savefig(chart_path)
                plt.close()
                
            # Tạo sheet thống kê
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df_report.to_excel(writer, sheet_name='Dữ liệu', index=False)
                
                # Tạo sheet thống kê
                stats_data = []
                for param_name, stats in statistics.items():
                    stats_data.append({
                        'Thông số': param_name,
                        'Giá trị nhỏ nhất': stats['min'],
                        'Giá trị lớn nhất': stats['max'],
                        'Giá trị trung bình': stats['mean'],
                        'Độ lệch chuẩn': stats['std'],
                        'Số lượng mẫu': stats['count']
                    })
                    
                df_stats = pd.DataFrame(stats_data)
                df_stats.to_excel(writer, sheet_name='Thống kê', index=False)
                
            return True
            
        except Exception as e:
            print(f"Lỗi khi tạo báo cáo: {e}")
            return False
            
    def get_report_templates(self):
        """Lấy danh sách template có thể dùng để tạo báo cáo"""
        return self.template_manager.get_all_templates()
        
    def export_to_pdf(self, excel_path, pdf_path):
        """Xuất báo cáo ra file PDF"""
        try:
            # Đọc file Excel
            df_data = pd.read_excel(excel_path, sheet_name='Dữ liệu')
            df_stats = pd.read_excel(excel_path, sheet_name='Thống kê')
            
            # Tạo file PDF
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Thêm tiêu đề
            elements.append(Paragraph("Báo Cáo Đo Lường", styles['Title']))
            elements.append(Paragraph(f"Ngày tạo: {df_data['Ngày tạo'][0]}", styles['Normal']))
            elements.append(Paragraph(f"Từ ngày: {df_data['Từ ngày'][0]}", styles['Normal']))
            elements.append(Paragraph(f"Đến ngày: {df_data['Đến ngày'][0]}", styles['Normal']))
            
            # Thêm bảng thống kê
            elements.append(Paragraph("Thống Kê", styles['Heading1']))
            stats_data = [df_stats.columns.tolist()] + df_stats.values.tolist()
            stats_table = Table(stats_data)
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(stats_table)
            
            # Thêm biểu đồ
            charts_dir = os.path.join(os.path.dirname(excel_path), 'charts')
            if os.path.exists(charts_dir):
                elements.append(Paragraph("Biểu Đồ", styles['Heading1']))
                for file in os.listdir(charts_dir):
                    if file.endswith('.png'):
                        img_path = os.path.join(charts_dir, file)
                        img = Image(img_path, width=400, height=300)
                        elements.append(img)
            
            # Tạo file PDF
            doc.build(elements)
            return True
            
        except Exception as e:
            print(f"Lỗi khi xuất PDF: {e}")
            return False
            
    def export_to_csv(self, excel_path, csv_path):
        """Xuất báo cáo ra file CSV"""
        try:
            # Đọc file Excel
            df_data = pd.read_excel(excel_path, sheet_name='Dữ liệu')
            
            # Xuất ra CSV
            df_data.to_csv(csv_path, index=False, encoding='utf-8-sig')
            return True
            
        except Exception as e:
            print(f"Lỗi khi xuất CSV: {e}")
            return False 