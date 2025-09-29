"""
Comprehensive Error Handling and Retry Logic

This module implements robust error handling and retry mechanisms
for the Recipe Enhancement Pipeline validation framework.
"""

import time
import logging
import json
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type
from dataclasses import dataclass
from enum import Enum

class ErrorCategory(Enum):
    """Error categories for classification."""
    NETWORK = "network"
    API_LIMIT = "api_limit"
    VALIDATION = "validation"
    FILE_IO = "file_io"
    PARSING = "parsing"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"

@dataclass
class ErrorStats:
    """Error statistics tracking."""
    total_errors: int = 0
    retries_attempted: int = 0
    successful_retries: int = 0
    failed_after_retries: int = 0
    errors_by_category: Dict[str, int] = None

    def __post_init__(self):
        if self.errors_by_category is None:
            self.errors_by_category = {}

class ErrorClassifier:
    """Classifies errors into categories for appropriate handling."""

    @staticmethod
    def classify_error(exception: Exception) -> ErrorCategory:
        """Classify an exception into an error category."""

        error_msg = str(exception).lower()

        # Network-related errors
        if any(keyword in error_msg for keyword in [
            'connection', 'network', 'timeout', 'unreachable', 'refused'
        ]):
            return ErrorCategory.NETWORK

        # API rate limiting
        if any(keyword in error_msg for keyword in [
            'rate limit', 'quota', 'too many requests', '429'
        ]):
            return ErrorCategory.API_LIMIT

        # File I/O errors
        if any(keyword in error_msg for keyword in [
            'file not found', 'permission denied', 'no such file', 'eisdir'
        ]):
            return ErrorCategory.FILE_IO

        # Parsing errors
        if any(keyword in error_msg for keyword in [
            'json', 'parse', 'decode', 'invalid format', 'syntax'
        ]):
            return ErrorCategory.PARSING

        # Timeout errors
        if any(keyword in error_msg for keyword in [
            'timeout', 'timed out', 'deadline exceeded'
        ]):
            return ErrorCategory.TIMEOUT

        # Validation errors
        if any(keyword in error_msg for keyword in [
            'validation', 'invalid', 'missing', 'required'
        ]):
            return ErrorCategory.VALIDATION

        return ErrorCategory.UNKNOWN

class RetryStrategy:
    """Defines retry strategies for different error categories."""

    def __init__(self):
        self.strategies = {
            ErrorCategory.NETWORK: {
                "max_retries": 3,
                "base_delay": 1.0,
                "backoff_multiplier": 2.0,
                "max_delay": 30.0
            },
            ErrorCategory.API_LIMIT: {
                "max_retries": 5,
                "base_delay": 60.0,  # Wait longer for API limits
                "backoff_multiplier": 1.5,
                "max_delay": 300.0
            },
            ErrorCategory.TIMEOUT: {
                "max_retries": 2,
                "base_delay": 5.0,
                "backoff_multiplier": 2.0,
                "max_delay": 60.0
            },
            ErrorCategory.FILE_IO: {
                "max_retries": 2,
                "base_delay": 0.5,
                "backoff_multiplier": 2.0,
                "max_delay": 5.0
            },
            ErrorCategory.PARSING: {
                "max_retries": 1,  # Usually not worth retrying
                "base_delay": 0.0,
                "backoff_multiplier": 1.0,
                "max_delay": 0.0
            },
            ErrorCategory.VALIDATION: {
                "max_retries": 0,  # Don't retry validation errors
                "base_delay": 0.0,
                "backoff_multiplier": 1.0,
                "max_delay": 0.0
            },
            ErrorCategory.UNKNOWN: {
                "max_retries": 1,
                "base_delay": 1.0,
                "backoff_multiplier": 1.0,
                "max_delay": 5.0
            }
        }

    def get_strategy(self, category: ErrorCategory) -> Dict[str, float]:
        """Get retry strategy for error category."""
        return self.strategies.get(category, self.strategies[ErrorCategory.UNKNOWN])

