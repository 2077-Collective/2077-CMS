from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.shortcuts import render
from .models import Subscriber
from .services import BeehiivService

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
            subscriber = Subscriber.objects.create(email=email, is_active=True)
            
            # Sync with Beehiiv
            beehiiv = BeehiivService()
            beehiiv.create_subscriber(email, is_active=True)
            
            return JsonResponse({'message': 'Subscription successful'}, status=200)
        
        except IntegrityError:
            # Handle case where email is already subscribed
            return JsonResponse({'message': 'Email already subscribed'}, status=400)
        
        except ValueError as e:
            # Handle Beehiiv "invalid" status
            return JsonResponse({'message': str(e)}, status=200)  # Return 200 with a warning message
        
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