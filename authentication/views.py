from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .serializer import UserSerializer, ChangePasswordSerializer

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
    #si el serializer no devuelve un error

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username = request.data['username'])
    #se rpegunta si existe el usuario
    if not user.check_password(request.data['password']):
        return Response({'Error': "Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST)
        #Se pregunta si la contrasaña esta correcta y si no es asi se manda error

    serializer = UserSerializer(instance = User)
    #Se crea un instancia del serializer
    token, created = Token.objects.get_or_create(user = user)
    #se obtienen el token del usuario

    return Response({'user': serializer.data, 'token': token.key}, status= status.HTTP_200_OK)
    #se devuelve el token del usuario y los datos del usuario

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes({IsAuthenticated})
#se pide el token de autorizacion y si el usuario esta autenticado
def log(request):
    print(request.user.password)
    return Response({'nice':'Perfecto'}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update(request):
    user = request.user
    serializer = UserSerializer(user, data = request.data, partial = True)
    #se serializa el los datos en un json
    if serializer.is_valid():
        #se regunta si el usuario es valido y si es valido se guarda en la base de datos
        serializer.save()
        return Response({'User': serializer.data}, status= status.HTTP_200_OK)

    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete(request):

    user = request.user
    #se obtiene el nombre de usuario del user
    try:
        user = User.objects.get(username = user.username)
        #si el usuario existe los datos se guardan el la variable
    except User.DoesNotExist:
        return Response({"Error": 'User dont exist'}, status= status.HTTP_404_NOT_FOUND)
        #si no existe el personaje devuelve un error

    user.delete()
    #si existe se elimina el usuario
    return Response({'success':'success'}, status = status.HTTP_200_OK)
    #y se devuelve el exito


@api_view(["GET"])
def validate_user(request):
    try:
        key = request.data.get("token")
        key = Token.objects.get(key = key)

        return Response({"reponse": key.user_id}, status= status.HTTP_200_OK)
    except:
        return Response({"reponse": "not valid"}, status= status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def validate_staff(request):
    try:
        key = request.data.get("token") or request.data.get("Token") 
        key = Token.objects.get(key = key)
        user = User.objects.get(id = key.user_id)
        if user.is_staff:
            return Response({"reponse": key.user_id}, status= status.HTTP_200_OK)
        return Response({"response": "not valid"}, status = status.HTTP_400_BAD_REQUEST)
    except Token.DoesNotExist:
        return Response({"Error": "it's not staff"}, status = status.HTTP_404_NOT_FOUND)
    except:
        return Response({"response": "not valid"}, status = status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def make_staff(request):
    user = request.user
    try:
        user = User.objects.get(username = user.username)
        user.is_staff = True
    except User.DoesNotExist:
        return Response({"Error": 'User dont exist'}, status= status.HTTP_404_NOT_FOUND)

    user.save()
    return Response({'success':'success'}, status = status.HTTP_200_OK)


@api_view(["PATCH"])
@authentication_classes([TokenAuthentication])
@permission_classes({IsAuthenticated})
def change_password(request):
    user_id = request.user.id 
    serializer = ChangePasswordSerializer(data = request.data)
    try:
        user = User.objects.get(id = user_id)
        if serializer.is_valid():
            user.set_password(serializer.data["password"]) 
            user.save()

            return Response({"Check": "Password changed"}, status= status.HTTP_200_OK) 
        else:
            return Response({"Error": serializer.errors}, status= status.HTTP_400_BAD_REQUEST) 
    except User.DoesNotExist:
        return Response({"Error": 'User dont exist'}, status= status.HTTP_404_NOT_FOUND)
        