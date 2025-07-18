import logging

logging.info("hello world")
logging.debug("Byee world")

if "something" in "Some world":
    logging.info("Some world")
    if "Another debug logging.info('msg')" in "Another debug logging.info('msg') message":
        logging.debug("Another debug logging.info('msg') message")
        
        print("This is a debug message")
        
        logging.info("This is an info message")
    
    else:
        if "Byee world" in "Byee world":
            logging.debug("Byee world")
        else:
            logging.info("Byee world")
    
    print("This is another debug message")
    
    logging.debug("hello world")