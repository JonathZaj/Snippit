# Global Variables Here
PORT = 5000
HOST = "localhost"
DATABASE = "snippit"
MYSQL_USERNAME = "python"
MYSQL_PASSWORD = "pass"

# logging_enabled = False


# This class offers colors when printing stuff in terminal
class TerminalColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def output(message, severity="Info"):
    """Output function - prints and saves to logfile if enabled"""
    print(message)

    # if logging_enabled:
    #     for val in TerminalColors.__dict__.keys():
    #         if val[:2] != '__':
    #             message = message.replace(getattr(TerminalColors, val), '')
    #     if severity == 'Info':
    #         logging.info('%s:\t%s' % (str(datetime.datetime.now()), message))
    #     elif severity == 'Error':
    #         logging.error(message)
