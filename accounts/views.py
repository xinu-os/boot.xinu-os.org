from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic import DetailView, RedirectView

from accounts.models import Profile
from accounts.forms import ProfileForm


class AccountsRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        pk = self.request.user.pk
        print 'redirecting to ', pk
        if pk is None:
            return reverse('accounts:login')
        else:
            return reverse('accounts:user-profile', kwargs={'pk': pk})


class AccountsProfileView(DetailView):
    model = User
    form_class = ProfileForm
    template_name = 'accounts/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super(AccountsProfileView, self).get_context_data(**kwargs)
        user = self.request.user
        if hasattr(self.request, 'form_instance'):
            context['form'] = self.request.form_instance
        elif user.pk == int(self.kwargs['pk']):
            profile, _ = Profile.objects.get_or_create(user=user)
            context['form'] = self.form_class(instance=profile)
        return context

    def post(self, request, *args, **kwargs):
        if self.request.user.pk != int(self.kwargs['pk']):
            return reverse('accounts:user-profile', kwargs=self.kwargs)
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        form = self.form_class(request.POST, instance=profile)
        if form.is_valid():
            form.save()
        else:
            self.request.form_instance = form
        return super(AccountsProfileView, self).get(request, *args, **kwargs)
