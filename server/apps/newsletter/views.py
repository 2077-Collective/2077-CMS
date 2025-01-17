from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.shortcuts import render
from .models import Subscriber
import logging
from .tasks import sync_to_beehiiv_task

logger = logging.getLogger(__name__)

@csrf_exempt
def subscribe(request):
    """
    Handles POST requests to subscribe an email address.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Validate email
        if not email:
            return JsonResponse({'message': 'Email is required'}, status=400)
        
        try:
            # Create a new subscriber
            subscriber, created = Subscriber.objects.get_or_create(email=email, defaults={'is_active': True})
            
            if not created:
                # Handle case where email is already subscribed
                return JsonResponse({'message': 'Email already subscribed'}, status=200)
            
            # Enqueue the sync task with Beehiiv
            sync_to_beehiiv_task.delay(email)
            
            return JsonResponse({'message': 'Subscription successful'}, status=200)
        
        except IntegrityError:
            # Handle database integrity errors
            logger.error(f"IntegrityError while subscribing {email}")
            return JsonResponse({'message': 'An error occurred during subscription'}, status=500)
        
        except Exception as e:
            # Log the error and return a generic error message
            logger.error(f"Error during subscription: {str(e)}")
            return JsonResponse({'message': 'An error occurred during subscription'}, status=500)
    
    # If the request method is not POST, return a 405 Method Not Allowed response
    return JsonResponse({'message': 'Method not allowed'}, status=405)

def unsubscribe(request, email):
    """
    Handles unsubscribing an email address.
    """
    try:
        subscriber = Subscriber.objects.get(email=email)
        subscriber.is_active = False
        subscriber.save()
        return render(request, 'newsletter/unsubscribe_success.html', {'email': email})
    
    except Subscriber.DoesNotExist:
        return render(request, 'newsletter/unsubscribe_fail.html', {'email': None})