from django.utils.deprecation import MiddlewareMixin
import logging
import time

import gzip


logger = logging.getLogger(__name__)


class RequestResponseLoggerMiddleware(MiddlewareMixin):
    """
    Middleware to log detailed information about each incoming request and response.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        """
        Called before the view function is called.
        """
        request.start_time = time.time()
        logger.info(
            f"Incoming Request: {request.method} {request.path} from {request.META.get('REMOTE_ADDR')}"
        )

    def process_response(self, request, response):
        """
        Called just before Django sends the response to the client.
        """
        end_time = time.time()
        logger.info(
            f"Outgoing Response: {response.status_code} {response['content-type']} in {end_time - request.start_time:.2f}s"
        )
        return response


class SecurityMiddleware:
    """
    Middleware to implement security headers and enforce HSTS.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response["Content-Security-Policy"] = "default-src 'self'"
        response["X-Content-Type-Options"] = "nosniff"

        response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


class RateLimitingMiddleware(MiddlewareMixin):
    """
    Middleware to limit the number of requests a user can make within a specific time frame.
    """

    def __init__(self, get_response, limit=5, window=60):
        self.get_response = get_response
        self.limit = limit
        self.window = window

    def process_request(self, request):
        """
        Called before the view function is called.
        """
        # Your rate limiting logic here
        pass

    def process_response(self, request, response):
        """
        Called just before Django sends the response to the client.
        """
        # Your rate limiting logic here
        return response


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to log the time taken by each view function.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Called just before Django calls the view function.
        """
        request.start_time = time.time()

    def process_response(self, request, response):
        """
        Called just before Django sends the response to the client.
        """
        end_time = time.time()

        # Check if resolver_match is not None before accessing its attributes
        if request.resolver_match:
            logger.info(
                f"View function '{request.resolver_match.url_name}' took {end_time - request.start_time:.2f}s"
            )
        else:
            logger.info(
                f"No URL match found for the current request. Took {end_time - request.start_time:.2f}s"
            )

        return response


class CustomAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware for custom authentication based on a special header.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        """
        Called before the view function is called.
        """
        # Your authentication logic here
        pass

    def process_response(self, request, response):
        """
        Called just before Django sends the response to the client.
        """
        # Your authentication logic here
        return response


class IPWhitelistMiddleware(MiddlewareMixin):
    """
    Middleware to allow or deny access based on IP whitelisting.
    """

    def __init__(self, get_response, allowed_ips=None):
        self.get_response = get_response
        self.allowed_ips = set(allowed_ips or [])

    def process_request(self, request):
        """
        Called before the view function is called.
        """
        # Your IP whitelist logic here
        pass

    def process_response(self, request, response):
        """
        Called just before Django sends the response to the client.
        """
        # Your IP whitelist logic here
        return response

    def process_response(self, request, response):
        """
        Called just before Django sends the response to the client.
        """
        return response


class CompressionMiddleware(MiddlewareMixin):
    """
    Middleware to compress responses for improved performance.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        """
        Called before the view function is called.
        """
        request.supports_gzip = "gzip" in request.META.get("HTTP_ACCEPT_ENCODING", "")

    def process_response(self, request, response):
        """
        Called just before Django sends the response to the client.
        """
        if self.should_compress(request, response):
            response = self.compress_response(response)
        return response

    def should_compress(self, request, response):
        """
        Check if the response should be compressed.
        """
        return getattr(request, "supports_gzip", False) and self.is_compressible(
            response
        )

    def is_compressible(self, response):
        """
        Check if the response content is compressible.
        """
        content_type = response.get("Content-Type", "").lower()
        return (
            "text/html" in content_type
            or "text/css" in content_type
            or "application/javascript" in content_type
        )

    def compress_response(self, response):
        """
        Compress the response content using gzip.
        """
        content = response.content

        if isinstance(content, str):
            content = content.encode("utf-8")

        compressed_content = gzip.compress(content)
        response.content = compressed_content

        response["Content-Encoding"] = "gzip"
        response["Content-Length"] = str(len(compressed_content))

        return response


class CacheControlMiddleware(MiddlewareMixin):
    """
    Middleware to add Cache-Control headers for caching strategies.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        """
        Called before the view function is called.
        """
        # Your cache control logic here (if needed)
        # For example, you might want to set specific cache headers based on the request
        request.custom_cache_control = {
            "max_age": 3600,  # Cache for 1 hour
            "public": True,  # Allow caching by public caches
            "no_cache": False,  # Allow caching but revalidate with the server
            "no_store": False,  # Allow caching but do not store a cached copy
        }

    def process_response(self, request, response):
        """
        Called just before Django sends the response to the client.
        """
        # Your cache control logic here (if needed)
        cache_control_settings = getattr(request, "custom_cache_control", None)

        if cache_control_settings:
            cache_control_header = self.build_cache_control_header(
                cache_control_settings
            )
            response["Cache-Control"] = cache_control_header

        return response

    def build_cache_control_header(self, settings):
        """
        Build the Cache-Control header string based on the provided settings.
        """
        parts = []
        if "max_age" in settings:
            parts.append(f'max-age={settings["max_age"]}')
        if "public" in settings and settings["public"]:
            parts.append("public")
        if "no_cache" in settings and settings["no_cache"]:
            parts.append("no-cache")
        if "no_store" in settings and settings["no_store"]:
            parts.append("no-store")

        return ", ".join(parts)
