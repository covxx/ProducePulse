import time
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

# Middleware to calculate the time taken to process a request, for stats page
class RequestTimingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            total_time = time.time() - request.start_time
            response['X-Request-Duration-ms'] = int(total_time * 1000)
            # You can also log this information if needed
            # logger.info(f"Request took {total_time * 1000}ms")
        return response
# Middleware to calculate the request rate per minute, for stats page
class RequestRateMiddleware(MiddlewareMixin):
    def process_request(self, request):
        current_minute = time.strftime("%Y-%m-%d %H:%M")
        request_count = cache.get(current_minute, 0)
        cache.set(current_minute, request_count + 1, timeout=60)

    def process_response(self, request, response):
        current_minute = time.strftime("%Y-%m-%d %H:%M")
        request_count = cache.get(current_minute, 0)
        response['X-Request-Rate'] = request_count
        return response