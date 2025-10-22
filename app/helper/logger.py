import logging
import os
from datetime import datetime

def get_logger(name:str,base_log_dir: str = 'log_file', log_to_file: bool = True)->logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # Neu Logger da co Hanlder roi thi khong can them nua
    if logger.handlers:
        return logger

    # Format for log
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    # File Handler
    if log_to_file:
        # Tao thu muc theo module
        module_dir = os.path.join(base_log_dir,name)
        os.makedirs(module_dir,exist_ok= True)
        
        
        log_path  = os.path.join(module_dir,f"{name}.log")
        
        file_handler = logging.FileHandler(log_path,encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    

    
    return logger

