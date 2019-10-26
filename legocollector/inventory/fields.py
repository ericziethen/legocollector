from django.forms import ModelChoiceField


class PartColorChoiceField(ModelChoiceField):
    # inspired by https://stackoverflow.com/questions/5089396/django-form-field-choices-adding-an-attribute

    # custom method to label the option field
    def label_from_instance(self, obj):
        # since the object is accessible here you can set the extra attributes
        if hasattr(obj, 'rgb'):
            self.widget.custom_attrs.update({obj.pk: {'rgb': obj.rgb}})
            self.widget.custom_attrs.update(
                {obj.pk: {'style': F'background-color:#{obj.rgb}; color:#{obj.complimentary_color}'}})

        return obj.name
