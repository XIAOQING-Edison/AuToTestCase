"""
OCR API模块
负责图片文字识别功能，将上传的图片转化为文本
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import tempfile
import os
import uuid
import logging
import sys
import traceback
from PIL import Image, ImageEnhance, ImageFilter
import io
import numpy as np

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ocr_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("OCR_API")

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

router = APIRouter()

# 存储OCR任务状态的字典
ocr_task_status = {}

def preprocess_image(image_path):
    """
    对图像进行预处理，以提高OCR识别率
    包括：调整对比度、锐化、去噪、二值化等
    """
    try:
        # 打开图像
        image = Image.open(image_path)
        
        # 创建处理后图像的保存路径
        preprocessed_path = f"{image_path}_preprocessed.jpg"
        
        # 转换为灰度图像
        if image.mode != 'L':
            image = image.convert('L')
            
        # 增强对比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)  # 对比度增强2倍
        
        # 锐化图像
        image = image.filter(ImageFilter.SHARPEN)
        
        # 去噪：使用中值滤波
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        # 保存预处理后的图像
        image.save(preprocessed_path)
        logger.info(f"图像预处理完成，保存到: {preprocessed_path}")
        
        return preprocessed_path
    except Exception as e:
        logger.error(f"图像预处理失败: {e}")
        return image_path  # 如果处理失败，返回原始图像路径

def perform_ocr_easyocr(image_path):
    """
    使用EasyOCR进行图片文字识别
    """
    try:
        import easyocr
        logger.info("使用EasyOCR进行文字识别")
        
        try:
            reader = easyocr.Reader(['ch_sim', 'en'])  # 支持中文和英文
            results = reader.readtext(image_path)
            
            # 提取文字
            if results:
                extracted_text = "\n".join([text[1] for text in results])
                logger.info(f"EasyOCR识别结果 ({len(results)}个区域): {extracted_text[:100]}...")
                return extracted_text
            else:
                logger.warning("EasyOCR未检测到任何文字")
                return None
        except Exception as e:
            logger.error(f"EasyOCR处理失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    except ImportError:
        logger.warning("EasyOCR未安装，尝试其他OCR方法")
        return None

def perform_ocr_pytesseract(image_path):
    """
    使用Pytesseract进行图片文字识别
    """
    try:
        import pytesseract
        from PIL import Image
        
        logger.info("使用Pytesseract进行文字识别")
        
        try:
            image = Image.open(image_path)
            
            # 尝试使用不同的语言识别
            try:
                # 首先尝试中文+英文
                logger.info("尝试使用中文+英文识别")
                text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            except Exception as e:
                logger.warning(f"中文+英文识别失败: {e}，尝试仅使用英文")
                # 如果失败，只使用英文
                text = pytesseract.image_to_string(image, lang='eng')
                
            logger.info(f"Pytesseract识别结果: {text[:100]}...")
            return text
        except Exception as e:
            logger.error(f"Pytesseract处理图片失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    except Exception as e:
        logger.error(f"Pytesseract OCR错误: {e}")
        return None

def process_image_ocr(task_id, image_path):
    """
    处理OCR任务
    """
    preprocessed_path = None
    
    try:
        # 更新任务状态
        ocr_task_status[task_id] = {
            "status": "processing",
            "progress": 10,
            "message": "正在准备识别..."
        }
        
        # 检查图片是否有效
        try:
            logger.info(f"验证图片: {image_path}")
            img = Image.open(image_path)
            img.verify()  # 验证图片完整性
            
            # 获取图片信息
            width, height = img.size
            format = img.format
            mode = img.mode
            logger.info(f"图片有效: {width}x{height}, 格式={format}, 模式={mode}")
            
            ocr_task_status[task_id]["progress"] = 20
            ocr_task_status[task_id]["message"] = "图片有效，开始预处理..."
        except Exception as e:
            logger.error(f"无效的图片: {e}")
            import traceback
            logger.error(traceback.format_exc())
            ocr_task_status[task_id] = {
                "status": "failed",
                "progress": 0,
                "message": f"无效的图片: {str(e)}"
            }
            return
        
        # 图像预处理
        ocr_task_status[task_id]["progress"] = 30
        ocr_task_status[task_id]["message"] = "正在预处理图片，提高识别率..."
        preprocessed_path = preprocess_image(image_path)
        
        # 尝试使用pytesseract进行OCR
        logger.info("开始OCR处理")
        ocr_task_status[task_id]["progress"] = 40
        ocr_task_status[task_id]["message"] = "正在使用Pytesseract识别..."
        
        text = perform_ocr_pytesseract(preprocessed_path)
        
        # 如果pytesseract失败，尝试使用easyocr
        if not text or len(text.strip()) < 5:  # 如果文本太短或为空，认为识别失败
            ocr_task_status[task_id]["progress"] = 60
            ocr_task_status[task_id]["message"] = "Pytesseract识别失败，尝试使用EasyOCR识别..."
            logger.info("Pytesseract识别失败，切换到EasyOCR")
            text = perform_ocr_easyocr(preprocessed_path)
            
            # 如果EasyOCR也失败，尝试对原始图像进行OCR
            if not text or len(text.strip()) < 5:
                logger.info("尝试对原始图像进行OCR识别")
                ocr_task_status[task_id]["message"] = "尝试对原始图像进行OCR识别..."
                text = perform_ocr_easyocr(image_path)
        
        # 检查识别结果
        if text and len(text.strip()) > 5:  # 确保有足够的文本被识别出来
            ocr_task_status[task_id]["progress"] = 90
            ocr_task_status[task_id]["message"] = "正在整理识别结果..."
            
            # 过滤和清理文本
            text = text.strip()
            
            # 更新任务状态为完成
            ocr_task_status[task_id] = {
                "status": "completed",
                "progress": 100,
                "message": "文字识别完成",
                "text": text
            }
            
            logger.info(f"OCR任务 {task_id} 完成，文本长度: {len(text)}")
        else:
            # 如果两种方法都失败
            logger.error(f"OCR任务 {task_id} 失败: 无法识别文字")
            ocr_task_status[task_id] = {
                "status": "failed",
                "progress": 0,
                "message": "无法识别图片中的文字，请检查图片质量或手动输入"
            }
            return
        
    except Exception as e:
        logger.error(f"OCR任务 {task_id} 失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # 更新任务状态为失败
        ocr_task_status[task_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"文字识别失败: {str(e)}"
        }
    finally:
        # 清理临时文件
        try:
            logger.info(f"清理临时文件: {image_path}")
            os.unlink(image_path)
            # 清理预处理后的图像
            if preprocessed_path and os.path.exists(preprocessed_path):
                logger.info(f"清理预处理图像: {preprocessed_path}")
                os.unlink(preprocessed_path)
        except Exception as e:
            logger.warning(f"清理临时文件失败: {e}")

@router.post("/recognize")
async def recognize_image(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    上传图片进行文字识别
    """
    # 验证文件格式
    valid_formats = ['image/jpeg', 'image/png', 'image/jpg', 'image/bmp', 'image/tiff']
    if file.content_type not in valid_formats:
        raise HTTPException(status_code=400, detail=f"不支持的图片格式: {file.content_type}，请上传JPG, PNG, BMP或TIFF格式")
    
    # 保存上传的图片到临时文件
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    try:
        # 读取上传的文件内容
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        # 生成唯一标识符作为任务ID
        task_id = str(uuid.uuid4())
        
        # 初始化任务状态
        ocr_task_status[task_id] = {
            "status": "queued",
            "progress": 0,
            "message": "任务已加入队列"
        }
        
        # 在后台执行文字识别
        background_tasks.add_task(
            process_image_ocr,
            task_id,
            temp_file.name
        )
        
        # 返回任务ID
        return {"task_id": task_id}
        
    except Exception as e:
        logger.error(f"图片识别失败: {str(e)}")
        logger.error(traceback.format_exc())
        
        # 清理临时文件
        try:
            os.unlink(temp_file.name)
        except:
            pass
            
        raise HTTPException(status_code=500, detail=f"图片识别失败: {str(e)}")

@router.get("/status/{task_id}")
async def get_ocr_status(task_id: str):
    """
    获取OCR任务状态
    """
    if task_id not in ocr_task_status:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    return ocr_task_status[task_id] 