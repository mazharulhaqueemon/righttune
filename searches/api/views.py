from django.db.models import Q
from rest_framework.generics import (
    ListAPIView
    )
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    )
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from profiles.models import Profile 
from .serializers import SearchSerializer

class SearchListApiView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        method_dict = request.GET
        query = method_dict.get('q',None)

        profiles_objs = []

        if query is not None:
            lookups = Q(full_name__icontains=query)
            profiles_objs = Profile.objects.filter(lookups).exclude(user=request.user).distinct()

        serializer_profiles = SearchSerializer(instance=profiles_objs,many=True,context={"request": request})
        return Response({'profiles':serializer_profiles.data})
        

