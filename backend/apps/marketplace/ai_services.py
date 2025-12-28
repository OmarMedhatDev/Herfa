"""
AI Services for Herfa Marketplace
- Price Estimation
- ID Verification (quality check)
- Chat Safety Monitoring
"""
import re
import cv2
import numpy as np
from typing import Dict, Tuple, Optional
from decimal import Decimal


class PriceEstimationService:
    """AI service for estimating service prices"""
    
    # Base prices in EGP for different categories
    BASE_PRICES = {
        'Plumbing': {'min': 100, 'max': 500},
        'Carpentry': {'min': 150, 'max': 800},
        'Electrical': {'min': 120, 'max': 600},
        'Painting': {'min': 80, 'max': 400},
        'Cleaning': {'min': 50, 'max': 200},
        'HVAC': {'min': 200, 'max': 1000},
        'General': {'min': 100, 'max': 500},
    }
    
    # Keywords that indicate complexity
    COMPLEXITY_KEYWORDS = {
        'urgent': 1.3,
        'emergency': 1.5,
        'complex': 1.4,
        'simple': 0.8,
        'quick': 0.7,
        'small': 0.7,
        'large': 1.3,
        'multiple': 1.2,
    }
    
    @classmethod
    def estimate_price(cls, category: str, description: str) -> str:
        """
        Estimate price range based on category and description
        Returns price range string like "150-200 EGP"
        """
        if category not in cls.BASE_PRICES:
            category = 'General'
        
        base_min = cls.BASE_PRICES[category]['min']
        base_max = cls.BASE_PRICES[category]['max']
        
        # Analyze description for complexity
        description_lower = description.lower()
        complexity_multiplier = 1.0
        
        for keyword, multiplier in cls.COMPLEXITY_KEYWORDS.items():
            if keyword in description_lower:
                complexity_multiplier *= multiplier
        
        # Calculate adjusted prices
        estimated_min = int(base_min * complexity_multiplier)
        estimated_max = int(base_max * complexity_multiplier)
        
        # Ensure min < max
        if estimated_min >= estimated_max:
            estimated_max = estimated_min + 50
        
        return f"{estimated_min}-{estimated_max} EGP"


class IDVerificationService:
    """AI service for National ID photo quality verification"""
    
    @classmethod
    def check_image_quality(cls, image_path: str) -> Tuple[bool, float, str]:
        """
        Check ID photo quality using OpenCV
        Returns: (is_valid, confidence_score, error_message)
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return False, 0.0, "Invalid image file"
            
            # Convert to grayscale for processing
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 1. Blur detection using Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 100:  # Threshold for blur detection
                return False, 0.0, "Image is too blurry. Please retake the photo."
            
            # 2. Face detection (basic check - ID should have a face)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                return False, 0.3, "No face detected. Please ensure the ID photo shows a clear face."
            
            # 3. Image dimensions check (should be reasonable size)
            height, width = gray.shape
            if height < 200 or width < 200:
                return False, 0.4, "Image resolution too low. Please use a higher quality photo."
            
            # 4. Brightness check
            mean_brightness = np.mean(gray)
            if mean_brightness < 50 or mean_brightness > 200:
                return False, 0.5, "Image brightness is not optimal. Please retake in better lighting."
            
            # Calculate confidence score
            confidence = min(1.0, (
                (laplacian_var / 500) * 0.4 +  # Blur score (40%)
                (len(faces) / 2) * 0.3 +  # Face detection (30%)
                (min(height, width) / 500) * 0.2 +  # Resolution (20%)
                (1 - abs(mean_brightness - 128) / 128) * 0.1  # Brightness (10%)
            ))
            
            return True, confidence, "Image quality is acceptable"
            
        except Exception as e:
            return False, 0.0, f"Error processing image: {str(e)}"
    
    @classmethod
    def extract_text_ocr(cls, image_path: str) -> Optional[str]:
        """
        Extract text from ID using OCR (simplified version)
        For production, use libraries like pytesseract or cloud OCR services
        """
        # Placeholder for OCR functionality
        # In production, integrate with pytesseract or cloud OCR API
        return None


class ChatSafetyService:
    """AI service for monitoring chat messages for safety violations"""
    
    # Keywords that indicate attempts to move payment outside the platform
    UNSAFE_KEYWORDS = [
        r'010\d{8}',  # Egyptian phone numbers
        r'01\d{9}',   # Alternative phone format
        r'cash',
        r'outside',
        r'off.*platform',
        r'direct.*payment',
        r'bank.*transfer',
        r'vodafone.*cash',
        r'orange.*money',
        r'etisalat.*cash',
    ]
    
    # Warning patterns
    WARNING_PATTERNS = [
        r'contact.*me.*directly',
        r'call.*me',
        r'whatsapp',
        r'telegram',
    ]
    
    @classmethod
    def check_message_safety(cls, message: str) -> Tuple[bool, Optional[str]]:
        """
        Check if message contains unsafe patterns
        Returns: (is_safe, flag_reason)
        """
        message_lower = message.lower()
        
        # Check for unsafe keywords
        for pattern in cls.UNSAFE_KEYWORDS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return False, "Message contains patterns suggesting off-platform payment. Please keep all transactions within the app for your safety."
        
        # Check for warning patterns
        for pattern in cls.WARNING_PATTERNS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return True, "Warning: Please keep all communications and payments within the platform for your protection."
        
        return True, None

