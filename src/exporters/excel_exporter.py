"""
Excel导出器模块
负责将测试用例导出为格式化的Excel文件，支持样式美化和自动调整
"""

from typing import List
import pandas as pd
from src.core.test_generator import TestCase
from src.config import EXCEL_TEMPLATE_HEADERS, OUTPUT_DIR
import os
from openpyxl.styles import Border, Side, Alignment, PatternFill, Font
from openpyxl.utils import get_column_letter

class ExcelExporter:
    def export(self, test_cases: List[TestCase], output_filename: str) -> str:
        """
        Export test cases to Excel format
        
        Args:
            test_cases (List[TestCase]): List of test cases to export
            output_filename (str): Name of the output file
            
        Returns:
            str: Path to the exported file
        """
        # Convert test cases to DataFrame format
        data = []
        for test_case in test_cases:
            steps_str = "\n".join([
                f"{step.step_number}. {step.description}"
                for step in test_case.steps
            ])
            
            expected_results_str = "\n".join([
                f"{step.step_number}. {step.expected_result}"
                for step in test_case.steps
            ])
            
            preconditions_str = "\n".join(test_case.preconditions) if test_case.preconditions else ""
            
            data.append({
                "用例编号": test_case.id,
                "所属模块": test_case.module,
                "用例标题": test_case.title,
                "优先级": test_case.priority,
                "用例类型": test_case.category,
                "前置条件": preconditions_str,
                "测试步骤": steps_str,
                "预期结果": expected_results_str
            })
        
        df = pd.DataFrame(data)
        print(f"\nExporting {len(data)} test cases to Excel")
        print("DataFrame columns:", df.columns.tolist())
        print("DataFrame shape:", df.shape)
        
        # Ensure columns are in the correct order
        df = df.reindex(columns=EXCEL_TEMPLATE_HEADERS)
        
        # Create output path
        if not output_filename.endswith('.xlsx'):
            output_filename += '.xlsx'
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # Export to Excel with formatting
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Test Cases')
            
            # Get the workbook and the worksheet
            workbook = writer.book
            worksheet = writer.sheets['Test Cases']
            
            # Define styles
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            header_fill = PatternFill(
                start_color='4472C4',
                end_color='4472C4',
                fill_type='solid'
            )
            
            header_font = Font(
                name='Arial',
                size=11,
                bold=True,
                color='FFFFFF'
            )
            
            data_font = Font(
                name='Arial',
                size=10
            )
            
            # Set column widths
            column_widths = {
                '用例编号': 40,
                '所属模块': 20,
                '用例标题': 40,
                '优先级': 15,
                '用例类型': 15,
                '前置条件': 40,
                '测试步骤': 60,
                '预期结果': 60
            }
            
            for i, column in enumerate(EXCEL_TEMPLATE_HEADERS, 1):
                col_letter = get_column_letter(i)
                worksheet.column_dimensions[col_letter].width = column_widths[column]
            
            # Apply styles to header
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.border = border
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            
            # Apply styles to data cells
            for row in worksheet.iter_rows(min_row=2):
                for cell in row:
                    cell.border = border
                    cell.font = data_font
                    cell.alignment = Alignment(vertical='top', wrap_text=True)
                    
                    # Center align Priority and Category columns
                    if cell.column_letter in [get_column_letter(4), get_column_letter(5)]:  # Priority and Category columns
                        cell.alignment = Alignment(horizontal='center', vertical='top', wrap_text=True)
            
            # Set row height
            worksheet.row_dimensions[1].height = 30  # Header row
            for i in range(2, worksheet.max_row + 1):  # Data rows
                worksheet.row_dimensions[i].height = 100
        
        return output_path 