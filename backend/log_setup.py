import logging

def logger_setup(name,file_name):

    logger=logging.getLogger(name) #Configure the logger for debugging and errors
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        file_handler=logging.FileHandler(file_name)
        formatter=logging.Formatter("%(asctime)s- %(name)s - %(levelname)s - %(message)s\n")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    return logger