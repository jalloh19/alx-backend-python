"""
Custom Middleware for Django Messaging App
"""
import logging
from datetime import datetime, time
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from collections import defaultdict
from time import time as current_time


# Configure logging for request logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler for logging
file_handler = logging.FileHandler('requests.log')
file_handler.setLevel(logging.INFO)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
if not logger.handlers:
    logger.addHandler(file_handler)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that logs each user's requests to a file,
    including the timestamp, user, and the request path.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Get user information
        if request.user.is_authenticated:
            user = request.user.username
        else:
            user = "Anonymous"
        
        # Log the request
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        
        # Process the request
        response = self.get_response(request)
        
        return response


class RestrictAccessByTimeMiddleware(MiddlewareMixin):
    """
    Middleware that restricts access to the messaging app during certain hours.
    Access is denied outside of 9 AM to 6 PM.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Get current server time
        current_hour = datetime.now().time()
        
        # Define allowed time window (9 AM to 6 PM)
        start_time = time(9, 0)  # 9:00 AM
        end_time = time(18, 0)   # 6:00 PM
        
        # Check if current time is within allowed window
        if not (start_time <= current_hour <= end_time):
            return JsonResponse(
                {
                    'error': 'Access forbidden',
                    'message': 'Chat access is restricted outside of 9 AM to 6 PM',
                    'current_time': current_hour.strftime('%H:%M:%S')
                },
                status=403
            )
        
        # Process the request if within allowed time
        response = self.get_response(request)
        
        return response


class OffensiveLanguageMiddleware(MiddlewareMixin):
    """
    Middleware that limits the number of chat messages a user can send
    within a certain time window, based on their IP address.
    Rate limit: 5 messages per minute per IP address.
    """
    
    # Class-level storage for request tracking
    ip_requests = defaultdict(list)
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_requests = 5  # Maximum requests per time window
        self.time_window = 60  # Time window in seconds (1 minute)
        super().__init__(get_response)
    
    def __call__(self, request):
        # Only check POST requests (message sending)
        if request.method == 'POST':
            # Get client IP address
            ip_address = self.get_client_ip(request)
            
            # Get current timestamp
            now = current_time()
            
            # Clean old requests outside the time window
            self.ip_requests[ip_address] = [
                timestamp for timestamp in self.ip_requests[ip_address]
                if now - timestamp < self.time_window
            ]
            
            # Check if user has exceeded rate limit
            if len(self.ip_requests[ip_address]) >= self.max_requests:
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded',
                        'message': f'You can only send {self.max_requests} messages per minute',
                        'retry_after': f'{self.time_window} seconds'
                    },
                    status=429  # Too Many Requests
                )
            
            # Add current request timestamp
            self.ip_requests[ip_address].append(now)
        
        # Process the request
        response = self.get_response(request)
        
        return response
    
    def get_client_ip(self, request):
        """Get the client's IP address from the request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolepermissionMiddleware(MiddlewareMixin):
    """
    Middleware that checks the user's role before allowing access to specific actions.
    Only admin and moderator users can access certain endpoints.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Define paths that require admin/moderator role
        self.protected_paths = [
            '/api/conversations/',
            '/api/messages/',
        ]
        super().__init__(get_response)
    
    def __call__(self, request):
        # Check if the request path requires role verification
        requires_role_check = any(
            request.path.startswith(path) for path in self.protected_paths
        )
        
        if requires_role_check:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse(
                    {
                        'error': 'Authentication required',
                        'message': 'You must be logged in to access this resource'
                    },
                    status=401
                )
            
            # Check if user has the required role
            user_role = getattr(request.user, 'role', None)
            
            # Allow access only for admin and moderator roles
            if user_role not in ['admin', 'moderator']:
                return JsonResponse(
                    {
                        'error': 'Permission denied',
                        'message': 'Only admin and moderator users can access this resource',
                        'your_role': user_role or 'No role assigned'
                    },
                    status=403
                )
        
        # Process the request
        response = self.get_response(request)
        
        return response
