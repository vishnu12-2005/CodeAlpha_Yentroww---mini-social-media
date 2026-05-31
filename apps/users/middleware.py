from django.shortcuts import redirect

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_paths = ['/', '/auth/login/', '/auth/register/']
        
        # Bypass for static, media, and admin routes
        if request.path.startswith('/static/') or request.path.startswith('/media/') or request.path.startswith('/admin/'):
            return self.get_response(request)

        if not request.user.is_authenticated and request.path not in allowed_paths:
            return redirect('/')
            
        return self.get_response(request)
