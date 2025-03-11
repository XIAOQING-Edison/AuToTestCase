from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import os
import sys
import shutil
from typing import Optional, Dict
import uuid
import time
import json
import logging

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_case_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TestCaseAPI")

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入核心功能
try:
    from src.core.test_generator import TestGenerator  # 假设您的项目中有这个模块
    from src.core.llm_engine import LLMEngine
    from src.exporters.excel_exporter import ExcelExporter
    from src.exporters.xmind_exporter import XMindExporter
except ImportError as e:
    logger.error(f"导入错误: {e}")

router = APIRouter()

# 存储任务状态的字典
task_status = {}

def read_file_content(file_path):
    """读取文件内容"""
    try:
        # 首先尝试以文本模式读取
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # 如果不是UTF-8编码，尝试以二进制模式读取并解码
            with open(file_path, 'rb') as f:
                content = f.read()
                # 尝试不同的编码
                for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                    try:
                        return content.decode(encoding)
                    except UnicodeDecodeError:
                        continue
                # 如果所有编码都失败，使用latin-1（它可以解码任何字节序列）
                return content.decode('latin-1')
    except Exception as e:
        logger.error(f"读取文件错误: {e}")
        return ""

def generate_test_cases_background(task_id: str, file_path: str, output_file: str, output_type: str):
    """在后台执行测试用例生成任务"""
    try:
        # 更新任务状态
        task_status[task_id] = {
            "status": "processing",
            "progress": 10,
            "message": "正在初始化LLM引擎..."
        }
        
        # 创建LLM引擎实例
        llm_engine = LLMEngine()
        
        task_status[task_id]["progress"] = 20
        task_status[task_id]["message"] = "正在分析需求文档..."
        
        # 调用测试用例生成器
        generator = TestGenerator(llm_engine)
        
        task_status[task_id]["progress"] = 30
        task_status[task_id]["message"] = "正在生成测试用例..."
        
        # 生成测试用例
        test_cases = generator.generate(file_path)
        
        task_status[task_id]["progress"] = 70
        task_status[task_id]["message"] = "正在导出测试用例..."
        
        # 导出测试用例
        if output_type == "excel":
            exporter = ExcelExporter()
            exporter.export(test_cases, output_file)
        elif output_type == "xmind":
            exporter = XMindExporter()
            exporter.export(test_cases, output_file)
        
        # 更新任务状态为完成
        task_status[task_id] = {
            "status": "completed",
            "progress": 100,
            "message": "测试用例生成完成",
            "output_file": output_file,
            "output_type": output_type
        }
        
        logger.info(f"任务 {task_id} 完成: {output_file}")
        
    except Exception as e:
        logger.error(f"任务 {task_id} 失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # 更新任务状态为失败
        task_status[task_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"生成测试用例失败: {str(e)}"
        }

@router.post("/generate-from-file")
async def generate_from_file(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    output_format: str = Form("excel"),
):
    """
    从上传的需求文档文件生成测试用例
    """
    # 保存上传的文件到临时目录
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md")
    try:
        # 读取上传的文件内容
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        # 创建输出目录
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "output", "web_generated")
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成唯一标识符作为任务ID和文件名
        task_id = str(uuid.uuid4())
        
        # 根据选择的格式确定输出文件路径
        if output_format.lower() == "excel":
            output_file = os.path.join(output_dir, f"{task_id}.xlsx")
            output_type = "excel"
        elif output_format.lower() == "xmind":
            output_file = os.path.join(output_dir, f"{task_id}.xmind")
            output_type = "xmind"
        else:
            raise HTTPException(status_code=400, detail=f"不支持的输出格式: {output_format}")
        
        # 初始化任务状态
        task_status[task_id] = {
            "status": "queued",
            "progress": 0,
            "message": "任务已加入队列"
        }
        
        # 在后台执行测试用例生成
        background_tasks.add_task(
            generate_test_cases_background,
            task_id,
            temp_file.name,
            output_file,
            output_type
        )
        
        # 返回任务ID
        return {"task_id": task_id}
        
    except Exception as e:
        logger.error(f"生成测试用例失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # 清理临时文件
        try:
            os.unlink(temp_file.name)
        except:
            pass
            
        raise HTTPException(status_code=500, detail=f"生成测试用例失败: {str(e)}")

@router.post("/generate-from-text")
async def generate_from_text(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    output_format: str = Form("excel"),
):
    """
    从直接输入的需求文本生成测试用例
    """
    # 创建临时文件保存需求文本
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md")
    try:
        # 写入文本内容
        temp_file.write(text.encode('utf-8'))
        temp_file.close()
        
        # 创建输出目录
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "output", "web_generated")
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成唯一标识符作为任务ID和文件名
        task_id = str(uuid.uuid4())
        
        # 根据选择的格式确定输出文件路径
        if output_format.lower() == "excel":
            output_file = os.path.join(output_dir, f"{task_id}.xlsx")
            output_type = "excel"
        elif output_format.lower() == "xmind":
            output_file = os.path.join(output_dir, f"{task_id}.xmind")
            output_type = "xmind"
        else:
            raise HTTPException(status_code=400, detail=f"不支持的输出格式: {output_format}")
        
        # 初始化任务状态
        task_status[task_id] = {
            "status": "queued",
            "progress": 0,
            "message": "任务已加入队列"
        }
        
        # 在后台执行测试用例生成
        background_tasks.add_task(
            generate_test_cases_background,
            task_id,
            temp_file.name,
            output_file,
            output_type
        )
        
        # 返回任务ID
        return {"task_id": task_id}
        
    except Exception as e:
        logger.error(f"生成测试用例失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # 清理临时文件
        try:
            os.unlink(temp_file.name)
        except:
            pass
            
        raise HTTPException(status_code=500, detail=f"生成测试用例失败: {str(e)}")

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    获取任务状态
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    return task_status[task_id]

@router.get("/download/{task_id}")
async def download_result(task_id: str):
    """
    下载生成的测试用例文件
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    task_info = task_status[task_id]
    
    if task_info["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"任务 {task_id} 尚未完成")
    
    output_file = task_info["output_file"]
    output_type = task_info["output_type"]
    
    if not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail=f"文件 {output_file} 不存在")
    
    return FileResponse(
        path=output_file,
        filename=f"test_cases.{output_type}",
        media_type="application/octet-stream"
    ) 