# Universal Entity Serializer - Replaces MasterPerson and MasterAsset Serializers

class MasterObjectSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    last_updated_by_name = serializers.CharField(source='last_updated_by.username', read_only=True)
    profiles_count = serializers.SerializerMethodField()
    field_values = serializers.SerializerMethodField()
    object_type_display = serializers.CharField(source='get_object_type_display', read_only=True)

    class Meta:
        model = MasterObject
        fields = [
            'id', 'object_type', 'object_type_display', 'display_name', 
            'created_at', 'updated_at', 'last_updated_by_name', 
            'profiles_count', 'field_values'
        ]

    def get_display_name(self, obj):
        """
        Get display name from FieldValue
        - For PERSON: use 'ho_ten'
        - For others: use 'so_giay_chung_nhan' or first available value
        """
        key = 'ho_ten' if obj.object_type == 'PERSON' else 'so_giay_chung_nhan'
        # Prioritize master data (loan_profile__isnull=True)
        fv = FieldValue.objects.filter(
            master_object=obj, 
            field__placeholder_key=key, 
            loan_profile__isnull=True
        ).first()
        
        if not fv:
            # Fallback to any value
            fv = FieldValue.objects.filter(
                master_object=obj, 
                field__placeholder_key=key
            ).order_by('-id').first()
        
        return fv.value if fv else f"{obj.get_object_type_display()} #{obj.id}"

    def get_profiles_count(self, obj):
        """Count how many profiles this object is linked to"""
        return obj.profile_links.count()

    def get_field_values(self, obj):
        """
        Return all master data field values for this object
        Only returns canonical data (loan_profile__isnull=True)
        """
        fvs = FieldValue.objects.filter(master_object=obj, loan_profile__isnull=True)
        return {fv.field.placeholder_key: fv.value for fv in fvs}


class LoanProfileObjectLinkSerializer(serializers.ModelSerializer):
    """Serializer for the junction table between LoanProfile and MasterObject"""
    object = MasterObjectSerializer(source='master_object', read_only=True)
    master_object_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = LoanProfileObjectLink
        fields = ['id', 'loan_profile', 'master_object_id', 'object', 'roles']
