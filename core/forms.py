from django import forms

from .models import Category


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories."""

    class Meta:
        model = Category
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Category name"}
            ),
        }


class TripForm(forms.Form):
    """Form for creating trips with category selection."""

    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Trip name (e.g., 'Japan 2025')",
            }
        ),
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=False,
        help_text="Select the categories to include in this trip's packing list.",
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["categories"].queryset = Category.objects.filter(user=user)
