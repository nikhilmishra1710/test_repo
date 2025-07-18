import logging

logging.debug("hel lo world")
logging.info("Byee world logging.info('Byee world')")

class LoggingInfoClass:
    def log_info(self):
        logging.info("This is an info message from LoggingInfoClass")
        logging.debug("This is a debug message from LoggingInfoClass")
    
    def another_log_method(self):
        if "Some condition" in "Some world":
            logging.info("Condition met in another_log_method") #--- IGNORE ---
            logging.debug("Debugging another_log_method")
        else:
            logging.warning("Condition not met in another_log_method")