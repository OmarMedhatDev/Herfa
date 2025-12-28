"""
Celery tasks for async processing
"""
from celery import shared_task
from django.core.files.storage import default_storage
from apps.users.models import ArtisanProfile
from .ai_services import IDVerificationService


@shared_task
def process_id_verification(profile_id):
    """
    Process National ID verification asynchronously
    """
    try:
        profile = ArtisanProfile.objects.get(id=profile_id)
        
        if not profile.national_id_photo:
            return {'status': 'error', 'message': 'No ID photo found'}
        
        # Get image path
        image_path = profile.national_id_photo.path
        
        # Check image quality
        is_valid, confidence_score, error_message = IDVerificationService.check_image_quality(image_path)
        
        if is_valid:
            # Update profile status to pending review
            profile.verification_status = 'PENDING_REVIEW'
            profile.id_confidence_score = confidence_score
            profile.save()
            return {
                'status': 'success',
                'message': 'ID photo quality check passed. Awaiting admin approval.',
                'confidence_score': confidence_score
            }
        else:
            # Auto-reject poor quality images
            profile.verification_status = 'REJECTED'
            profile.rejection_reason = error_message
            profile.id_confidence_score = confidence_score
            profile.save()
            return {
                'status': 'rejected',
                'message': error_message,
                'confidence_score': confidence_score
            }
    
    except ArtisanProfile.DoesNotExist:
        return {'status': 'error', 'message': 'Profile not found'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

