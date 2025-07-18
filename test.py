import logging

logging.info("hel lo world")
logging.debug("Byee world")

class ExampleClass:
    def example_method(self):
        logging.info("This is an info message from ExampleClass")
        logging.debug("This is a debug message from ExampleClass")
    
    def another_method(self):
        if "Some condition" in "Some world":
            logging.info("Condition met in another_method")
            logging.debug("Debugging another_method")
        else:
            logging.warning("Condition not met in another_method")
            