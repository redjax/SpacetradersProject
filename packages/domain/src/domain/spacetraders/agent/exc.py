class AgentAlreadyRegisteredException(Exception):
    """Exception raised when a Spacetraders agent register request returns a 409: Conflict.
    
    Attributes:
        message (str): The message to print when the exception is raised.
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        
        # super().__init__(message)
        
    def __str__(self):
        return f"Agent symbol has already been registered: {self.symbol}"
