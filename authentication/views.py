from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication 
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404 

from .serializer import UserSerializer

# Create your views here.
@api_view(['POST'])
def register(request): 
    serializer = UserSerializer(data = request.data) 
    #s convierte la data dada por el servidor en un json
    if serializer.is_valid():
        #se pregunta si el serializador es valido
        serializer.save()
        #si es valido se guarda

        user = User.objects.get(username=serializer.data['username'])
        #Se crea un objeto tipo "usuario"
        user.email = serializer.data['email']
        #dentroi del onjeto se añade el email
        user.set_password(serializer.data['password'])
        #ahora se setea la contraeña utilkizando la funcion set password
        user.save()
        #y por ultimo se guardia el usuario
        token = Token.objects.create(user= user)
        #ahora se crea un token en la base de datos que esta relacionado con el usuario recien creado
        return Response({'token': token.key, 'user': serializer.data}, status= status.HTTP_201_CREATED)
        #se debuelve tanto el la key del token como los datos del usuario y por ultimo el status creado

    return Response({'error':serializer.errors}, status= status.HTTP_400_BAD_REQUEST)
    #si el serializer no es valido da esto 
    
@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username = request.data(['username']))

    if not user.check_password(request.data(['password'])):
        return Response({'Error': "Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(instance = User)
    token, created = Token.objects.get_or_create(user = user)

    return Response({'user': serializer.data, 'token': token.ket}, status= status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes({IsAuthenticated})
def log(request):
    print("request.user")
    return Response({'nice':'Perfecto'}, status=status.HTTP_200_OK)
