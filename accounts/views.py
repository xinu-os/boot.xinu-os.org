from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.views.generic import DetailView, RedirectView
from django.views.generic.edit import ProcessFormView, FormMixin

from shared.views import ProtectedMixin
from accounts.models import Profile
from accounts.forms import ProfileForm


class AccountsRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        pk = self.request.user.pk
        if pk is None:
            return reverse('accounts:login')
        else:
            return reverse('accounts:user-profile', kwargs={'pk': pk})


class AccountsProfileView(DetailView, ProcessFormView, FormMixin):
    model = User
    form_class = ProfileForm
    template_name = 'accounts/user_profile.html'

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        user = self.request.user
        profile = Profile.objects.get_profile(user=user)
        if self.request.POST:
            form = form_class(self.request.POST, instance=profile)
        else:
            form = form_class(instance=profile)
        return form

    def get_context_data(self, **kwargs):
        context = super(AccountsProfileView, self).get_context_data(**kwargs)
        # Only add form context if your own account
        if ProtectedMixin.is_my_account(self):
            context['form'] = self.get_form()
        return context

    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

    def get_success_url(self):
        pk = self.request.user.pk
        return reverse('accounts:user-profile', kwargs={'pk': pk})

    def post(self, request, *args, **kwargs):
        # Cannot modify other accounts
        if not ProtectedMixin.is_my_account(self):
            return redirect('accounts:profile')
        form = self.get_form()
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        else:
            self.object = form
            return self.form_invalid(form)

