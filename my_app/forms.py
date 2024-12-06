from django import forms
from  auth_1.models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_names','profile_picture' ,'bio',]
        
        
    def save(self, commit=True):
              
        profile = super().save(commit=False)
        
        if hasattr(self, 'user'):
            profile.user = self.user
        # Ensure user is set to the logged-in user
        if commit:
            profile.save()
        return profile


full_names = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Full Names'}))
bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something about yourself'}))
profile_picture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))