class ErrorHandler:
    """Comprehensive error handling and retry logic."""

    def __init__(self, log_file: str = "validation_errors.log"):
        self.error_stats = ErrorStats()
        self.classifier = ErrorClassifier()
        self.retry_strategy = RetryStrategy()
        self.error_log: List[Dict[str, Any]] = []

        # Setup logging
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""

        last_exception = None

        # Initial attempt
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            self.error_stats.total_errors += 1

            # Classify error
            category = self.classifier.classify_error(e)
            self.error_stats.errors_by_category[category.value] = \
                self.error_stats.errors_by_category.get(category.value, 0) + 1

            # Log error
            error_info = {
                "function": func.__name__,
                "category": category.value,
                "error": str(e),
                "timestamp": time.time()
            }
            self.error_log.append(error_info)
            self.logger.error(f"Error in {func.__name__}: {e} (Category: {category.value})")

            # Get retry strategy
            strategy = self.retry_strategy.get_strategy(category)
            max_retries = strategy["max_retries"]

            if max_retries == 0:
                self.error_stats.failed_after_retries += 1
                raise e

            # Retry attempts
            for attempt in range(max_retries):
                self.error_stats.retries_attempted += 1

                # Calculate delay
                delay = min(
                    strategy["base_delay"] * (strategy["backoff_multiplier"] ** attempt),
                    strategy["max_delay"]
                )

                if delay > 0:
                    self.logger.info(f"Retrying {func.__name__} in {delay:.1f}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)

                try:
                    result = func(*args, **kwargs)
                    self.error_stats.successful_retries += 1
                    self.logger.info(f"Retry successful for {func.__name__} on attempt {attempt + 1}")
                    return result

                except Exception as retry_exception:
                    last_exception = retry_exception
                    self.logger.warning(f"Retry {attempt + 1} failed for {func.__name__}: {retry_exception}")
                    continue

            # All retries failed
            self.error_stats.failed_after_retries += 1
            self.logger.error(f"All retries failed for {func.__name__}")
            raise last_exception

    def safe_execute(self, func: Callable, *args, default=None, **kwargs) -> Any:
        """Execute function safely with error handling, returning default on failure."""

        try:
            return self.with_retry(func, *args, **kwargs)
        except Exception as e:
            self.logger.warning(f"Function {func.__name__} failed, returning default: {e}")
            return default

    def get_error_report(self) -> Dict[str, Any]:
        """Generate comprehensive error report."""

        success_rate = 1.0
        if self.error_stats.total_errors > 0:
            success_rate = self.error_stats.successful_retries / self.error_stats.total_errors

        return {
            "total_errors": self.error_stats.total_errors,
            "retries_attempted": self.error_stats.retries_attempted,
            "successful_retries": self.error_stats.successful_retries,
            "failed_after_retries": self.error_stats.failed_after_retries,
            "retry_success_rate": success_rate,
            "errors_by_category": self.error_stats.errors_by_category,
            "recent_errors": self.error_log[-10:],  # Last 10 errors
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on error patterns."""

        recommendations = []

        # Check for high network errors
        network_errors = self.error_stats.errors_by_category.get(ErrorCategory.NETWORK.value, 0)
        if network_errors > 5:
            recommendations.append("Consider implementing connection pooling or checking network stability")

        # Check for API limit issues
        api_errors = self.error_stats.errors_by_category.get(ErrorCategory.API_LIMIT.value, 0)
        if api_errors > 2:
            recommendations.append("Consider implementing request throttling or upgrading API limits")

        # Check for parsing errors
        parsing_errors = self.error_stats.errors_by_category.get(ErrorCategory.PARSING.value, 0)
        if parsing_errors > 3:
            recommendations.append("Review data formats and add validation before parsing")

        # Check for file I/O errors
        file_errors = self.error_stats.errors_by_category.get(ErrorCategory.FILE_IO.value, 0)
        if file_errors > 2:
            recommendations.append("Check file permissions and paths, ensure directories exist")

        # Overall retry success rate
        if self.error_stats.total_errors > 0:
            success_rate = self.error_stats.successful_retries / self.error_stats.total_errors
            if success_rate < 0.5:
                recommendations.append("Low retry success rate - consider reviewing error handling strategies")

        if not recommendations:
            recommendations.append("Error handling is performing well")

        return recommendations

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for adding retry logic to functions."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            error_handler = ErrorHandler()
            return error_handler.with_retry(func, *args, **kwargs)
        return wrapper
    return decorator

def safe_operation(default=None):
    """Decorator for safe operation execution with default fallback."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            error_handler = ErrorHandler()
            return error_handler.safe_execute(func, *args, default=default, **kwargs)
        return wrapper
    return decorator

# Example usage and testing
class ValidationErrorHandling:
    """Example implementation of error handling in validation context."""

    def __init__(self):
        self.error_handler = ErrorHandler("validation_errors.log")

    def validate_recipe_with_api(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Example: Validate recipe using external API (simulated)."""

        # Simulate potential API failures
        import random
        if random.random() < 0.1:  # Reduced failure rate for testing
            if random.random() < 0.5:
                raise Exception("Connection timeout - network error")
            else:
                raise Exception("Rate limit exceeded - too many requests")

        return {"status": "valid", "score": 0.95}

    @safe_operation(default=[])
    def extract_modifications_safely(self, review_text: str) -> List[str]:
        """Example: Safely extract modifications with fallback."""

        # Simulate potential parsing failures
        import random
        if random.random() < 0.2:  # 20% chance of failure
            raise Exception("JSON decode error - invalid format")

        return ["modification1", "modification2"]

    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate validation report with error handling metrics."""

        return {
            "validation_status": "complete",
            "error_handling": self.error_handler.get_error_report()
        }

def main():
    """Test error handling and retry logic."""

    print("🔧 Testing Error Handling and Retry Logic")
    print("=" * 50)

    validator = ValidationErrorHandling()

    # Test API validation (simplified)
    print("Testing API validation...")
    try:
        result = validator.validate_recipe_with_api({"title": "Test Recipe"})
        print(f"  Validation result: {result['status']}")
    except Exception as e:
        print(f"  Validation failed: {e}")

    # Test safe operations
    print("Testing safe modification extraction...")
    result = validator.extract_modifications_safely("Test review text")
    print(f"  Extracted {len(result)} modifications")

    # Test error classification
    print("Testing error classification...")
    classifier = ErrorClassifier()
    test_errors = [
        Exception("Connection timeout"),
        Exception("Rate limit exceeded"),
        Exception("File not found"),
        Exception("JSON decode error")
    ]

    for error in test_errors:
        category = classifier.classify_error(error)
        print(f"  '{error}' -> {category.value}")

    print("\n✅ Error handling and retry logic implemented successfully!")

if __name__ == "__main__":
    main()