
import sys
import traceback
from logger.custom_logger import CustomLogger


logger = CustomLogger().get_logger(__file__)

class TripPlannerPortalException(Exception):
    """Custom exception for Trip Planner"""

    def __init__(self, error_message: str, error_details: sys = None):
        _, _, exc_tb = error_details.exc_info()
        self.file_name = exc_tb.tb_frame.f_code.co_filename if exc_tb else "Unknown"
        self.lineno = exc_tb.tb_lineno if exc_tb else -1
        self.error_message = str(error_message)
        self.traceback_str = ''.join(traceback.format_exception(*error_details.exc_info()))

    def __str__(self):
        return (
            f"Error in [{self.file_name}] at line [{self.lineno}]\n"
            f"Message: {self.error_message}\n"
            f"Traceback:\n{self.traceback_str}"
        )
    
if __name__ == "__main__":
    try:
        # Simulate an error
        a = 1/0
        print(a)
    except Exception as e:
        app_exc = TripPlannerPortalException(e, sys)
        logger.error(app_exc)
        raise app_exc
